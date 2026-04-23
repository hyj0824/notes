---
id: 1b01882a-539b-4304-ae89-8d57b1b11ae0
title: TensorRT
tags:
  - no-tag
---


使用TensorRt加载onnx模型的步骤其实是很固定的,根据官方例呈给出的示范,加载一个onnx的模型分为以下几步

> - 创建builder(构建器)
> - 创建网络定义：builder —> network
> - 配置参数：builder —> config
> - 生成engine：builder —> engine (network, config)
> - 序列化保存：engine —> serialize
> - 释放资源：delete


https://zhuanlan.zhihu.com/p/157319734

https://docs.nvidia.com/deeplearning/tensorrt/latest/architecture/architecture-overview.html#deploy_opt_model

https://www.cnblogs.com/CrescentWind/p/18229812#1-%E6%A8%A1%E5%9E%8B%E5%8A%A0%E8%BD%BD