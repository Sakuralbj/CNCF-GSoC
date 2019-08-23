
## Goal  
Inject volume information and environment variable into the container in device-plugin part of GPUShare to simplify the operation of users.
  
## Process

### premise
1. Two roles，deployer and user.  
* Deployer:Deploy GPUShare and start MPS.In the process of deploy,deployer set the Unix socket of each component,
and the directory can be injected as global variable. 
* User:Using the same directory of deployer. 


2.  Device plugin of GPUShare：  
When kubelet actually creates a pod on the node, it will eventually execute the allocate method, which will judge and calculate the resource availability of the cached record of the kubelet itself, and then select the device to be used.  
Sends an Allocate call to the device-plugin. The device-plugin checks for availability of the device id in the request and returns the required parameters to the kubelet using the devices.
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
    
  
### Step
1. Set a path to save the communication channel of the MPS component at the program entry. It is set by the deployer at deployment time and is consistent when enabled on the node.  
![MPS pipie](https://ws3.sinaimg.cn/large/006tNc79ly1g4uzt05dftj31g205s43r.jpg)  
Set the channel entry path, and the value of mps-pipe indicates the interaction path to be passed in.  
Pass in this global variable in the device-plugin deployment file 
``` 
command:
          - gpushare-device-plugin-v2
          - -logtostderr
          - --v=5
          - --memory-unit=GiB
          - --mps-pipe=/root/nvidia-mps
 ``` 
2.DevicePlugin design
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
  

3.NvidiaDevicePlugin Allocate pass variable  
 The allocate function of NvidiaDevicePlugin will return the pluginapi.AllocateResponse type.
  AllocateResponse consists of ContainerAllocateResponse.
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
 
   mount struct definition:  
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
  
  In the Envs field, pass in the environment variable to be injected into the container, and the mount field is passed to the container's volume information.
     
         
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
       
  Description:   
  EnvResourceByContainer stands for GPUmemory on behalf of the container, EnvPipe is CUDA_MPS_PIPE_DIRECTORY, EnvPercentage stands for CUDA_MPS_ACTIVE_THREAD_PERCENTAGE and controls gpu resource usage.
     
### 流程图
![Design](https://ws3.sinaimg.cn/large/006y8mN6ly1g69e8c3xotj31cx0u0dm5.jpg) 