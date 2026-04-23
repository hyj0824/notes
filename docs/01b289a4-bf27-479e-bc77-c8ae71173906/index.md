---
id: 01b289a4-bf27-479e-bc77-c8ae71173906
title: ROS2
tags:
  - no-tag
---

## 注意

任何操作之前都要激活环境，类似 conda：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

报 doesn't exist 多数情况是没有 source 导致从 PATH 找不到包。Python 包的 PATH 用的是另外一个环境变量。

ROS安装的默认目录在/opt/ros/下，humble版本的ROS安装目录在/opt/ros/humble下。

DOMAIN-ID：介于0和101之间的安全的域ID (包括0和101)。每个计算机应为不同 DOMAIN。使用 `export ROS_DOMAIN_ID=0`

---

## 依赖、构建、包管理

### 项目初始化创建 pkg

```bash
# 进入src目录
cd ~/ros2_ws/src

# 创建一个名为 my_cpp_pkg 的包，并生成一个名为 my_node 的基础C++源文件
ros2 pkg create  my_cpp_pkg --build-type ament_cmake --node-name my_node
ros2 pkg create example_cpp --build-type ament_cmake --dependencies rclcpp
```

*   `--build-type ament_cmake`: 明确指定为 C++包。
*   `--node-name my_node`: 会自动在 `src/` 下创建一个 `my_node.cpp` 的骨架文件。

```bash
# 全参数
cd ${WorkspaceFolder}
ros2 pkg create example_parameters_rclcpp --build-type ament_cmake --dependencies rclcpp --destination-directory src --node-name parameters_basic --maintainer-name "hyj0824" --maintainer-email "12510430@mail.sustech.edu.cn"
```

### 构建运行

```bash
# 1. 回到工作区根目录
cd ~/ros2_ws

# 2. 构建所有包 (或指定包)
colcon build
# 或者，只构建你修改的包，速度更快
# colcon build --packages-select my_cpp_pkg

# 3. 设置环境 (非常重要！每次打开新终端都要执行)
source install/setup.bash

# 4. 运行你的节点
ros2 run my_cpp_pkg my_node
ros2 run <package_name> <node_name>
```

### 手动添加依赖

**编辑 `package.xml` -> 编辑 `CMakeLists.txt` -> `rosdep install` -> `colcon build`**

#### **第 1 步: 编辑 `package.xml` (声明依赖)**

**依赖类型解释**:

*   `<depend>`: **最常用**。表示编译和运行时都需要这个包。
*   `<build_depend>`: 仅在编译时需要。
*   `<exec_depend>`: 仅在运行时需要。
*   `<test_depend>`: 仅在测试时需要 (例如 `gtest`)。

**示例**: 添加 `rclcpp` (通常已存在) 和 `std_msgs`。

```xml
<!-- my_cpp_pkg/package.xml -->
...
  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>ament_cmake_auto</buildtool_depend>

  <depend>rclcpp</depend> 
  <depend>std_msgs</depend>
  <!-- !! 在这里手动添加你的新依赖 !! --> 

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
...
```

#### **第 2 步: 编辑 `CMakeLists.txt` (让构建系统找到并链接依赖)**

打开你的包目录下的 `CMakeLists.txt` 文件。你需要做两处修改。

**a) 找到包 (find_package)**:
在 `find_package(ament_cmake REQUIRED)` 之后，添加 `find_package` 命令来查找你的新依赖。

> [!attention]
> **Best Practice**: Always request only the components you need — it speeds up configuration, reduces binary size, and avoids unnecessary dependencies.

**b) 链接库 (ament_target_dependencies)**:
在 `add_executable(...)` 之后，使用 `ament_target_dependencies` 将依赖链接到你的可执行文件上。

**示例**:
```cmake
# my_cpp_pkg/CMakeLists.txt

# ... (省略前面的部分)

# 查找编译所需的依赖包
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
# !! 在这里手动添加，让CMake找到新依赖 !!
find_package(std_msgs REQUIRED) 

# ...

# 添加你的可执行文件
add_executable(my_node src/my_node.cpp)
ament_install_target_dependencies(my_node) # 通常用来处理 install 规则

# 将依赖链接到你的可执行文件
ament_target_dependencies(my_node
  rclcpp
  # !! 在这里手动添加，链接库 !!
)

# ... (省略后面的部分)
```

#### **第 3 步: 安装依赖到系统**

**场景**: 你添加了一个新的依赖，但你的系统里可能还没有安装它。

