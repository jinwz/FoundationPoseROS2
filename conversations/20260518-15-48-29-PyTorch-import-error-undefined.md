# Session: PyTorch import error: undefined symbol iJIT_NotifyEvent

**Created:** 2026-05-18 15:48:29

---

## Conversation

### 🤖 Assistant
*2026-05-18 15:58:50*

(foundationpose_ros) jinwz@jinwz-ubuntu:~/FoundationPoseROS2/FoundationPoseROS2$ python ./foundationpose_ros_multi.py
Traceback (most recent call last):
  File "/home/jinwz/FoundationPoseROS2/FoundationPoseROS2/./foundationpose_ros_multi.py", line 7, in <module>
    from estimater import *
  File "/home/jinwz/FoundationPoseROS2/FoundationPoseROS2/./FoundationPose/estimater.py", line 10, in <module>
    from Utils import *
  File "/home/jinwz/FoundationPoseROS2/FoundationPoseROS2/./FoundationPose/Utils.py", line 10, in <module>
    import os, sys, time,torch,pickle,trimesh,itertools,pdb,zipfile,datetime,imageio,gzip,logging,joblib,importlib,uuid,signal,multiprocessing,psutil,subprocess,tarfile,scipy,argparse
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/torch/__init__.py", line 367, in <module>
    from torch._C import *  # noqa: F403
ImportError: /home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/torch/lib/libtorch_cpu.so: undefined symbol: iJIT_NotifyEvent
(foundationpose_ros) jinwz@jinwz-ubuntu:~/FoundationPoseROS2/FoundationPoseROS2$

### 🤖 Assistant
*2026-05-18 15:58:50*

*[step-start part]*

💭 **Reasoning:**

<details>
<summary>Click to expand reasoning</summary>

The error is about PyTorch having an undefined symbol `iJIT_NotifyEvent`. This is typically caused by Intel VTune profiler incompatibility or a corrupted PyTorch installation.

The solution is usually to:
1. Unset the LD_PRELOAD environment variable that might be loading conflicting libraries
2. Reinstall PyTorch

Let me provide a concise solution.


</details>



This is a PyTorch/Intel VTune profiler conflict. Try:

```bash
unset LD_PRELOAD && python ./foundationpose_ros_multi.py
```

If that works, add this to your shell profile:
```bash
echo 'unset LD_PRELOAD' >> ~/.bashrc
```

Or reinstall PyTorch:
```bash
pip install --force-reinstall torch
```

*[step-finish part]*

### 🤖 Assistant
*2026-05-18 15:58:50*

