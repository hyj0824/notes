---
title: 单目相机的坐标转换与PnP解算
id: b9b1aa97-c0ef-4f3e-b7ef-bd93825b9ac0
tags:
  - 计算机视觉
  - pnp
  - opencv
  - robotics
---


https://www.lisii.cn/pdfs/pnpsolve.pdf

**作者**: Lisii  
**日期**: September 27, 2023

---

## 1. 坐标变换

### 1.1 世界坐标系到相机坐标系

相机在世界中的位姿通过旋转矩阵 **R** 和平移向量 **t** 表示。由线性代数知识可以知道二维旋转矩阵，我们把旋转分解到三个轴上，用旋转矩阵 **R** 描述沿 x、y、z 轴的旋转：

- 沿 z 轴旋转（z 值不变）：
  $$
  \begin{pmatrix} x_{\text{cam}} \\ y_{\text{cam}} \\ z_{\text{cam}} \end{pmatrix} = \begin{pmatrix} \cos\beta & -\sin\beta & 0 \\ \sin\beta & \cos\beta & 0 \\ 0 & 0 & 1 \end{pmatrix} \cdot \begin{pmatrix} x_{\text{world}} \\ y_{\text{world}} \\ z_{\text{world}} \end{pmatrix}
  $$
- 沿 x 轴旋转：
  $$
  \begin{pmatrix} x_{\text{cam}} \\ y_{\text{cam}} \\ z_{\text{cam}} \end{pmatrix} = \begin{pmatrix} 1 & 0 & 0 \\ 0 & \cos\beta & \sin\beta \\ 0 & -\sin\beta & \cos\beta \end{pmatrix} \begin{pmatrix} x_{\text{world}} \\ y_{\text{world}} \\ z_{\text{world}} \end{pmatrix}
  $$
- 沿 y 轴旋转：
  $$
  \begin{pmatrix} x_{\text{cam}} \\ y_{\text{cam}} \\ z_{\text{cam}} \end{pmatrix} = \begin{pmatrix} \cos\gamma & 0 & -\sin\gamma \\ 0 & 1 & 0 \\ \sin\gamma & 0 & \cos\gamma \end{pmatrix} \begin{pmatrix} x_{\text{world}} \\ y_{\text{world}} \\ z_{\text{world}} \end{pmatrix}
  $$

三个旋转矩阵相乘就得到了旋转矩阵 **R**，叠加平移向量 **t**，世界坐标系到相机坐标系的变换为：
$$
\begin{pmatrix} x_{\text{cam}} \\ y_{\text{cam}} \\ z_{\text{cam}} \end{pmatrix} = R \cdot \begin{pmatrix} x_{\text{world}} \\ y_{\text{world}} \\ z_{\text{world}} \end{pmatrix} + \begin{pmatrix} T_x \\ T_y \\ T_z \end{pmatrix}
$$

![[rotation.webp]]

### 1.2 图像坐标系到像素坐标系

普通相机的成像模型采用小孔成像，初中的物理知识告诉我们，物体经小孔后，在成像平面
上下相反、左右颠倒。为了计算便利，引入了虚拟成像平面模型（如图）。

在这个标准约定中：相机坐标系的 Z 轴（光轴）正向是从光心指向相机前方。将物理上位于光心后方的倒立实像，对称地“投影”到光轴正方向的虚拟成像平面上，避免了在公式中处理负号，简化了坐标变换的数学表达。

然后将根据简单的相似三角形几何知识，可以推出 3D 目标点在相机坐标系下的坐标与图像像素坐标之间的关系：

![[camera.webp]]

如图，标出的点 **X** 在相机坐标系下表示为 $(X, Y, Z)$ 投影到图像坐标 $(u, v)$：
$$
\begin{cases} u = f \cdot \frac{X}{Z} \\ v = f \cdot \frac{Y}{Z} \end{cases}
$$
其中 $f$ 为焦距。而从图像坐标系中心点到像素坐标系中心点还有一个偏移量，这属于相机内参的一部分。如果我们已知图像坐标系的一个点，我们还应该知道，横坐标的每毫米对应像素是多少。像素坐标系的原点偏移 $(u_0, v_0)$ 和像素尺寸 $(dx, dy)$，即有如下公式：$p(u, v) = p(\frac{x}{dx+u_0}, \frac{y}{dy+v_0})$，齐次坐标形式为：
$$
Z \begin{pmatrix} u \\ v \\ 1 \end{pmatrix} = \begin{pmatrix} f_x & 0 & u_0 & 0 \\ 0 & f_y & v_0 & 0 \\ 0 & 0 & 1 & 0 \end{pmatrix} \begin{pmatrix} X \\ Y \\ Z \\ 1 \end{pmatrix}
$$
这里 $f_x = \frac{f}{dx}$, $f_y = \frac{f}{dy}$ 为归一化焦距。

