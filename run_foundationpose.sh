#!/bin/bash
# Wrapper script for FoundationPoseROS2
# Sets up all necessary environment variables

CONDA_ENV=foundationpose_ros
PROJ_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || \
    source "/home/jinwz/miniconda3/etc/profile.d/conda.sh"
conda activate $CONDA_ENV

# Critical: ignore ~/.local site-packages to avoid version conflicts
export PYTHONNOUSERSITE=1

# Point CUDA to the conda env's toolkit (CUDA 12.1, matches torch build)
export CUDA_HOME="$CONDA_PREFIX"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$CONDA_PREFIX/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH"

# Source ROS2 (if available)
if [ -f /opt/ros/humble/setup.bash ]; then
    source /opt/ros/humble/setup.bash
elif [ -f /opt/ros/foxy/setup.bash ]; then
    source /opt/ros/foxy/setup.bash
fi

cd "$PROJ_ROOT"

# Run the main script
exec python foundationpose_ros_multi.py "$@"
