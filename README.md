# CNCF GSoC 2019 (Run GPU sharing workloads with Kuberneres + kubeflow )
Student: **Jianbo Ma**(majb2114@zju.edu.cn)  

Mentor:  **Harry Zhang** (@resouer) ,**Kai Zhang**(@wsxiaozhang) ,**Jian He** (@jian-he)    
  
----

### Project description  
[GPUSharing](https://github.com/AliyunContainerService/gpushare-scheduler-extender) is an open source project which could share GPU by leveraging Kubernetes scheduling and Device Plugin extensibility.  
[Arena](https://github.com/kubeflow/arena) is a command-line interface for the data scientists to run and monitor the machine learning training jobs and check their results in an easy way.   Currently it supports solo/distributed TensorFlow training. In the backend, it is based on Kubernetes, helm and Kubeflow. But the data scientists can have very little knowledge about kubernetes.  It's goal is to make the data scientists feel like to work on a single machine but with the Power of GPU clusters indeed.

  
### Goals
* Integrate arena with GPUSharing in tensorflow-serving situation.
* Integrate Nvidia MPS as the option for isolation

## Stage 1:Integrate arena with GPUSharing in tensorflow-serving situation.
### Achievement
* Finish an end to end tf-serving task using GPUMemory.  
* Check the GPUMemory resource of K8s cluster. 
* Finish a User_guide of tf-serving with GPUMemory.
### Design  
[The design of tf-serving-gpushare](Arena/Design.md)

### Code
[tf-serving-gpushare](https://github.com/kubeflow/arena/pull/211)  
[View GPU resource of cluster](https://github.com/kubeflow/arena/pull/226)
[User_guide](https://github.com/kubeflow/arena/pull/250)



#### Stage2:Integrate Nvidia MPS as the option for isolation

* Investigate how to use MPS.
* Test the capacity of MPS.  
* Integrate MPS with GPUShare,simplify the operation of Users.


### Code
#### arena
[pr1](https://github.com/kubeflow/arena/pull/226) view GPU resource of the cluster  

[pr211](https://github.com/kubeflow/arena/pull/211) integrate tf-serving with GPUMemory

#### MPS




### to do
Find 

