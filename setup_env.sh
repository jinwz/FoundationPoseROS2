#!/bin/bash
# ==============================================================
# FoundationPoseROS2 一键环境重建脚本
# 用法: bash setup_env.sh
# 说明: 在 git clone && git lfs pull 之后运行
# ==============================================================
set -e

CONDA_ENV=foundationpose_ros
PYTHON_VERSION=3.10
PROJ_ROOT="$(cd "$(dirname "$0")" && pwd)"

# ---------- 1. 创建 conda 环境 ----------
echo ">>> [1/6] Creating conda environment: $CONDA_ENV"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda create -y -n $CONDA_ENV python=$PYTHON_VERSION
conda activate $CONDA_ENV

# ---------- 2. PyTorch 2.7.0+cu128（必须，含 sm_120 内核） ----------
echo ">>> [2/6] Installing PyTorch 2.7.0+cu128"
pip install torch==2.7.0+cu128 torchvision==0.22.0+cu128 \
  --index-url https://download.pytorch.org/whl/cu128 \
  --default-timeout=300

# ---------- 3. pyTorch3D（CPU-only，避免 sm_120 编译问题） ----------
echo ">>> [3/6] Installing pytorch3d (CPU-only)"
PYTORCH3D_FORCE_NO_CUDA=1 pip install --no-build-isolation \
  "git+https://github.com/facebookresearch/pytorch3d.git@stable"

# ---------- 4. 通用 Python 依赖 ----------
echo ">>> [4/6] Installing Python dependencies"
pip install --no-build-isolation \
  numpy==1.26.4 \
  scipy \
  opencv-python-headless \
  trimesh \
  pyopengl \
  ultralytics \
  nvidia-ml-py3 \
  warp-lang \
  imageio \
  scikit-image

# ---------- 5. 编译 C++/CUDA 扩展 ----------
echo ">>> [5/6] Building custom extensions"

# 5a. nvdiffrast（含 PTX 供 sm_120 运行时 JIT 编译）
cd "$PROJ_ROOT/FoundationPose/nvdiffrast"
PYTHONNOUSERSITE=1 TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;9.0+PTX" \
  pip install --no-build-isolation -e .

# 5b. mycpp
cd "$PROJ_ROOT/FoundationPose/mycpp"
python setup.py build_ext --inplace

# 5c. mycuda（C++17 兼容性修正已应用于 bundlesdf/mycuda/setup.py）
cd "$PROJ_ROOT/FoundationPose/bundlesdf/mycuda"
python setup.py build_ext --inplace

# ---------- 6. 验证 ----------
echo ">>> [6/6] Verifying installation"
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
echo "============================================"
echo " Setup complete! Run with:"
echo "   source /opt/ros/humble/setup.bash"
echo "   conda activate $CONDA_ENV"
echo "   PYTHONNOUSERSITE=1 bash run_foundationpose.sh"
echo "============================================"
