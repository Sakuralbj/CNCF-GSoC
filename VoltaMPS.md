## 组成

Three components:
+ Control Daemon Process – The control daemon is responsible for starting and stopping the server, as well as coordinating connections between clients and servers.
+ Client Runtime – The MPS client runtime is built into the CUDA Driver library and may be used transparently by any CUDA application
+ Server Process – The server is the clients' shared connection to the GPU and provides concurrency between clients

1. Volta MPS clients submit work directly to the GPU without passing through the MPS server.
2. Each Volta MPS client owns its own GPU address space instead of sharing GPU address space with all other MPS clients.
3. Volta MPS supports limited execution resource provisioning for Quality of Service (QoS).
![Volta mps](https://ws4.sinaimg.cn/large/006tNc79ly1g3y4rwi9ovj30me0oowgy.jpg)

## 环境变量
+ CUDA_VISIBLE_DEVICES
+ CUDA_MPS_PIPE_DIRECTORY
+ CUDA_MPS_LOG_DIRECTORY
+ CUDA_DEVICE_MAX_CONNECTIONS
+ CUDA_MPS_ACTIVE_THREAD_PERCENTAGE

## 运行mps

#### Starting MPS control daemon
+ export CUDA_VISIBLE_DEVICES=？
+ nvidia-smi -i ID -c EXCLUSIVE_PROCESS
+ export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps
+ export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log
+ nvidia-cuda-mps-control -d 

#### Starting MPS client application
Note that CUDA_VISIBLE_DEVICES should not be set in the client’s environment
+ export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps
+ export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log

#### Shutting Down MPS
+ echo quit | nvidia-cuda-mps-control

#### Log file
+ $CUDA_MPS_LOG_DIRECTORY/control.log
+ $CUDA_MPS_LOG_DIRECTORY/server.log
  