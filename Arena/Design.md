## The design of tf-serving with GPUShare. 

1. per_process_gpu_memory_fraction  

Fraction that each process occupies of the GPU memory space. The value is between 0.0 and 1.0 (with 0.0 as the default)   
If 1.0, the server will allocate all the memory when the server starts,   
If 0.0, Tensorflow will automatically select a valupe.  

For example, If we want the serving job to occupy half of the GPU resources,we can set per_process_gpu_memory_fraction equals to 0.5.

2. The design process.   
 
Goals:After users submit the serving task,we need to calculate the correct per_process_gpu_memory_fraction.  

per_process_gpu_memory_fraction=required GPUMemory/total GPUMemory in GPU card.

* The gpumemory serving task requires will be transformed into spec.container.resource.limits.aliyun.com/gpu-mem.
* After GPUShare scheduler-extender and device-plugin,environmental variable will be generated.  
* Required GPUMemory equals to ALIYUN_COM_GPU_MEM_CONTAINER,total GPUMemory in GPU card equals to ALIYUN_COM_GPU_MEM_DEV.
* per_process_gpu_memory_fraction=$ALIYUN_COM_GPU_MEM_CONTAINER/$ALIYUN_COM_GPU_MEM_DEV

3. The design  diagram.
![](https://ws3.sinaimg.cn/large/006tNc79gy1g605lvp09aj31ho0je762.jpg)