**命令**:
回到你的工作区根目录 (`~/ros2_ws`)，运行 `rosdep`。这个命令会读取你 `src` 目录下所有包的 `package.xml` 文件，并使用系统包管理器（如 apt）安装缺失的依赖。

```bash
cd ~/ros2_ws

# （首次使用或很久没用时，先更新rosdep数据库）
# sudo rosdep init  (如果从未运行过)
# rosdep update

# 扫描src目录并安装缺失的依赖
rosdep install --from-paths src -y --ignore-src
```
*   `--ignore-src`: 告诉 rosdep 忽略那些源码就在 `src` 目录里的包，只处理外部依赖。


### Ament_cmake

`ament_auto_find_build_dependencies`仅能解析那些在 ament 索引中注册为 ROS 2 包的依赖（即，这些依赖通过 `package.xml`和 `ament_cmake`/`ament_python`导出元数据）。

通过 ROS deb 软件源安装的 Sophus 和 g2o 会像普通的 CMake 包（例如 `libfmt-dev` 等）一样提供 ` Find*.cmake ` 文件，但它们并未将自身注册为 ament 包，因此 ament 索引中没有任何内容可以自动引入。你需要像处理第三方库一样来处理它们，即三板斧。

我们知道引入第三方库需要三板斧：find-include-link，但是还可以精简。

`find_package(OpenCV REQUIRED)` 会引入 Cmake 包导出的目标，例如你在 link 时候写的 `OpenCV::opencv_core`（现代方式）或 `${OpenCV_LIBS}`（传统方式）。

“现代方式”链接时，CMake 会自动引入其 `INTERFACE_INCLUDE_DIRECTORIES` 属性，因此无需手动调用 `include_directories(...)`。

“传统方式”链接时，我们会手动把库加到 `target_link_libraries`，例如使用 `${OpenCV_LIBS}`；这些变量没有附带头文件路径，所以不会触发自动 include。

`ament_target_dependencies` 同样只能对于 ament 包产生效果，它链接了这些 ament 包导出的库。对于非 ament 库，需要使用 `target_link_libraries` 来手动链接他们的目标。

Example

```cmake
cmake_minimum_required(VERSION 3.10)
project(armor_detector)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_compile_options(-Wall -Werror -O3)

## Export compile commands for vscode
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

###########
## Build ##
###########

# 1. 先使用 ament_auto 自动查找 ament 包的依赖
find_package(ament_cmake_auto REQUIRED)
ament_auto_find_build_dependencies()

# 2. 对于不是 ament 包的第三方库，仍需手动查找
find_package(OpenCV REQUIRED)
## include_directories(${OpenCV_INCLUDE_DIRS})
find_package(TBB REQUIRED COMPONENTS tbb)
find_package(Sophus REQUIRED)
find_package(g2o REQUIRED)

# 3. 定义构建目标，这里是导出为动态库
ament_auto_add_library(${PROJECT_NAME} SHARED
  DIRECTORY src
)

# 4. 给目标添加依赖，包括头文件和库
# 4.1 先自动处理依赖的 ament 包的链接
ament_target_dependencies(${PROJECT_NAME})

# 4.2 手动添加非ROS2的第三方库
target_include_directories(${PROJECT_NAME} ${OpenCV_INCLUDE_DIRS})
# 要么不加 target，要么写在定义 target 的后面
target_link_libraries(${PROJECT_NAME}
  ${OpenCV_LIBS}
  fmt::fmt
  TBB::tbb
  Sophus::Sophus
  g2o::core
  g2o::stuff
  g2o::types_slam3d
  g2o::solver_dense
)

# 注册节点
rclcpp_components_register_node(${PROJECT_NAME}
  PLUGIN "artinx::auto_aim::ArmorDetectorNode"
  EXECUTABLE armor_detector_node
)

#############
## Testing ##
#############

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_gtest)
  ament_add_gtest(test_detector test/test_detector.cpp)
  target_link_libraries(test_detector ${PROJECT_NAME})
endif()

#############
## Install ##
#############

# 最后指定安装地址，模型文件也复制过去
ament_auto_package(
  INSTALL_TO_SHARE
  model
)
```

对于完全没有 Cmake 包结构的第三方库：
SDK_PATH -> (target_)include_directories -> target_link_directories


---

## 几种通信手段

话题、服务、参数、动作


USE FOXGLOVE INSTEAD OF RVIZ



## 时间戳

### 关键细节与最佳实践

1. **并非所有消息都自动带有时间戳**
    
    只有那些定义了 `std_msgs/Header`头文件的消息（如 `sensor_msgs/Image`, `sensor_msgs/PointCloud2`等）才会自动包含时间戳。对于 `std_msgs/String`这类基础消息，默认是没有的。如果您自己定义消息类型，并且需要时间同步，务必在其中包含一个 `Header header`字段。
    
