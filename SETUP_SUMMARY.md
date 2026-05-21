# FoundationPoseROS2 环境搭建总结

**GPU:** RTX 5090 Ti (sm_120 Blackwell) · 16GB · Driver 595.58 (CUDA 13.2)
**OS:** Ubuntu 22.04 · ROS2 Humble
**Python:** 3.10 (conda: foundationpose_ros)

---

## 环境关键点

### PyTorch 版本选择
- RTX 5090 Ti (sm_120) 需要 **PyTorch 2.7.0+cu128**
- 只有 cu128 的预编译 wheel 包含 sm_120 内核
- 安装：`pip install torch==2.7.0+cu128 torchvision==0.22.0+cu128 --index-url https://download.pytorch.org/whl/cu128`

### nvdiffrast 编译（关键）
- conda 环境中 nvcc 是 CUDA 12.1，**不支持 sm_120 编译**
- 解决方案：编译时指定 `TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;9.0+PTX"`
- 生成 compute_90 的 PTX，运行时由 CUDA 13.2 驱动 **JIT 编译为 sm_120** 执行

### pytorch3d
- 与 PyTorch 2.7 不兼容，需要重新编译
- 编译时 CUDA 12.1 nvcc 不支持 sm_120 → 使用 `PYTORCH3D_FORCE_NO_CUDA=1` 编译 CPU-only 版本
- FoundationPose 对 pytorch3d 的 CUDA 运算依赖不大，CPU 版本够用

### 关键环境变量
- `PYTHONNOUSERSITE=1` — **必须**，否则 `~/.local/lib/python3.10/site-packages` 会覆盖 conda 包

---

## 运行指南

### 1. 启动 RealSense 相机
```bash
source /opt/ros/humble/setup.bash
source /home/jinwz/miniconda3/bin/activate foundationpose_ros
PYTHONNOUSERSITE=1 ros2 launch /opt/ros/humble/share/realsense2_camera/launch/rs_launch.py align_depth.enable:=true
```

### 2. 启动 FoundationPose
```bash
source /opt/ros/humble/setup.bash
source /home/jinwz/miniconda3/bin/activate foundationpose_ros
PYTHONNOUSERSITE=1 bash run_foundationpose.sh
```

### 3. 交互流程
1. **Tkinter 文件选择窗口** — 列出 `demo_data/` 下所有 .obj，用 Move Up/Down 排序，点 Done
2. **SAM2 自动分割** — 显示第一帧图像中所有物体的绿色轮廓
3. **鼠标点击选中** — 点击物体 → 与队列中的 mesh 对应
4. **确认跟踪** — 按 `c` / Enter / Space → 开始 6D 位姿跟踪
5. **快捷键**：`s`=跳过当前 mesh，`r`=重新 SAM2 分割，`q`=退出

### 4. 启动参数
```bash
python foundationpose_ros_multi.py --est_refine_iter 8 --track_refine_iter 6
```
- `--est_refine_iter`：首次注册迭代次数（默认4，增大可提高精度）
- `--track_refine_iter`：逐帧跟踪迭代次数（默认2）

### 5. 运行时添加物体
```bash
ros2 topic pub /add_mesh std_msgs/msg/String "data: '/path/to/model.obj'" --once
```
（仅在第一帧 SAM2 对话框出现期间有效）

### 6. 查看结果
| 方式 | 命令 |
|------|------|
| OpenCV 窗口 | 程序自动弹出 |
| RViz2 | `rviz2` → Add Marker → `/Current_OBJ_position_1_mesh` |
| 话题 | `ros2 topic echo /Current_OBJ_position_1` |

---

## 文件结构

```
FoundationPoseROS2/
├── foundationpose_ros_multi.py    # ROS2 主节点
├── run_foundationpose.sh          # 启动脚本
├── setup_env.sh                   # 环境重建脚本
├── environment.yaml               # conda 包列表
├── requirements_freeze.txt        # pip 精确版本
├── cam_2_base_transform.py        # 相机→基座坐标系变换
├── .gitignore                     # Git 忽略规则
├── .gitattributes                 # Git LFS 配置
├── demo_data/                     # 测试用 .obj 文件
│   ├── cube/
│   ├── drill/
│   ├── mustard0/
│   └── soup_can/
└── FoundationPose/                # NVIDIA FoundationPose 源码
    ├── estimater.py               # FoundationPose 类定义
    ├── Utils.py                   # 工具函数
    ├── nvdiffrast/                # 光栅化引擎
    ├── mycpp/                     # C++ 扩展
    ├── bundlesdf/mycuda/          # CUDA 扩展
    ├── weights/                   # 预训练权重 (Git LFS)
    ├── eigen-3.4.0/               # C++ 矩阵库
    └── pybind11/                  # C++ Python 绑定
```

## 重装后恢复
```bash
git clone https://github.com/jinwz/FoundationPoseROS2.git
cd FoundationPoseROS2
git lfs pull
bash setup_env.sh
```
