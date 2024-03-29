This guide walks through the steps required to deploy and serve a TensorFlow model with GPU using Kubernetes (K8s) and Arena.

1\. Setup

Before using `Arena` for TensorFlow serving with GPU, we need to setup the environment including Kubernetes cluster.

Make sure that your Kubernetes cluster is running and follow the Kubernetes [instructions for enabling GPUs](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/).


2\. Create Persistent Volume for Model Files

Create /tfmodel in the NFS Server, and prepare mnist models by following the command:

```
mount -t nfs -o vers=4.0 NFS_SERVER_IP:/ /tfmodel/
wget https://github.com/osswangxining/tensorflow-sample-code/raw/master/models/tensorflow/mnist.tar.gz
tar xvf mnist.tar.gz
``` 

Then create Persistent Volume and Persistent Volume Claim by following the command (using NFS as sample):

Persistent Volume:
```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: tfmodel
  labels:
    tfmodel: nas-mnist
spec:
  persistentVolumeReclaimPolicy: Retain
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteMany
  nfs:
    server: NFS_SERVER_IP
    path: "/tfmodel"
```

Persistent Volume Claim:

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: tfmodel
  annotations:
    description: "this is tfmodel for mnist"
    owner: tester
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
       storage: 5Gi
  selector:
    matchLabels:
      tfmodel: nas-mnist
```

Check the data volume:
```
arena data list
NAME    ACCESSMODE     DESCRIPTION                OWNER   AGE
tfmodel  ReadWriteMany this is tfmodel for mnist  tester  31s
```


3\. Tensorflow serving with GPU

You can deploy and serve a Tensorflow model with GPU.If you want to serve a Tensorflow model with GPUMemory,please look at [GPUShare_UserGuide](User_guide_gpushare.md)

Submit tensorflow serving job to deploy and serve machine learning models using the following command.

```
arena serve tensorflow [flags]

options:
      --command string           the command will inject to container's command.
      --cpu string               the request cpu of each replica to run the serve.
  -d, --data stringArray         specify the trained models datasource to mount for serving, like <name_of_datasource>:<mount_point_on_job>
      --enableIstio              enable Istio for serving or not (disable Istio by default)
  -e, --envs stringArray         the environment variables
      --exposeService            expose service using Istio gateway for external access or not (not expose by default)
      --gpumemory int            the limit GPU memory of each replica to run the serve.
      --gpus int                 the limit GPU count of each replica to run the serve.
  -h, --help                     help for tensorflow
      --image string             the docker image name of serve job, default image is tensorflow/serving:latest (default "tensorflow/serving:latest")
      --imagePullPolicy string   the policy to pull the image, and the default policy is IfNotPresent (default "IfNotPresent")
      --memory string            the request memory of each replica to run the serve.
      --modelConfigFile string   Corresponding with --model_config_file in tensorflow serving
      --modelName string         the model name for serving
      --modelPath string         the model path for serving in the container
      --port int                 the port of tensorflow gRPC listening port (default 8500)
      --replicas int             the replicas number of the serve job. (default 1)
      --restfulPort int          the port of tensorflow RESTful listening port (default 8501)
      --servingName string       the serving name
      --servingVersion string    the serving version
      --versionPolicy string     support latest, latest:N, specific:N, all

Options inherited from parent commands
      --arenaNamespace string   The namespace of arena system service, like TFJob (default "arena-system")
      --config string           Path to a kube config. Only required if out-of-cluster
      --loglevel string         Set the logging level. One of: debug|info|warn|error (default "info")
      --namespace string        the namespace of the job (default "default")
      --pprof                   enable cpu profile      