Downloading torch-2.12.0-cp310-cp310-manylinux_2_28_x86_64.whl (532.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0.3/532.1 MB 4.3 kB/s eta 34:42:46
ERROR: Exception:
Traceback (most recent call last):
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_vendor/urllib3/response.py", line 438, in _error_catcher
    yield
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_vendor/urllib3/response.py", line 561, in read
    data = self._fp_read(amt) if not fp_closed else b""
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_vendor/urllib3/response.py", line 527, in _fp_read
    return self._fp.read(amt) if amt is not None else self._fp.read()
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_vendor/cachecontrol/filewrapper.py", line 100, in read
    data: bytes = self.__fp.read(amt)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/http/client.py", line 471, in read
    s = self.fp.read(amt)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/socket.py", line 717, in readinto
    return self._sock.recv_into(b)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/ssl.py", line 1307, in recv_into
    return self.read(nbytes, buffer)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/ssl.py", line 1163, in read
    return self._sslobj.read(len, buffer)
BrokenPipeError: [Errno 32] 断开的管道

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/cli/base_command.py", line 107, in _run_wrapper
    status = _inner_run()
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/cli/base_command.py", line 98, in _inner_run
    return self.run(options, args)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/cli/req_command.py", line 96, in wrapper
    return func(self, options, args)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/commands/install.py", line 419, in run
    preparer.prepare_linked_requirements_more(
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/operations/prepare.py", line 569, in prepare_linked_requirements_more
    self._complete_partial_requirements(
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/operations/prepare.py", line 478, in _complete_partial_requirements
    for link, (filepath, _) in batch_download:
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/network/download.py", line 183, in batch
    filepath, content_type = self(link, location)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/network/download.py", line 194, in __call__
    self._process_response(download, resp)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/network/download.py", line 211, in _process_response
    for chunk in chunks:
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/cli/progress_bars.py", line 69, in _rich_download_progress_bar
    for chunk in iterable:
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_internal/network/utils.py", line 65, in response_chunks
    for chunk in response.raw.stream(
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_vendor/urllib3/response.py", line 622, in stream
    data = self.read(amt=amt, decode_content=decode_content)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_vendor/urllib3/response.py", line 560, in read
    with self._error_catcher():
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/contextlib.py", line 153, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/pip/_vendor/urllib3/response.py", line 455, in _error_catcher
    raise ProtocolError("Connection broken: %r" % e, e)
pip._vendor.urllib3.exceptions.ProtocolError: ("Connection broken: BrokenPipeError(32, '断开的管道')", BrokenPipeError(32, '断开的管道'))
(foundationpose_ros) jinwz@jinwz-ubuntu:~/FoundationPoseROS2/FoundationPoseROS2$

### 🤖 Assistant
*2026-05-18 15:58:50*

*[step-start part]*

💭 **Reasoning:**

<details>
<summary>Click to expand reasoning</summary>

The download broke. The simplest fix for the original problem is to just unset LD_PRELOAD.


</details>



The download broke. The original fix is simpler - just unset LD_PRELOAD:

```bash
unset LD_PRELOAD && python ./foundationpose_ros_multi.py
```

If that works, make it permanent:
```bash
echo 'unset LD_PRELOAD' >> ~/.bashrc
```

*[step-finish part]*

### 🤖 Assistant
*2026-05-18 15:58:50*

unset LD_PRELOAD && python ./foundationpose_ros_multi.py不行，还是undefined symbol: iJIT_NotifyEvent错误

### 🤖 Assistant
*2026-05-18 15:58:50*

*[step-start part]*

💭 **Reasoning:**

<details>
<summary>Click to expand reasoning</summary>

The unset LD_PRELOAD didn't work. Let me think about other solutions:

1. The error is about `iJIT_NotifyEvent` - this is a symbol from Intel's JIT profiling library (used by Intel VTune or similar tools).

2. This could be caused by:
   - An incompatible version of PyTorch with the Intel profiling tools
   - A conflicting PyTorch installation
   - CUDA version mismatch

Let me suggest checking what's happening with the LD_PRELOAD and whether there's a specific library causing this.

Another approach is to try:
1. Check what PyTorch version is installed
2. Try reinstalling from the existing cache, or
3. Try installing a CPU-only version of PyTorch
4. Or check if there's a conflict with the CUDA versions

Let me suggest some diagnostic commands and potential fixes.


</details>



Try these steps:

```bash
# Check PyTorch version
python -c "import torch; print(torch.__version__)"

# Check what's preloaded
ldd /home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/torch/lib/libtorch_cpu.so | grep -i jit

# Try CPU-only PyTorch reinstall
pip install --no-cache-dir --force-reinstall torch==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
```

If still fails, the nuclear option:
```bash
pip uninstall torch -y && pip install torch==2.1.0
```

*[step-finish part]*

### 🤖 Assistant
*2026-05-18 15:58:50*

(foundationpose_ros) jinwz@jinwz-ubuntu:~/FoundationPoseROS2/FoundationPoseROS2$ python -c "import torch; print(torch.__version__)"  
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/torch/__init__.py", line 367, in <module>
    from torch._C import *  # noqa: F403
ImportError: /home/jinwz/miniconda3/envs/foundationpose_ros/lib/python3.10/site-packages/torch/lib/libtorch_cpu.so: undefined symbol: iJIT_NotifyEvent
(foundationpose_ros) jinwz@jinwz-ubuntu:~/FoundationPoseROS2/FoundationPoseROS2$

### 🤖 Assistant
*2026-05-18 15:58:50*

*[step-start part]*

💭 **Reasoning:**

<details>
<summary>Click to expand reasoning</summary>

The issue is clear now - PyTorch itself can't even be imported. The `iJIT_NotifyEvent` symbol is from Intel's VTune profiler. This usually happens when:

1. Intel VTune is installed and interfering
2. Some other Intel library is preloaded

Let me check what's setting this up. The symbol `iJIT_NotifyEvent` comes from `libjitprofiling.so`. Let me check if there's an environment variable or something setting LD_PRELOAD or LD_LIBRARY_PATH.

Let me ask to check the environment variables and see if there's Intel-related stuff.


</details>



PyTorch本身坏了。检查下是否有Intel相关的环境变量冲突：

```bash
env | grep -i intel
env | grep -i jt
env | grep -i preload
```

或者检查你的conda环境是否有问题：
```bash
pip uninstall torch -y
pip install torch
```

*[step-finish part]*
