# MPS功能启用与GPUShare整合的设计
1. 管理者在node上启用MPS:  
    启用Daemonset :  
    export CUDA_VISIBLE_DEVICES=ID  // specify which GPU’s should be visible to a CUDA application   
     
    export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps //MPS应用交互的管道，默认为/tmp/nvidia-mps  
    
    export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log //日志目录，默认为/var/log/nvidia-mps  
    
    nvidia-smi -c EXCLUSIVE_PROCESS//设置GPU的运算模式
    
    nvidia-cuda-mps-control -d //启用MPS  
    
    ps -ef | grep mps//观察MPS daemon是否启用  
    
    echo quit | nvidia-cuda-mps-control //退出MPS  
    
2. client的启用(yaml文件环境变量写入)  
    export CUDA_MPS_ACTIVE_THREAD_PERCENTAGE=设置的值
    hostIPC=true  
    yaml文件示例:
    ![yaml](https://ws3.sinaimg.cn/large/006tNc79ly1g4s8i3jtqvj30u00lo79y.jpg)  
      
3. 整合设计
    GPUShare的Device-plugin机制：
    kubelet在node上实际创建pod时，最终会执行allocate方法，会将kubelet本身缓存记录的资源可用量进行判断和计算，然后选定要使用的设备，向device-plugin发送Allocate调用，device-plugin会针对request中的设备id，检查是否可用，并将使用这几个设备需要的使用参数返回给kubelet，返回的格式是:  
    ![Result](https://ws3.sinaimg.cn/large/006tNc79ly1g4s8jgdxmwj30bk02wgq1.jpg)  
    在Envs中将需要传入容器中的MPS环境变量传入回去，CUDA_MPS_ACTIVE_THREAD_PERCENTAGE=100*EnvResourceByPod/EnvResourceByDev  
    
    最终的设计:  
    
    ![Design](https://ws2.sinaimg.cn/large/006tNc79ly1g4s8kety1kj30bj05tn6b.jpg)  
    整合后的yaml文件:  
    ![yaml](https://ws3.sinaimg.cn/large/006tNc79ly1g4s8ll16b4j30ty0j4tb4.jpg)
    