```

3.1\. View the GPU resource of your cluster 

Before you submit the serving task,make sure you have GPU in your cluster and you have deployed [k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin#preparing-your-gpu-nodes)    
Using arena top node to see the GPU resource of your cluster.
```
# arena top node
NAME                                IPADDRESS     ROLE    STATUS  GPU(Total)  GPU(Allocated) 
cn-shanghai.i-uf61h64dz1tmlob9hmtb  192.168.0.71  <none>  ready   1           0               
cn-shanghai.i-uf61h64dz1tmlob9hmtc  192.168.0.70  <none>  ready   1           0               
cn-shanghai.i-uf6347ba9krw8hj5yvsy  192.168.0.67  master  ready   0           0               
cn-shanghai.i-uf662a07bhojl329pity  192.168.0.68  master  ready   0           0               
cn-shanghai.i-uf69zddmom136duk79qu  192.168.0.69  master  ready   0           0               
-------------------------------------------------------------------------------------------
Allocated/Total GPUs In Cluster:
0/2 (0%)  
```  
If your cluster have enough GPU resource,you can submit a serving task.  

3.2\. Submit tensorflow serving task  
you can submit a Tensorflow-GPU model with specific version policy as below.

```
arena serve tensorflow --name=mymnist1 --model-name=mnist1  --gpus=1   --image=tensorflow/serving:latest-gpu --data=tfmodel:/tfmodel --model-path=/tfmodel/mnist --versionPolicy=specific:1    

```

Once this command is triggered, one Kubernetes service will be created to expose gRPC and RESTful APIs of mnist model.The task will assume the same gpus as it request.
After the command,using arena top node to see the gpu resource of the cluster.
```
# arena top node
NAME                                IPADDRESS     ROLE    STATUS  GPU(Total)  GPU(Allocated)  
cn-shanghai.i-uf61h64dz1tmlob9hmtb  192.168.0.71  <none>  ready   1           0               
cn-shanghai.i-uf61h64dz1tmlob9hmtc  192.168.0.70  <none>  ready   1           1               
cn-shanghai.i-uf6347ba9krw8hj5yvsy  192.168.0.67  master  ready   0           0               
cn-shanghai.i-uf662a07bhojl329pity  192.168.0.68  master  ready   0           0               
cn-shanghai.i-uf69zddmom136duk79qu  192.168.0.69  master  ready   0           0               
-------------------------------------------------------------------------------------------
Allocated/Total GPUs In Cluster:
1/2 (50%)  

```
If you want to see the details of pod ,you can use arena top node -d.
```
#arena top node -d
NAME:       cn-shanghai.i-uf61h64dz1tmlob9hmtc
IPADDRESS:  192.168.0.70
ROLE:       <none>

NAMESPACE  NAME                                          GPU REQUESTS   
default    mymnist1-tensorflow-serving-76d5c7c8fc-2kwpw  1             

Total GPUs In Node cn-shanghai.i-uf61h64dz1tmlob9hmtc:      1         
Allocated GPUs In Node cn-shanghai.i-uf61h64dz1tmlob9hmtc:  1 (100%)  
```

4\. List all the serving jobs

You can use the following command to list all the serving jobs.

```
# arena serve list
  NAME      TYPE        VERSION  DESIRED  AVAILABLE  ENDPOINT_ADDRESS  PORTS
  mymnist1  TENSORFLOW           1        1          172.19.10.38      serving:8500,http-serving:8501
```
  

5\. Test RESTful APIs of serving models 

Deploy the `sleep` pod so you can use `curl` to test above serving models via RESTful APIs.

```
# cat <<EOF | kubectl create -f -
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: sleep
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: sleep
    spec:
      containers:
      - name: sleep
        image: tutum/curl
        command: ["/bin/sleep","infinity"]
        imagePullPolicy: IfNotPresent
