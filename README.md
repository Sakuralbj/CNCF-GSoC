# Summary of GSoC 2019 (Run GPU sharing workloads with Kuberneres + kubeflow )
Student: **Jianbo Ma**(majb2114@zju.edu.cn)  

Mentor:  **Harry Zhang** (@resouer) ,**Kai Zhang**(@wsxiaozhang) ,**Jian He** (@jian-he)    
  
----

### Project description  
[GPUSharing](https://github.com/AliyunContainerService/gpushare-scheduler-extender) is an open source project which could share GPU by leveraging Kubernetes scheduling and Device Plugin extensibility.  
[Arena](https://github.com/kubeflow/arena) is a command-line interface for the data scientists to run and monitor the machine learning training jobs and check their results in an easy way.In the backend, it is based on Kubernetes, helm and Kubeflow. But the data scientists can have very little knowledge about kubernetes.  It's goal is to make the data scientists feel like to work on a single machine but with the Power of GPU clusters indeed.

  
### Goals
* Integrate arena with GPUSharing in tensorflow-serving situation.
* Integrate Nvidia MPS as the option for isolation

## Stage 1: Integrate arena with GPUSharing in tensorflow-serving situation.
### Achievement
* Finish an end to end tf-serving task using GPUShare.  
* Check the GPUMemory resource of kubernetes cluster. 
* Finish a user_guide of tf-serving with GPUShare.
### Design    
####  
##### 1. per_process_gpu_memory_fraction  
Per_process_gpu_memory_fraction is a fraction that each process occupies of the GPU memory space. The value is between 0.0 and 1.0 (with 0.0 as the default)   
If 1.0, the server will allocate all the memory when the server starts,   
If 0.0, Tensorflow will automatically select a valupe.  

For example, If we want the serving job to occupy half of the GPU resources,we can set per_process_gpu_memory_fraction equals to 0.5.

##### 2. The design process.   
 
Goals:After users submit the serving task,we need to calculate the correct per_process_gpu_memory_fraction and convert it as a parameter oo serving-task.  

per_process_gpu_memory_fraction=(required GPUMemory)/(total GPUMemory in allocated GPU card).

* The gpumemory serving task requires will be transformed into spec.container.resource.limits.aliyun.com/gpu-mem.
* After GPUShare scheduler-extender and device-plugin,environmental variable will be generated.  
* Required GPUMemory equals to ALIYUN_COM_GPU_MEM_CONTAINER,total GPUMemory in GPU card equals to ALIYUN_COM_GPU_MEM_DEV.
* per_process_gpu_memory_fraction=$ALIYUN_COM_GPU_MEM_CONTAINER/$ALIYUN_COM_GPU_MEM_DEV  
* If in GPUShare situation,convert per_process_gpu_memory_fraction in the task.

##### 3. The design  diagram.
![](https://ws3.sinaimg.cn/large/006tNc79gy1g605lvp09aj31ho0je762.jpg)

### Code
[tf-serving-gpushare](https://github.com/kubeflow/arena/pull/211)  
[View GPU resource of cluster](https://github.com/kubeflow/arena/pull/226)  
[User_guide](https://github.com/kubeflow/arena/pull/250)



## Stage 2: Integrate Nvidia MPS as the option for isolation
### Achievement
* Investigate how to use MPS.
* Test the capacity of MPS.  
* Integrate MPS with GPUShare,simplify user operations.  

### Design and result
* Use [MPS](MPS/MPSUserGuide.md)  
* Test [result](MPS/TestResult.md)
* Integratate [design](MPS/DesignMPS.md)


### Code
[User_guide and Integration](https://github.com/AliyunContainerService/gpushare-device-plugin/pull/14)


### To do
Test if  GPU thread is controled by MPS.  

Reference:  
1. [MPS](https://docs.nvidia.com/deploy/mps/index.html#topic_2_1_2)
2. [nvprof](https://devblogs.nvidia.com/cuda-pro-tip-nvprof-your-handy-universal-gpu-profiler/)


