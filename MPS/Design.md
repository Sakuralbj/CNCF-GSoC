---
title: "Integrate Device-plugin with MPS"
date: 2019-07-10
draft: false
---

## 目标
在GPUshare的device-plugin部分将volume信息和环境变量信息注入容器，减少用户操作。 
  
## 流程

### 前提 
1. 整个过程分为两个角色，集群部署者和使用者。部署者完成GPUShare部署和MPS功能启用，在部署的过程中，部署者设定MPS
各个组件的交互通道目录，因此可以将这个目录在部署时以全局变量的形式传入，部署者在node上用相同的值启用MPS.  


2.  GPUShare的Device-plugin机制：kubelet在node上实际创建pod时，最终会执行allocate方法，会将kubelet本身缓存记录的资源可用量进行判断和计算，然后选定要使用的设备，
    向device-plugin发送Allocate调用，device-plugin会针对request中的设备id，检查是否可用，并将使用这几个设备需要的使用参数返回给kubelet.  
    ``` 
    type ContainerAllocateResponse struct {
    	// List of environment variable to be set in the container to access one of more devices.
    	Envs map[string]string `protobuf:"bytes,1,rep,name=envs" json:"envs,omitempty" protobuf_key:"bytes,1,opt,name=key,proto3" protobuf_val:"bytes,2,opt,name=value,proto3"`
    	// Mounts for the container.
    	Mounts []*Mount `protobuf:"bytes,2,rep,name=mounts" json:"mounts,omitempty"`
    	// Devices for the container.
    	Devices []*DeviceSpec `protobuf:"bytes,3,rep,name=devices" json:"devices,omitempty"`
    	// Container annotations to pass to the container runtime
    	Annotations map[string]string `protobuf:"bytes,4,rep,name=annotations" json:"annotations,omitempty" protobuf_key:"bytes,1,opt,name=key,proto3" protobuf_val:"bytes,2,opt,name=value,proto3"`
    }
    ``` 
    
  
### 步骤
1. 在程序入口处设定一个保存MPS组件通信通道的路径。部署时由部署者设定，在node上启用时保持一致。  
![MPS pipie](https://ws3.sinaimg.cn/large/006tNc79ly1g4uzt05dftj31g205s43r.jpg)  
设定通道入口路径，mps-pipe的值表示要传入的交互路径。  

在device-plugin的部署文件中传入这个全局变量  
``` 
command:
          - gpushare-device-plugin-v2
          - -logtostderr
          - --v=5
          - --memory-unit=GiB
          - --mps-pipe=/root/nvidia-mps
 ``` 
2.DevicePlugin结构体设计
``` 
type NvidiaDevicePlugin struct {
	devs         []*pluginapi.Device
	realDevNames []string
	devNameMap   map[string]uint
	devIndxMap   map[uint]string
	socket       string
	mps          bool
	healthCheck  bool
	mpspipe      string
	stop         chan struct{}
	health       chan *pluginapi.Device

	server *grpc.Server
	sync.RWMutex
}
``` 
说明:mpspipe的值代表交互路径。  

3.NvidiaDevicePlugin的Allocate段将变量传入
  
  NvidiaDevicePlugin的allocate函数会返回pluginapi.AllocateResponse类型.  
  AllocateResponse由ContainerAllocateResponse组成。
  ``` 
      type ContainerAllocateResponse struct {
      	// List of environment variable to be set in the container to access one of more devices.
      	Envs map[string]string `protobuf:"bytes,1,rep,name=envs" json:"envs,omitempty" protobuf_key:"bytes,1,opt,name=key,proto3" protobuf_val:"bytes,2,opt,name=value,proto3"`
      	// Mounts for the container.
      	Mounts []*Mount `protobuf:"bytes,2,rep,name=mounts" json:"mounts,omitempty"`
      	// Devices for the container.
      	Devices []*DeviceSpec `protobuf:"bytes,3,rep,name=devices" json:"devices,omitempty"`
      	// Container annotations to pass to the container runtime
      	Annotations map[string]string `protobuf:"bytes,4,rep,name=annotations" json:"annotations,omitempty" protobuf_key:"bytes,1,opt,name=key,proto3" protobuf_val:"bytes,2,opt,name=value,proto3"`
      }
   ``` 
 
   mount数据结构的定义:  
   ```
   type Mount struct {
   	// Path of the mount within the container.
   	ContainerPath string `protobuf:"bytes,1,opt,name=container_path,json=containerPath,proto3" json:"container_path,omitempty"`
   	// Path of the mount on the host.
   	HostPath string `protobuf:"bytes,2,opt,name=host_path,json=hostPath,proto3" json:"host_path,omitempty"`
   	// If set, the mount is read-only.
   	ReadOnly bool `protobuf:"varint,3,opt,name=read_only,json=readOnly,proto3" json:"read_only,omitempty"`
   }
   ```
  
   在Envs字段传入要注入容器的环境变量,mount字段传入容器的volume信息。
     
         
     for _, req := range reqs.ContainerRequests {
   			reqGPU := uint(len(req.DevicesIDs))
   			mount := pluginapi.Mount{
   				ContainerPath: m.mpspipe,
   				HostPath:      m.mpspipe,
   			}
   			response := pluginapi.ContainerAllocateResponse{
   				Envs: map[string]string{
   					envNVGPU:               candidateDevID,
   					EnvResourceIndex:       fmt.Sprintf("%d", id),
   					EnvResourceByPod:       fmt.Sprintf("%d", podReqGPU),
   					EnvResourceByContainer: fmt.Sprintf("%d", reqGPU),
   					EnvResourceByDev:       fmt.Sprintf("%d", getGPUMemory()),
   					EnvPipe:                fmt.Sprintf(m.mpspipe),
   					EnvPercentage:          fmt.Sprint(100 * reqGPU / getGPUMemory()),
   				},
   				Mounts: []*pluginapi.Mount{&mount},
   			}
   			responses.ContainerResponses = append(responses.ContainerResponses, &response)
   		}
       
  说明:EnvResourceByContainer代表容器请求GPUmemory,EnvPipe为CUDA_MPS_PIPE_DIRECTORY，
     EnvPercentage代表CUDA_MPS_ACTIVE_THREAD_PERCENTAGE，控制gpu资源使用量。
     
### 流程图
![Design](https://ws1.sinaimg.cn/large/006tNc79ly1g4v15g25ohj31ed0u0tf4.jpg) 