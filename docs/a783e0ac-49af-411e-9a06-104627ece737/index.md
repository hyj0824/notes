---
id: a783e0ac-49af-411e-9a06-104627ece737
title: Jetson Orin 教程
tags:
  - no-tag
---

# Jetson Orin 教程

Jetson Orin NX 是异构计算平台，其arm的架构决定了不能像x86平台一样直接安装Ubuntu系统、随意升级。

## 1. 系统安装

一般arm开发板，核心板和载板厂商都会给一个配套的板级支持包（BSP），里面是定制的Linux系统和烧录工具。

英伟达给Jetson提供了一个全家桶JetPack SDK，里面包含了系统镜像、烧录工具、驱动、CUDA、TensorRT等。在[这里](https://developer.nvidia.com/embedded/jetpack-archive)查看最新版本情况。

我们刷系统，就需要其中的 Jetson Linux SDK，建议使用从[这里](https://developer.nvidia.com/embedded/jetson-linux-archive)获取最新版本。

以 [Jetson Linux 36.5.0](https://developer.nvidia.com/embedded/jetson-linux-r365) 为例，具体安装步骤可以查看官网的[安装指南](https://docs.nvidia.com/jetson/archives/r36.5/DeveloperGuide/IN/QuickStart.html#to-flash-the-jetson-developer-kit-operating-software)。

大致流程就是，下载解压 BSP 和 Sample Root Filesystem，先运行厂商提供的配置环境的脚本（不用每次刷板子都跑，只需要运行过一次即可）

然后让板子进入刷机模式，lsusb 此时会有个 NVIDIA APX 的设备，Orin风扇不会转。此时执行烧录命令。

注意，宿主机必须是 Ubuntu 22.04，而且wsl是不行的，要么使用物理机，要么使用VMware。

> 注：Jetson Orin Nano 的烧写命令与 Jetson Orin NX 是一样的。

## 2. 系统开荒

刷完系统后，主要需要更换设备树、调整风扇转速、更换软件源、安装Intel网卡驱动以及安装JetPack SDK。建议不要在欢迎界面安装 chromium。

### 2.1 网卡问题

英特尔的无线网卡需要额外安装驱动。没有网络可以使用 USB 手机共享热点等方式临时联网，安装完成后再切换回无线网卡。（当然也可以把驱动包写到rootfs里，刷系统的时候就一起刷了）

```bash
sudo apt install -y iwlwifi-modules
```

不可以开机快速找到网卡，需要等待一些时间。有条件最好还是使用免驱网卡！

### 2.2 一键脚本

下面这份脚本已经整理好，请先确保网络正常连接。脚本执行结束后会自动重启。

```bash
#!/usr/bin/env bash
set -euo pipefail

# Jetson Orin post-flash one-click setup script.
# Run this script as root.

log() {
	echo "[INFO] $*"
}

if [[ "${EUID}" -ne 0 ]]; then
	echo "[ERROR] Please run as root: sudo bash $0" >&2
	exit 1
fi

log "Step 1/7: Replace ubuntu-ports with SUSTech mirror."
sed -i 's|http://ports.ubuntu.com|https://mirrors.sustech.edu.cn|g' /etc/apt/sources.list
apt update

log "Step 2/7: Hold snapd to avoid incompatible upgrades."
snap download snapd --revision=24724
snap ack snapd_24724.assert
snap install snapd_24724.snap
snap refresh --hold snapd

# 实测安装 chrome 会有问题，暂不安装。
# log "Step 3/7: Install chromium-browser."
# apt install -y chromium-browser

log "Step 4/7: Install JetPack and jtop."
apt install -y nvidia-jetpack python3-pip
python3 -m pip install -U jetson-stats

log "Writing /etc/profile.d/nvidia-jetpack.sh, creating CUDA_HOME and updating PATH..."
cat >/etc/profile.d/nvidia-jetpack.sh <<'EOF'
export CUDA_HOME=/usr/local/cuda # Not strictly necessary, but ArtinxHub needs it.
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64\
                         ${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
EOF
chmod 0644 /etc/profile.d/nvidia-jetpack.sh

log "Step 5/7: Force fan to full speed via systemd service."
cat >/usr/lib/systemd/system/full_fan_speed.service <<'EOF'
[Unit]
Description=Force Jetson Fan to 100%
After=nvpmodel.service nvfancontrol.service basic.target

[Service]
ExecStartPre=/usr/bin/systemctl stop nvfancontrol
ExecStart=/usr/bin/jetson_clocks --fan
Type=oneshot
RemainAfterExit=true
Restart=on-failure
RestartSec=2s
TimeoutStartSec=30s
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable full_fan_speed.service
systemctl start full_fan_speed.service

log "6/7: Set power mode to MAXN via nvpmodel."
nvpmodel -m 0

log "7/7: Remove brltty to avoid potential issues with serial console."
apt remove -y brltty

log "Done."
log "Will reboot in 10s...Press any key to reboot immediately."

read -n 1 -s -r -t 10
reboot
```

将上述脚本整体复制执行（需 root 权限）即可。

### 2.3 更换设备树

如果你有 `.dtb` 文件，可以直接跳到“使设备树生效”部分。

设备树是嵌入式设备（因为没有完整ACPI支持）用来描述硬件信息的数据结构，设备树文件一般位于 `/boot/dtb/` 目录下。根据不同的载板需要更换不同的设备树文件，具体可以参考厂商提供的文档。设备树文件 `.dtb` 是编译后的二进制文件，无法直接修改，我们需要修改 `.dts` 源码并编译。

#### 步骤概述

以达妙的载板为例，我们要修改设备树就需要先下载英伟达官方载板的设备树文件，在其基础上修改。你也可以直接反编译当前系统的设备树文件，修改后再编译回去（但是只建议用于临时测试）

参考[这篇文章](https://docs.nvidia.com/jetson/archives/r36.5/DeveloperGuide/SD/Kernel/KernelCustomization.html#to-manually-download-and-expand-the-kernel-sources)定制内核的步骤：

先解压内核源码+OOT模块源码+显示驱动源码，然后安装一些依赖，比如 build-essential bison flex 等等。不过实际上我们不需要全部编译。照着上面的步骤到 `make -C kernel` 即可。

这是因为我们不想用宿主系统自带的 `dtc`，所以编译一下内核就行，不用编译模块了。

然后进行修改，[这篇文章](https://docs.nvidia.com/jetson/archives/r36.5/DeveloperGuide/HR/JetsonModuleAdaptationAndBringUp/JetsonOrinNxNanoSeries.html#porting-the-linux-kernel-device-tree)告诉我们，英伟达会在内核树里的 `.dts` 上再叠一层，这一层在 `nv-platform` 这个文件夹里。

找到 `Linux_for_Tegra/source/hardware/nvidia/t23x/nv-public/nv-platform`，这里就是实际编译的 `.dts` 文件。我们的载板修改 `tegra234-p3768-0000+p3767-0000-nv-super.dts` 即可。

```dts
// SPDX-License-Identifier: GPL-2.0
// SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

/dts-v1/;

#include "tegra234-p3768-0000+p3767-0000-nv.dts"

/ {
	compatible = "nvidia,p3768-0000+p3767-0000-super", "nvidia,p3767-0000", "nvidia,tegra234";
	model = "NVIDIA Jetson Orin NX Engineering Reference Developer Kit Super";

	aliases {
		serial3 = "/bus@0/serial@3110000";
	};

	bus@0 {
		serial@3110000 {/* Enable UART1 */
			compatible = "nvidia,tegra194-hsuart";
			reset-names = "serial";
			status = "okay";
		};

		padctl@3520000 {
			pads {
				usb3 {
					lanes {
						/* 添加USB2物理层（PHY）的 lane 配置*/
						usb3-2 {		// 第三个 USB 3.0 通道
							nvidia,function = "xusb";
							status = "okay";
						};
					};
				};
			};

			ports {
				/* 添加usb3-2部分使能 USB3.0*/
				usb3-2 {
					nvidia,usb2-companion = <2>;		// "2"为配对标识符 表示：usb3-2 通道与 usb2-2 通道配对
					status = "okay";
				};
			};
		};

		usb@3610000 {
			status = "okay";

			phys = <&{/bus@0/padctl@3520000/pads/usb2/lanes/usb2-0}>,
				   <&{/bus@0/padctl@3520000/pads/usb2/lanes/usb2-1}>,
				   <&{/bus@0/padctl@3520000/pads/usb2/lanes/usb2-2}>,
				   <&{/bus@0/padctl@3520000/pads/usb3/lanes/usb3-0}>,
				   <&{/bus@0/padctl@3520000/pads/usb3/lanes/usb3-1}>,
				   <&{/bus@0/padctl@3520000/pads/usb3/lanes/usb3-2}>;
				   //添加这一行将将 usb3-2 挂载到 usb3.0 总线上
			phy-names = "usb2-0", "usb2-1", "usb2-2", "usb3-0", "usb3-1", "usb3-2";
			// 添加 usb3-2 将usb3-2 在总线上标记为 usb3-2 供驱动内部使用
		};
	};

};
```

设备树的 `#include` 和 c/cpp 很像，是直接插入，而且设备树后面写的配置会覆盖前面写的配置，所以我们在 `tegra234-p3768-0000+p3767-0000-nv.dts` 的基础上修改，这个比较像 yaml，删除节点/字段有一套特殊规则，这里先不提。我们只添加需要覆写的配置即可。随后按照 Building the DTBs 的步骤生成 `.dtb` 文件。

我们可以在 `Linux_for_Tegra/source/kernel-devicetree/generic-dts/dtbs` 目录下找到生成的 `.dtb` 文件。本例中是 `tegra234-p3768-0000+p3767-0000-nv-super.dtb`。直接复制到 `/boot/dtb/` 目录下。

#### 使设备树生效

把 `.dtb` 文件复制到对应目录后，还需要在 Jetson Orin 板卡的 `/boot/extlinux/extlinux.conf` 中添加如下内容：
```text
TIMEOUT 30
DEFAULT primary

MENU TITLE L4T boot options

LABEL primary
      MENU LABEL primary kernel
      # 增加下面FDT这行，指定对应的dtb文件，文件名称根据你实际情况修改
      FDT /boot/dtb/tegra234-p3768-0000+p3767-0000-nv-super.dtb
      LINUX /boot/Image
      INITRD /boot/initrd
      ......
```

完成上述操作后重启Jetson Orin板卡，检查设备树是否生效。可以在命令行中检查 `lsusb -t` 的输出结果，以及查看 `ls /dev/ttyTHS*` 是否有三个串口设备。

## 3. 其他知识

+ 把网口设置成静态IP，方便SSH连接。
+ 直接使用 type-c 口连接，Orin 会自动生成一个网卡，你的电脑直接通过 `192.168.55.1` 连接到 Orin。