### 1.3 世界坐标系到像素坐标系

结合外参（旋转和平移）和内参，世界坐标系到像素坐标系的完整变换为：
$$
Z \begin{pmatrix} u \\ v \\ 1 \end{pmatrix} = \begin{pmatrix} f_x & 0 & u_0 & 0 \\ 0 & f_y & v_0 & 0 \\ 0 & 0 & 1 & 0 \end{pmatrix} \begin{pmatrix} R & t \\ 0^T & 1 \end{pmatrix} \begin{pmatrix} X_{\text{world}} \\ Y_{\text{world}} \\ Z_{\text{world}} \\ 1 \end{pmatrix}
$$
其中：
- 内参矩阵 $K_1 = \begin{pmatrix} f_x & 0 & u_0 \\ 0 & f_y & v_0 \\ 0 & 0 & 1 \end{pmatrix}$
- 外参矩阵 $K_2 = \begin{pmatrix} R & t \\ 0^T & 1 \end{pmatrix}$

### 1.4 像素坐标系到世界坐标系

逆变换通过求解深度 $Z_c$ 和外参逆矩阵实现：
$$
\begin{pmatrix} X_{\text{world}} \\ Y_{\text{world}} \\ Z_{\text{world}} \\ 1 \end{pmatrix} = Z_c \cdot K_2^{-1} \cdot K_1^{-1} \cdot \begin{pmatrix} u \\ v \\ 1 \end{pmatrix}
$$
需额外深度信息（如双目相机或激光雷达）才能完整还原。

---

## 2. PnP解算

PnP（Perspective-n-Point）用于估计相机位姿：已知 3D 点（世界坐标系）和对应 2D 像素点，求解相机外参（旋转矩阵 **R** 和平移向量 **t**）。

### 2.1 OpenCV-PnPSolver

OpenCV 提供以下函数：
- **solvePnP**：
  ```cpp
  bool solvePnP(InputArray objectPoints, InputArray imagePoints,
                InputArray cameraMatrix, InputArray distCoeffs,
                OutputArray rvec, OutputArray tvec,
                bool useExtrinsicGuess = false, int flags = SOLVEPNP_ITERATIVE);
  ```
- **solvePnPRansac**：使用 RANSAC 剔除异常点，参数类似。

**使用步骤**：
1. 准备输入：
   - `objectPoints`：世界坐标系下的 3D 点坐标（至少 4 点）。
   - `imagePoints`：对应图像像素坐标。
   - `cameraMatrix`：相机内参矩阵（3×3）。
   - `distCoeffs`：畸变系数（如无畸变，设为零矩阵）。
2. 调用函数输出 `rvec`（旋转向量）和 `tvec`（平移向量）。
3. 将旋转向量转换为旋转矩阵（使用 `Rodrigues` 函数），组合位姿矩阵：
   ```cpp
   Mat wldToCam = Mat::zeros(4, 4, CV_64FC1);
   Rodrigues(rvec, wldToCam(Rect(0, 0, 3, 3))); // 旋转部分
   tvec.copyTo(wldToCam(Rect(3, 0, 1, 3)));     // 平移部分
   ```
4. 求相机在世界坐标系中的位姿：`Mat camToWld = wldToCam.inv();`

---

## 3. 深度信息的获取

从 2D 像素坐标还原 3D 世界坐标需深度信息 $Z_c$，可通过以下方式获取：
- 双目相机（视差计算深度）。
- 激光雷达（直接测距）。
- 其他传感器（如结构光或飞行时间相机）。

> [!note] 注意
> 注：单目相机本身无法提供深度，需借助外部手段或假设。