2. **时间戳的准确性取决于发布者**
    
    虽然框架提供了自动填充的机制，但时间戳的准确性最终依赖于发布者节点的实现。一个设计良好的传感器驱动节点会在数据采集完成的**硬件中断时刻**或**软件采集瞬间**尽可能准确地记录时间，而不是在数据处理后才填写。
    
3. **如何处理无头文件的消息？**
    
    当您使用 `message_filters`同步那些没有头文件的消息时（例如两个 `std_msgs/Int32`话题），Python版同步器提供了一个变通方案：设置 `allow_headerless=True`。此时，同步器会以**节点接收到消息的当前ROS时间**作为该消息的时间戳进行同步。但这会引入网络延迟，精度不如在源头填充的方式。
    

### 给开发者的建议

- **作为订阅者/同步方**：您可以相信，只要订阅的是标准的传感器话题，其消息头中的时间戳就是发布者自动填充的，可以直接用于同步。
    
- **作为发布者**：当您开发节点产生数据时，**最佳实践是主动、及时地填充时间戳**。在节点的回调函数或数据生成处，使用类似下面的代码：
    
    ```python
    # Python 示例
    msg = sensor_msgs.msg.Image()
    msg.header.stamp = self.get_clock().now().to_msg()  # 获取当前时间并转换为消息格式
    ```
    
    这样做确保了整个系统有一个统一、可靠的时间基准，是多传感器融合算法正确工作的基石。



## 组件

- **典型工作流**：在开发初期，可以**全部使用传统main函数节点**。这便于每个模块独立开发、测试和调试。当系统集成并进行性能剖析时，再**将那些通信频繁、性能关键的节点对或节点组重构为组件**，并放入同一个组件容器中运行。
    
- **利用执行器类型**：ROS 2 提供了不同的组件容器，如单线程的 `component_container`、多线程的 `component_container_mt`。根据组件的特性（如是否有阻塞调用）选择合适的容器，对系统性能和响应性也很重要。


## Foxglove 集成

```
ros-humble-foxglove-bridge/jammy,jammy,now 3.2.2-1jammy.20251229.214525 arm64 [installed]
  ROS Foxglove Bridge

ros-humble-foxglove-bridge-dbgsym/jammy,jammy 3.2.2-1jammy.20251229.214525 arm64
  debug symbols for ros-humble-foxglove-bridge

ros-humble-foxglove-compressed-video-transport/jammy,jammy 3.0.1-1jammy.20251229.125407 arm64
  foxglove_compressed_video_transport provides a plugin to image_transport for transparently sending an image stream encoded in foxglove compressed video packets.

ros-humble-foxglove-compressed-video-transport-dbgsym/jammy,jammy 3.0.1-1jammy.20251229.125407 arm64
  debug symbols for ros-humble-foxglove-compressed-video-transport

ros-humble-foxglove-msgs/jammy,jammy 3.2.2-1jammy.20251219.055750 arm64
  foxglove_msgs provides visualization messages that are supported by Foxglove.

ros-humble-foxglove-msgs-dbgsym/jammy,jammy 3.2.2-1jammy.20251219.055750 arm64
  debug symbols for ros-humble-foxglove-msgs
```

`sudo apt install ros-humble-foxglove-bridge ros-humble-foxglove-compressed-video-transport ros-humble-foxglove-msgs`



## OPENCV + CUDA

```
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_opencv_python2=0 -D BUILD_opencv_python3=1 -D WITH_FFMPEG=1 -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda -D WITH_TBB=ON -D ENABLE_FAST_MATH=1 -D CUDA_FAST_MATH=1 -D WITH_CUBLAS=1 -D WITH_CUDA=ON -D BUILD_opencv_cudacodec=OFF -D WITH_CUDNN=ON -D OPENCV_DNN_CUDA=ON -D CUDA_ARCH_BIN=8.7 -D WITH_V4L=ON -D WITH_QT=OFF -D WITH_OPENGL=ON -D WITH_GSTREAMER=ON -D OPENCV_GENERATE_PKGCONFIG=ON -D OPENCV_PC_FILE_NAME=opencv.pc -D OPENCV_ENABLE_NONFREE=ON -D OPENCV_EXTRA_MODULES_PATH=/usr/src/opencv_contrib-4.8.0/modules -D INSTALL_PYTHON_EXAMPLES=OFF -D INSTALL_C_EXAMPLES=OFF -D BUILD_EXAMPLES=OFF ..
```


