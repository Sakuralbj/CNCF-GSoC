## arena serving场景
### Arena serving 与GPUShare的集成  

目的:serving的场景下，利用per_process_gpu_memory_fraction来控制serving任务占用的显存。  

问题:per_process_gpu_memory_fraction的值等于容器占用显存除以调度到GPU卡的显存，GPU卡的显存需要在调度完成后才能计算出来,而deployment模版中的参数需要在yaml创建前写入。  

解决方案:  

1.建立新的镜像，以tensorflow-serving-gpu为基础镜像，覆盖原有镜像的entrypoint，在dockerfile中加入必要的参数，如port,rest_api_port，per_process_gpu_memory_fraction等等。  
Docker file示例:  
```
FROM tensorflow/serving:latest-gpu
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y && apt install apt-utils -y && apt install bc -y
RUN echo '#!/bin/bash \n\n
tensorflow_model_server --port=8500 --rest_api_port=8501 --model_config_file=/tmp/config --per_process_gpu_memory_fraction=$(printf "%.10f" echo "scale=10; ${ALIYUN_COM_GPU_MEM_CONTAINER}/ ${ALIYUN_COM_GPU_MEM_DEV}" | bc) 
"$@"' > /usr/bin/tf_serving_entrypoint.sh 
&& chmod +x /usr/bin/tf_serving_entrypoint.sh
ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
```
缺点：因为要执行新的ENTRYPOINT，需要删除原有deployment模版中的command和args字段，对原有的GPU-count的场景会产生影响，不合适。  
  
2.加一个判定条件，在gpucount的场景下，deployment模版的args字段以变量的形式传入计算per_process_gpu_memory_fraction的表达式，在分配容器时环境变量注入后计算出per_process_gpu_memory_fraction的值。  

修改后的command和args字段:  
```
         command:
          - "sh"
          - "-c"
          args:
            - |
              /usr/bin/tensorflow_model_server --port={{ .Values.port }}{{- if .Values.rest_api_port }} --rest_api_port={{ .Values.rest_api_port }}
            {{- end }}{{- if ne .Values.modelConfigFileContent "" }} --model_config_file=/tmp/config{{- end }}{{- if gt (int $gpuMemory) 0 }} --per_process_gpu_memory_fraction=$(awk 'BEGIN{printf "%.2f",'$ALIYUN_COM_GPU_MEM_CONTAINER'/'$ALIYUN_COM_GPU_MEM_DEV'}')
            {{- end }}
          {{- end }}
```