### Docker Image
1. registry.cn-hangzhou.aliyuncs.com/tensorflow-samples/nbody  nbody task.
2. sakuralbj/mytest:v2 tensorflow task,no control for GPUUsage.
3. sakuralbj/sakuralbj:dynamic tensorflow task，tf_config.gpu_options.allow_growth = True control GPUUsage.  
### Result  

1. nbody task. 
 ![Result](https://ws1.sinaimg.cn/large/006tNc79ly1g3xgcy9m3uj318e0h2dhc.jpg)
2. tensorflow task,no GPUUsage limit.  
 ![Result](https://ws4.sinaimg.cn/large/006tNc79ly1g4s7ubcv4oj315a09mjsm.jpg)  
3. tensorflow task,tf_config.gpu_options.allow_growth = True
 ![Result](https://ws4.sinaimg.cn/large/006tNc79ly1g4s7qow9zzj315c09o75e.jpg)  
    