---
id: 3d7e564d-502a-440c-b1d3-4696f231638f
title: 速记
tags:
  - meta
---


## SSH 转发 X 11

- 修改服务端的 `/etc/ssh/sshd_config`，把相关功能打开
- 本地链接的时候使用 `ssh -Y <ip>` （或者 `ssh -X <ip>`）
- 输入 `xclock` 或者 `rqt`


## 编译出现警告 `WARNING:colcon.colcon_ros.prefix_path.ament:The path '/home/artinx/artinxrub/install/rm_auto_aim' in the environment variable AMENT_PREFIX_PATH doesn't exist`

警告原因：你的环境变量 AMENT_PREFIX_PATH/CMAKE_PREFIX_PATH 里残留了不存在的安装目录（rm_auto_aim、armor_solver、armor_detector），通常是之前构建过、后来目录被删或被 COLCON_IGNORE 跳过导致的。

```bash
#!/bin/bash

# Clean AMENT_PREFIX_PATH and CMAKE_PREFIX_PATH from non-existent paths.
# Usage: source rm_scripts/clean_ros_env.sh

set -euo pipefail

filter_paths() {
  local input="${1:-}"
  local output=()
  local path

  if [[ -z "$input" ]]; then
    echo ""
    return 0
  fi

  IFS=':' read -r -a parts <<< "$input"
  for path in "${parts[@]}"; do
    if [[ -n "$path" && -d "$path" ]]; then
      output+=("$path")
    fi
  done

  local IFS=':'
  echo "${output[*]}"
}

if [[ -n "${AMENT_PREFIX_PATH:-}" ]]; then
  export AMENT_PREFIX_PATH
  AMENT_PREFIX_PATH="$(filter_paths "$AMENT_PREFIX_PATH")"
fi

if [[ -n "${CMAKE_PREFIX_PATH:-}" ]]; then
  export CMAKE_PREFIX_PATH
  CMAKE_PREFIX_PATH="$(filter_paths "$CMAKE_PREFIX_PATH")"
fi

echo "Cleaned AMENT_PREFIX_PATH and CMAKE_PREFIX_PATH."
```

修复步骤（任选其一）：

不构建这些包：在当前终端先 source /opt/ros/humble/setup. Bash，再 source rm_scripts/clean_ros_env. Sh，然后重新 colcon build。

需要这些包：移除对应包的 COLCON_IGNORE 并重新构建，让 install 目录生成后警告自然消失。


## ROS 2 包结构

ROS 2 不必死守 src 目录，它的 colcon 会自动找子目录，把每个有 `package.xml` 的文件夹视作软件包。

```
In this package, headers install destination is set to `include` by ament_auto_package. It is recommended to install `include/xxx` instead and will be the default behavior of ament_auto_package from ROS 2 Kilted Kaiju. On distributions before Kilted, ament_auto_package behaves the same way when you use USE_SCOPED_HEADER_INSTALL_DIR option.
```


## 自瞄框架设计

> 什么是理想的架构？什么是理想的代码？

首先要清晰易懂好维护！

尽量做到高内聚！一个 pkg 在链接层面，应该尽可能少依赖其他 pkg，独立完成任务。这样也适合分工开发。这也是换 ros 的原因。

为什么要迁移到 ros？因为好调，各种要追踪的关键数据都是直接发布到话题，很容易就能知道哪里不对。各节点通过 topic 读取数据，因此要统一相关话题、消息的设计规范。最好写个文档。

- 换原生logger，方便调车！
- 删掉原本的 heartbeat，原生 respawn=True 可以重启
- *尝试使用 lifecycle + node_manager 设计*
- 相机驱动
- 串口驱动（试试epoll？）
- 数据采集时的本地时间戳支持
- 手眼标定与 ros 2 话题的支持
- 能量机关模块
- 自瞄模块

- Yolo pose 网络训练，目前是 3+臂灯的角点设计
- Ypd 的卡尔曼调参。加减速的平动---有加速度的卡尔曼
- 坐标系转换都用 eigen
- ~~时间戳球面插值~~，同济的代码有，后续可加。但重要的是同步画面和 imu 的时间。可以考虑用脚本去测延迟。要跟电控商量协议。
- 开火延迟不稳定的问题，测试标准改成 dps 而非命中率。
- JetPack 6.2 SuperMode 刷系统，升级 tensorRT，换载板 https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules/

Utils：当确实很多地方要用再写。个人认为简单的功能函数，比如图像处理流程，不需要套 class，直接一个 `Utils.hpp` 声明函数+一堆 cpp 就好。命名空间在必要时才套，本身的 pkg 隔离就已经提供了很好的效果。

删去有些不必要的组件（特别是 ros 已经提供的组件，比如 Logger）以后差不多是下面的样子。真的不要重复造不必要的轮子！

```
add_library(tools OBJECT 
    exiter.cpp
    extended_kalman_filter.cpp
    ransac_sine_fitter.cpp
    img_tools.cpp
    math_tools.cpp
    plotter.cpp
    trajectory.cpp
    recorder.cpp
    logger.cpp [*Deleted]
    pid.cpp
    crc.cpp
)
```

```
./rm_utils/
├── CMakeLists.txt
├── include
│   └── rm_utils
|       ├── logger        [*Deleted]
│       ├── assert.hpp
│       ├── common.hpp
│       ├── heartbeat.hpp [*Deleted]
│       ├── math
│       │   ├── extended_kalman_filter.hpp
│       │   ├── manual_compensator.hpp
│       │   ├── particle_filter.hpp
│       │   ├── pnp_solver.hpp
│       │   ├── trajectory_compensator.hpp
│       │   └── utils.hpp
│       └── url_resolver.hpp
```


中南的框架设计有没有问题？Namespace 太多、重复造 Logger 的轮子、没有清晰的决策层。

要不要用同济的开源？用多少，全抄？怎么用？我们自己的 ros 要怎么设计？

TensorRT 的推理加速头文件需不需要公开出来？

