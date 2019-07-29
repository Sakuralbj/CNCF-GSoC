# arena top node实现思路  

## 前提:每个node要么是GPUShare节点，要么是以卡分配，不能共存。  

### 1.整个集群中没有GPUShare节点。
此时要显示的信息，包括allocated gpu,total gpu,gpuUsage  

1.1 获取集群的所有pod,以及所有node，构建node和pod信息的nodeinfo数组，每一项包含node和该node上的所有pod。  
1.2 对于每个node节点，totalgpu为nvidia.com/gpu的数量，通过k8s-device-plugin获取到，allocated gpu为该node上所有pod中容器申请的nvidia.com/gpu的数目和，计算每个容器的request nvidia.com/gpu的数目和。  

### 2.整个集群中有GPUShare节点
2.1 加上一列表示是否为GPUShare节点,对于一个node，若是，则显示sharable，否则显示N/A。  
2.2 对于每个nodeinfo，首先判断该node是否为gpushare场景，若是，则构建该node的Deviceinfo信息。  
2.3  对于GPUShare节点和普通节点，total gpu和allocated gpu的计算方式不同。  
* 对于普通节点，total gpu为nvidia.com/gpu的数目，allocated-gpu数目为该node上所有pod的GPU数之和。   
* 对于GPUShare节点，total gpu为aliyun.com/gpu的数目，allocated gpu的值需要根据node的deviceinfo来获取，deviceinfo中多少张卡的usegpumem大于0，则allocated gpu的值为多少。  

### 3.最终效果  
* arena top node 显示所有节点的GPU使用信息，如果在整个集群中有GPUShare的场景，则增加一列表示节点是否为GPUShare的节点，Sharable表示是，N/A代表不是，若整个集群都无GPUShare节点，则不显示该列。(若某个节点为GPUShare的场景，某一张卡只要有显存被占用，则认为该卡被allocated）  

* arena top node -d，显示节点GPU的详细信息，包括占用GPU卡的pod的详细信息，如name和namespace以及占用多少卡。若node为GPUShare的场景，则显示该node为sharable。  

* arena top node -s,只显示所有GPUShare节点信息，包括该node上多少张GPU卡，每张卡总的显存(total）以及分配的显存(allocated),以及所有GPUShare节点的总显存和总分配显存。  

* arena top node -s -d，显示所有GPUShare节点的详细信息，包括分配在每个node上的gpushare任务NAME,NAMESPACEE,占用的哪张GPU卡的显存数。