EOF
```



Find the name of  `sleep` pod and enter into this pod, for example:

```
# kubectl exec -it sleep-5dd9955c58-km59h -c sleep bash
```

In this pod, use `curl` to call the exposed Tensorflow serving RESTful API:

```
# curl -X POST http://ENDPOINT_ADDRESS:8501/v1/models/mnist:predict -d '{"signature_name": "predict_images", "instances": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3294117748737335, 0.7254902124404907, 0.6235294342041016, 0.5921568870544434, 0.2352941334247589, 0.1411764770746231, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8705883026123047, 0.9960784912109375, 0.9960784912109375, 0.9960784912109375, 0.9960784912109375, 0.9450981020927429, 0.7764706611633301, 0.7764706611633301, 0.7764706611633301, 0.7764706611633301, 0.7764706611633301, 0.7764706611633301, 0.7764706611633301, 0.7764706611633301, 0.6666666865348816, 0.2039215862751007, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.26274511218070984, 0.44705885648727417, 0.2823529541492462, 0.44705885648727417, 0.6392157077789307, 0.8901961445808411, 0.9960784912109375, 0.8823530077934265, 0.9960784912109375, 0.9960784912109375, 0.9960784912109375, 0.9803922176361084, 0.8980392813682556, 0.9960784912109375, 0.9960784912109375, 0.5490196347236633, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.06666667014360428, 0.25882354378700256, 0.05490196496248245, 0.26274511218070984, 0.26274511218070984, 0.26274511218070984, 0.23137256503105164, 0.08235294371843338, 0.9254902601242065, 0.9960784912109375, 0.41568630933761597, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.32549020648002625, 0.9921569228172302, 0.8196079134941101, 0.07058823853731155, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.08627451211214066, 0.9137255549430847, 1.0, 0.32549020648002625, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5058823823928833, 0.9960784912109375, 0.9333333969116211, 0.1725490242242813, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.23137256503105164, 0.9764706492424011, 0.9960784912109375, 0.24313727021217346, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5215686559677124, 0.9960784912109375, 0.7333333492279053, 0.019607843831181526, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.03529411926865578, 0.803921639919281, 0.9725490808486938, 0.22745099663734436, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4941176772117615, 0.9960784912109375, 0.7137255072593689, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.29411765933036804, 0.9843137860298157, 0.9411765336990356, 0.22352942824363708, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.07450980693101883, 0.8666667342185974, 0.9960784912109375, 0.6509804129600525, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.011764707043766975, 0.7960785031318665, 0.9960784912109375, 0.8588235974311829, 0.13725490868091583, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.14901961386203766, 0.9960784912109375, 0.9960784912109375, 0.3019607961177826, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.12156863510608673, 0.8784314393997192, 0.9960784912109375, 0.45098042488098145, 0.003921568859368563, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5215686559677124, 0.9960784912109375, 0.9960784912109375, 0.2039215862751007, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2392157018184662, 0.9490196704864502, 0.9960784912109375, 0.9960784912109375, 0.2039215862751007, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4745098352432251, 0.9960784912109375, 0.9960784912109375, 0.8588235974311829, 0.1568627506494522, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4745098352432251, 0.9960784912109375, 0.8117647767066956, 0.07058823853731155, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]}'
```

You should update request url with your model service ENDPOINT_ADDRESS and modelname accordingly. 

The value of "instances" is actually a list of numeric pixels of the first image (which is a hand-written digit "7") in MNIST test dataset.

So you may get response as below. It means the model predicts the input data as "7" with the highest probability among all 10 digits.

```
{
    "predictions": [[2.04608277e-05, 1.72721537e-09, 7.74099826e-05, 0.00364777888, 1.25222812e-06, 2.27521778e-05, 1.14668968e-08, 0.99597472, 3.68833353e-05, 0.000218785644]]
}
```

6\. Delete one serving job

You can use the following command to delete a tfserving job and its associated pods
                                     
```
# arena serve delete mymnist1
configmap "mymnist1-tensorflow-serving-cm" deleted
service "mymnist1-tensorflow-serving" deleted
deployment.extensions "mymnist1-tensorflow-serving" deleted
configmap "mymnist1-tf-serving" deleted
INFO[0000] The Serving job mymnist1 has been deleted successfully
```
