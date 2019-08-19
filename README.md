### CNCF GSoC 2019 (Run GPU sharing workloads with Kuberneres + kubeflow )
### Background
1\.GPUShare  
[GPUShare](https://github.com/AliyunContainerService/gpushare-scheduler-extender) is a solution on native Kubernetes, it is based on scheduler extender and device-plugin and it helps data scientists run  their Nvidia GPU based inference tasks on same Nvidia GPU device using Kubernetes.   
2\.Arena 
[Arena](https://github.com/kubeflow/arena) is a command-line interface for the data scientists to run and monitor the machine learning training jobs and check their results in an easy way.   
Currently it supports solo/distributed TensorFlow training. In the backend, it is based on Kubernetes, helm and Kubeflow. But the data scientists can have very little knowledge about kubernetes.  
It's goal is to make the data scientists feel like to work on a single machine but with the Power of GPU clusters indeed.  

### Goals
* Intergrate arena with Gpushare in tensorflow-serving situation.
* Integrate Nvidia MPS as the option for isolation

###
