1 在node节点上开启mps服务
+ export CUDA_VISIBLE_DEVICES=ID
+ nvidia-smi -c EXCLUSIVE_PROCESS
+ export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps ##默认/tmp/nvidia-mps
+ export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log  ##/var/log/nvidia-mps
+ nvidia-cuda-mps-control -d   

2  根据yaml文件创建任务  

kubectl create -f binpackmps2.yaml  

kubectl create -f nbody.yaml  

 3 在node上nvidia-smi查看GPU使用状况，进入/tmp/nvidia-log查看日志
  