## Concurrency

https://roscon.ros.org/2019/talks/roscon2019_concurrency.pdf

https://blog.csdn.net/qq_53044655/article/details/144995702


## 视频发布到 /image_raw

```
ros2 run rm_video_publisher video_file_publisher --ros-args -p video_path:=/home/artinx/rune/redbuff.avi -p topic:=/image_raw -p loop:=true
```

参数不能掉了 `--ros-args`

```
ros2 run rune_detect rune_detector_node --ros-args --log-level INFO
```


## 符解算优化 TODO

**User**:

刚体有六个自由度来描述它的位姿，那一个平面呢？它有 3 个自由度来描述吗？我想要判断空间中一个平面四边形是否在这个平面内，要怎么做？

---
**Assistant**:

平面（作为“无限延伸的几何平面”）在三维空间里确实是 3 个自由度。

**1) 平面有几个自由度？**
- 刚体位姿是 `3(平移)+3(转动)=6` 自由度。
- 一个“几何平面”可以用“单位法向量 + 到原点的有符号距离”表示：
  - 法向量方向：单位向量在球面上是 2 个自由度（例如用俯仰/偏航，或任意参数化）。
  - 距离 `d`：1 个自由度。
  - 合计 3 个自由度。
- 如果你说的是“一个有边界的平面四边形（面片）”本身，那就不是 3 自由度了：它还包含形状/尺寸（边长、角度等）信息；只有当形状固定（比如给定一个刚性矩形面片）时，它作为刚体仍是 6 自由度。

---

**2) 判断空间中的一个平面四边形是否在某个平面内（共面）怎么做？**
设目标平面用法向量 `n`（建议归一化）和常数 `d` 表示：
- 平面方程：`n · x + d = 0`

四边形给你四个顶点 `p1,p2,p3,p4`（3 D 向量）。做法：

**方法 A：点到平面距离（最直接、最常用）**
1. 计算每个顶点的“代入值”  
   `si = n · pi + d`
2. 设容差 `eps`（比如 `1e-6` 到 `1e-4`，取决于你的单位/噪声/数值规模）。
3. 若对所有 i 都满足 `|si| <= eps`，则四边形在平面内（数值意义下共面）。

说明：
- 若 `n` 已归一化，则 `|si|` 就是点到平面的有符号距离；没归一化也能用，但 `eps` 要相应缩放（更推荐把 `n` 归一化）。

**方法 B：用四边形自身算出的平面来比对（当目标平面未知或想自检）**
1. 先用前三个不共线点求四边形的法向：  
   `nq = (p2-p1) × (p3-p1)`
2. 如果 `|nq|` 很小，说明点退化（几乎共线），四边形不成“面”，需要单独处理。
3. 用 `nq` 构造四边形所在平面：  
   `d_q = -nq · p1`
4. 检查第 4 点是否满足：  
   `|(nq · p4 + d_q)| <= eps * |nq|`  
   （这里用 `|nq|` 做尺度归一，避免没单位化带来的阈值问题）

---

**3) 你说“是否在这个平面内”，可能还有第二层意思：在平面上且在平面四边形区域内**
如果你的问题其实是：判断某个点/某个多边形是否落在“这个平面四边形（面片）”覆盖的区域里，那就需要：
- 第一步仍然是“共面”（点到平面距离小于 eps）。
- 第二步做“二维域内判断”：
  - 把点/顶点投影到该平面的 2 D 坐标系（在平面上取两条正交基向量 `u,v`，对任意点用 `x2=dot(p,u), y2=dot(p,v)`）。
  - 再在 2 D 里对四边形做点在多边形内判断（射线法/叉积同向法）；或判断两个多边形的包含/相交关系。

---

**我需要你确认一个细节，才能给你最合适的步骤/代码：**
1) 你要判断的是“一个四边形的 4 个顶点是否共面于给定平面”（只做共面）？  
还是  
2) “它是否落在某个有限的四边形面片区域内部/被包含”（共面 + 区域内）？  

如果你把“平面”的表示方式（点法式：已知平面上一点 `p0` 和法向 `n`；或一般式 `ax+by+cz+d=0`）以及数据尺度（单位、噪声量级）告诉我，我可以顺便帮你选一个合理的 `eps` 和更稳健的实现方式。

---
**User**:

这个四边形面片的位姿是 pnp 解算出来的（在相机坐标系下）我希望找到这个面片所在平面，然后判断下一次识别到的位姿是否还近似落在这个平面内。

---
**Assistant**:

