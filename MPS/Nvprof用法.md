### 1.nvprof
1.1 描述:是用来测试了解并优化CUDA或OpenACC应用程序的性能的分析工具,
能够从命令行收集和查看分析数据。 
  
简要介绍:https://gist.github.com/sonots/5abc0bccec2010ac69ff74788b265086   
示例：nvprof --print-gpu-trace python train_mnist.py 

 
使用方法:Usage: nvprof [options] [application] [application-arguments]  

示例:nvprof ./a.out,a.out为编译后的可执行文件

### 2.visual profiler  
File .new session 剖析的应用程序exe文件