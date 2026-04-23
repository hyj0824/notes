---
id: 1fd14cf8-6d28-4f13-9661-b6c4d4fe06a9
title: USB与串口
tags:
  - no-tag
---


USB 转串口常用 CH 430 芯片，该芯片是全速 USB 接口，轮询率为 1000 Hz。USB 是主机轮询，因此不是硬中断。也就是说，我们获取下位机数据的最快速度就是 1 ms 一个包。此时的波特率没有实际意义。

## 如果串口挂了……

使用 `sudo dmesg -w` 查看 USB 接口日志，使用 `sudo udevadm control --reload && sudo udevadm trigger` 刷新设备而不用重启。

```
[ 7558.033539] usb 1-2.4: USB disconnect, device number 90
[ 7561.763358] usb 1-2: reset high-speed USB device number 2 using tegra-xusb
[ 7562.319209] usb 1-2.4: new full-speed USB device number 91 using tegra-xusb
[ 7562.536987] cdc_acm 1-2.4:1.0: ttyACM0: USB ACM device
```

不排除是内核的问题，需要进一步研究。