你这个场景里，“平面”更像是一个稳定的约束：第一次 PnP 给出面片位姿（相机系），你从该位姿提取出面片所在的几何平面；之后每次识别到新的位姿，检查它对应的面片是否仍然近似共面。

关键点：PnP 输出的是刚体位姿 `R,t`（把物体坐标点变到相机坐标），而面片平面在“物体坐标系”里是已知的（例如 z=0）。用位姿就能把这个平面变到相机坐标系。

---

**1) 从一次 PnP 位姿求“相机坐标系下的平面”**

假设你的面片模型坐标系这样定义：
- 面片在物体坐标系里是 `Z=0` 的平面
- 该平面的法向（物体系）为 `n_o = [0,0,1]^T`
- 平面上一点（物体系）可取 `p_o0 = [0,0,0]^T`（或任意一个角点）

PnP 给出 `R, t`，使得
- `p_c = R * p_o + t`

那么相机系下：
- 平面法向：`n_c = R * n_o`
- 平面上一点：`p_c0 = R * p_o0 + t`（若 p_o 0=0，则 p_c 0=t）
- 平面方程：`n_c · (x - p_c0) = 0`
  - 展开成 `n_c · x + d = 0`，其中 `d = - n_c · p_c0`

建议把 `n_c` 归一化，并把 `d` 同步缩放。

这一步你只需要第一次“可信”的位姿，就能得到一个参考平面 `(n_ref, d_ref)`（都在相机坐标系）。

---

**2) 用下一次识别到的位姿判断“是否仍落在该平面内”**

有两种常用判据，你可以同时用（更稳）：

A. 位置（平移）是否在平面上  
对新位姿 `R2,t2`，取新面片平面上的一点 `p2_c0`（最简单用 `t2`，对应物体原点）：
- 点到参考平面的有符号距离：
  - `dist = n_ref · p2_c0 + d_ref`
- 通过阈值：`|dist| < eps_dist`

`eps_dist` 取决于你的尺度和噪声，例如：几毫米到几厘米量级（看你的目标大小、PnP 抖动、测量距离）。

B. 姿态是否与平面法向一致（法向是否平行）  
新位姿对应的面片法向：
- `n2 = R2 * n_o`
与参考平面法向的夹角：
- `cosang = clamp(n_ref · n2, -1, 1)`
- `ang = arccos(cosang)`
- 通过阈值：`ang < eps_ang`（例如 1°~5°）

说明：
- 如果面片有“正反”翻转的可能（PnP 偶尔解出法向反向），可以用 `|n_ref · n2|` 来忽略符号：`ang = arccos(|dot|)`。
- 只用距离可能会误判：面片中心落在平面上，但面片已经倾斜了；只用角度也可能误判：法向对了但整片离平面有偏移。所以建议两者都用。

---

**3) 更严格：用“面片四个角点”做共面距离检查**
如果你有模型四个角点 `P_o_i`（物体系，Z=0），用新位姿变到相机系：
- `P_c_i = R2 * P_o_i + t2`
检查每个角点到参考平面的距离：
- `di = n_ref · P_c_i + d_ref`
要求：
- `max_i |di| < eps_dist`

这比只检查 `t2` 更稳，因为能覆盖“中心在平面附近但有倾斜/变形/抖动”的情况。

---

**4) 实操建议（阈值和稳定性）**
- 把参考平面建立在“最可信的一帧”或“多帧平均”上：
  - 多帧时可以对法向做单位向量平均（注意归一化），对 `d` 取平均；或用多帧点云拟合平面（更强）。
- `eps_dist` 经验取法：
  - 先统计一段时间内 `dist` 的标准差 `σ`，用 `3σ` 作为阈值会比拍脑袋稳定。
- 如果相机在动、平面在静：参考平面应在相机坐标系会变（因为相机系在动）。这种情况下你需要把平面表达在“世界系/地图系”，或者每帧用相机位姿把参考平面变换过去。你这里说“PnP 位姿都在相机坐标系下”，通常意味着相机系固定，物体在动；那就没问题。


## 能量机关

正在激活状态的大能量机关转速按照三角函数呈周期性变化。速度目标函数为：spd = a ∗ sin (wt) + b，其中 spd 的单位为 rad/s，t 的单位为 s，a 的取值范围为 0.780~1.045，ω的取值范围为 1.884~2.000，b 始终满足 b=2.090-a。
这一项是保证 spd 非负。

每次开始击打（进入正在激活状态），所有参数重置，其中 t 重置为 0，a 和ω重置为取值范围内任意值。能量机关的实际转速与速度目标函数的时间误差在 500 ms 内。

