import sys
sys.path.append('./FoundationPose')
sys.path.append('./FoundationPose/nvdiffrast')

import rclpy
from rclpy.node import Node
from estimater import *
import cv2
import numpy as np
import trimesh
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge
import argparse
import os
from scipy.spatial.transform import Rotation as R
from ultralytics import SAM
from std_msgs.msg import String
from visualization_msgs.msg import Marker

# ---------- FoundationPose monkey-patches ----------
original_init = FoundationPose.__init__
original_register = FoundationPose.register

def modified_init(self, model_pts, model_normals, symmetry_tfs=None, mesh=None, scorer=None, refiner=None, glctx=None, debug=0, debug_dir='./FoundationPose'):
    original_init(self, model_pts, model_normals, symmetry_tfs, mesh, scorer, refiner, glctx, debug, debug_dir)
    self.is_register = False

def modified_register(self, K, rgb, depth, ob_mask, iteration):
    pose = original_register(self, K, rgb, depth, ob_mask, iteration)
    self.is_register = True
    return pose

FoundationPose.__init__ = modified_init
FoundationPose.register = modified_register
# ---------- end monkey-patches ----------


class AutoPoseNode(Node):
    def __init__(self, est_iter=4, track_iter=2):
        super().__init__('foundationpose_auto')
        self.est_iter = est_iter
        self.track_iter = track_iter

        self.bridge = CvBridge()
        self.color_image = None
        self.depth_image = None
        self.cam_K = None

        # Subscribers
        self.create_subscription(Image, '/camera/camera/color/image_raw', self.image_cb, 10)
        self.create_subscription(Image, '/camera/camera/aligned_depth_to_color/image_raw', self.depth_cb, 10)
        self.create_subscription(CameraInfo, '/camera/camera/color/camera_info', self.info_cb, 10)
        self.create_subscription(String, '/add_mesh', self.add_mesh_cb, 10)

        # FoundationPose models
        self.scorer = ScorePredictor()
        self.refiner = PoseRefinePredictor()
        self.glctx = dr.RasterizeCudaContext()

        # SAM2 model
        self.seg_model = SAM("sam2.1_b.pt")

        # State — only one object at a time
        self.current_object = None   # {est, to_origin, bbox, path} or None
        self.pending_mesh = None     # single mesh path awaiting initialization

        # Publishers (created on demand)
        self.pose_pub = None
        self.marker_pub = None
        self._pose_logged = False

        self.get_logger().info("AutoPoseNode ready. Publish .obj path to /add_mesh to start tracking.")

    # ---------- callbacks ----------

    def info_cb(self, msg):
        if self.cam_K is None:
            self.cam_K = np.array(msg.k).reshape((3, 3))
            self.get_logger().info(f"Camera intrinsics: {self.cam_K}")

    def image_cb(self, msg):
        self.color_image = self.bridge.imgmsg_to_cv2(msg, "rgb8")

    def depth_cb(self, msg):
        self.depth_image = self.bridge.imgmsg_to_cv2(msg, "32FC1") / 1e3
        self.process()

    def add_mesh_cb(self, msg):
        path = msg.data
        if not os.path.exists(path):
            self.get_logger().error(f"File not found: {path}")
            return
        if self.current_object and self.current_object['path'] == path:
            self.get_logger().info(f"Already tracking this mesh: {path}")
            return

        # Replace previous tracked object
        if self.current_object:
            self.get_logger().info(f"Replacing previous object with: {path}")
            self.current_object = None

        self._pose_logged = False
        self.pending_mesh = path
        self.get_logger().info(f"Mesh queued for auto-init: {path}")

    # ---------- initialization ----------

    def init_object(self, path, color, depth):
        """Load mesh, try each SAM2 mask, pick the highest-scoring register()."""
        self.get_logger().info(f"Initializing object from: {path}")

        mesh = trimesh.load(path)

        # Normalise mesh units to metres (RealSense depth is in metres).
        # Heuristic: if the largest dimension > 10, assume mm and scale to m.
        extents = mesh.extents
        if extents.max() > 10:
            self.get_logger().info(f"Mesh extents {extents} appear in mm, scaling to metres")
            mesh.vertices *= 0.001

        _, extents = trimesh.bounds.oriented_bounds(mesh)
        bbox = np.stack([-extents/2, extents/2], axis=0).reshape(2, 3)

        H, W = color.shape[:2]
        total_px = H * W

        # SAM2 auto-segmentation
        res = self.seg_model.predict(color)[0]
        if not res:
            self.get_logger().warn("SAM2 found no objects, retrying on next frame")
            return False

        masks = []
        for r in res:
            for c in r:
                m = np.zeros((H, W), np.uint8)
                contour = c.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2)
                cv2.drawContours(m, [contour], -1, 255, cv2.FILLED)
                masks.append(m)

        if not masks:
            self.get_logger().warn("No valid masks extracted, retrying")
            return False

        # Filter: skip obviously-wrong masks (too small = noise, too large = background)
        sizes = np.array([m.sum() for m in masks], dtype=np.int32)
        valid = [(s > 0.001 * total_px) & (s < 0.85 * total_px) for s in sizes]
        candidates = [(masks[i], sizes[i]) for i, v in enumerate(valid) if v]
        self.get_logger().info(
            f"SAM2: {len(masks)} objects total, "
            f"{len(candidates)} after size filter"
        )

        if not candidates:
            self.get_logger().warn("All masks filtered out (too small or too large)")
            return False

        # Try register() on each candidate mask, keep the best-scoring one
        best_est = None
        best_score = -1e9
        best_idx = -1

        for idx, (mask, area) in enumerate(candidates):
            self.get_logger().info(f"  Register attempt {idx+1}/{len(candidates)} (area={area} px)...")
            est = FoundationPose(
                model_pts=mesh.vertices,
                model_normals=mesh.vertex_normals,
                mesh=mesh,
                scorer=self.scorer,
                refiner=self.refiner,
                glctx=self.glctx,
            )
            est.register(
                K=self.cam_K, rgb=color, depth=depth,
                ob_mask=mask, iteration=self.est_iter,
            )
            score = float(est.scores[0].item() if hasattr(est.scores[0], 'item') else est.scores[0])
            self.get_logger().info(f"    score={score:.6f}")
            if score > best_score:
                best_score = score
                best_est = est
                best_idx = idx

        if best_est is None:
            self.get_logger().error("No valid registration found — no pose will be published")
            self.pending_mesh = None
            return False

        self.get_logger().info(f"Best mask #{best_idx+1} (score={best_score:.6f})")
        self.current_object = {
            'est': best_est,
            'bbox': bbox,
            'path': path,
        }
        self.pending_mesh = None
        self.get_logger().info(f"Now tracking: {path}")
        return True

    # ---------- main loop ----------

    def process(self):
        if self.color_image is None or self.depth_image is None or self.cam_K is None:
            return

        H, W = self.color_image.shape[:2]
        color = cv2.resize(self.color_image, (W, H), interpolation=cv2.INTER_NEAREST)
        depth = cv2.resize(self.depth_image, (W, H), interpolation=cv2.INTER_NEAREST)
        depth[(depth < 0.1) | (depth >= np.inf)] = 0

        # Initialize pending mesh (if any)
        if self.pending_mesh is not None:
            self.init_object(self.pending_mesh, color, depth)

        # Track current object
        if self.current_object is not None and self.current_object['est'].is_register:
            est = self.current_object['est']
            pose = est.track_one(rgb=color, depth=depth, K=self.cam_K, iteration=self.track_iter)
            if not self._pose_logged:
                t = pose[:3, 3]
                self.get_logger().info(f"FIRST frame pose t=({t[0]:.6f}, {t[1]:.6f}, {t[2]:.6f})")
                self._pose_logged = True
            self.publish_pose(pose)

    # ---------- output ----------

    def publish_pose(self, center):
        pos = center[:3, 3]
        rot = center[:3, :3]
        quat = R.from_matrix(rot).as_quat()

        topic = "/Current_OBJ_position"

        if self.pose_pub is None:
            self.pose_pub = self.create_publisher(PoseStamped, topic, 10)

        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_color_optical_frame"
        msg.pose.position.x = float(pos[0])
        msg.pose.position.y = float(pos[1])
        msg.pose.position.z = float(pos[2])
        msg.pose.orientation.w = float(quat[3])
        msg.pose.orientation.x = float(quat[0])
        msg.pose.orientation.y = float(quat[1])
        msg.pose.orientation.z = float(quat[2])
        self.pose_pub.publish(msg)

        # Marker (semi-transparent bounding box)
        marker_topic = f"{topic}_mesh"
        if self.marker_pub is None:
            self.marker_pub = self.create_publisher(Marker, marker_topic, 10)

        bbox = self.current_object['bbox']
        marker = Marker()
        marker.header = msg.header
        marker.ns = topic
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.position = msg.pose.position
        marker.pose.orientation = msg.pose.orientation
        marker.scale.x = float(bbox[1, 0] - bbox[0, 0])
        marker.scale.y = float(bbox[1, 1] - bbox[0, 1])
        marker.scale.z = float(bbox[1, 2] - bbox[0, 2])
        marker.color.a = 0.4
        marker.color.r = 0.2
        marker.color.g = 0.6
        marker.color.b = 1.0
        self.marker_pub.publish(marker)


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--est_refine_iter', type=int, default=4)
    parser.add_argument('--track_refine_iter', type=int, default=2)
    parsed = parser.parse_args()

    rclpy.init()
    node = AutoPoseNode(est_iter=parsed.est_refine_iter, track_iter=parsed.track_refine_iter)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
