#!/bin/bash
# ==============================================================
# FoundationPoseROS2 完整环境重建脚本 (RTX 5090 Ti / sm_120)
# 用法: bash setup_env.sh
# ==============================================================
set -e

# ---------- 配置 ----------
CONDA_ENV=foundationpose_ros
PYTHON_VERSION=3.10
PROJ_ROOT="$(cd "$(dirname "$0")" && pwd)"
CONDA_BASE="$(conda info --base 2>/dev/null || echo "/home/jinwz/miniconda3")"

# ---------- 1. 创建 conda 环境 ----------
echo ">>> Creating conda environment: $CONDA_ENV"
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda create -y -n $CONDA_ENV python=$PYTHON_VERSION
conda activate $CONDA_ENV

# ---------- 2. 安装 PyTorch 2.7.0+cu128（必须，包含 sm_120 内核） ----------
echo ">>> Installing PyTorch 2.7.0+cu128"
pip install torch==2.7.0+cu128 torchvision==0.22.0+cu128 \
  --index-url https://download.pytorch.org/whl/cu128 \
  --default-timeout=300

# ---------- 3. 安装 pyTorch3D（CPU-only，避免 sm_120 编译问题） ----------
echo ">>> Installing pytorch3d (CPU-only)"
PYTORCH3D_FORCE_NO_CUDA=1 pip install --no-build-isolation \
  "git+https://github.com/facebookresearch/pytorch3d.git@stable"

# ---------- 4. 安装其他 pip 依赖 ----------
echo ">>> Installing Python dependencies"
pip install --no-build-isolation \
  numpy==1.26.4 \
  scipy \
  opencv-python-headless \
  trimesh \
  pyopengl \
  ultralytics[sam] \
  nvidia-ml-py3 \
  warp-lang \
  imageio

# ---------- 5. 克隆 FoundationPose（如未拉取子模块） ----------
if [ ! -d "$PROJ_ROOT/FoundationPose" ]; then
  echo ">>> Please clone FoundationPose first:"
  echo "    git clone https://github.com/NVlabs/FoundationPose.git"
  exit 1
fi

# ---------- 6. 编译 nvdiffrast（关键：含 PTX 供 sm_120 JIT 编译） ----------
echo ">>> Building nvdiffrast with PTX (9.0+PTX for sm_120 JIT)"
cd "$PROJ_ROOT/FoundationPose/nvdiffrast"
PYTHONNOUSERSITE=1 TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;9.0+PTX" \
  pip install --no-build-isolation -e .

# ---------- 7. 编译 mycpp/mycuda 扩展 ----------
echo ">>> Building mycpp extension"
cd "$PROJ_ROOT/FoundationPose/mycpp"
python setup.py build_ext --inplace

echo ">>> Building mycuda extension"
# C++17 兼容性修正已应用于 bundlesdf/mycuda/setup.py
cd "$PROJ_ROOT/FoundationPose/bundlesdf/mycuda"
python setup.py build_ext --inplace

# ---------- 8. 验证 ----------
echo ">>> Verifying installation"
cd "$PROJ_ROOT"
PYTHONNOUSERSITE=1 python -c "
import sys
sys.path.insert(0, './FoundationPose/nvdiffrast')
sys.path.insert(0, './FoundationPose')
from Utils import *
from estimater import *
import nvdiffrast.torch as dr
ctx = dr.RasterizeCudaContext()
import torch
print('torch:', torch.__version__)
print('CUDA:', torch.cuda.is_available())
print('Device:', torch.cuda.get_device_name(0))
print('sm_120 support:', 'sm_120' in torch.cuda.get_arch_list())
print('=== SETUP COMPLETE ===')
"

echo ""
echo "Done! Run with:"
echo "  source /opt/ros/humble/setup.bash"
echo "  conda activate $CONDA_ENV"
echo "  PYTHONNOUSERSITE=1 python foundationpose_ros_multi.py"
