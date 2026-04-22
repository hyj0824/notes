---
id: bdd0c204-2865-4007-95a7-1ce404060f0b
title: ArtinxHub 环境配置
tags:
  - no-tag
---

# ArtinxHub 环境配置

讲解ArtinxHub的环境配置，以及可能遇到的坑。

建议在 `~/workspace/` 目录下进行配置。默认 `$WORKSPACE=~/workspace`。

0. 安装必要软件包
    ```bash
    sudo apt update
    sudo apt install -y build-essential cmake git vim curl wget unzip flex bison autoconf ninja-build clangd
    ```
1. 克隆vcpkg，并使用git checkout命令签出到版本较老的tag，如2023.01.09。执行bootstrap脚本获取vcpkg。
    ```bash
    cd $WORKSPACE
    git clone https://github.com/microsoft/vcpkg.git
    cd vcpkg
    git checkout 2023.01.09
    ./bootstrap.sh
    ```
2. 用vcpkg安装以下软件包(windows下, 软件包名称后加:x64-windows；opencv4[contrib,ffmpeg], 如用zsh请用""括起来每个软件包)：
    ```bash
    ./vcpkg install nlohmann-json caf glm cpp-httplib fmt magic-enum opencv4[contrib,ffmpeg] opengl eigen3 spdlog ceres
    ```
    如果安装过程中出现错误，可能缺少一些系统依赖。把错误信息发给我也行，不过更推荐问AI分析。最好可以整理一份缺少的依赖软件包列表，后续修改文档。
3. 启用集成
    ```bash
    ./vcpkg integrate install #集成到其他构建系统
    ./vcpkg integrate ${SHELL} #启用shell补全
    ```
4. 安装 HikRobot 相机驱动。注意架构选择！Orin 的 armv8 必须用 aarch64。
    ```bash
    sudo dpkg -i ./MVS-<version>_aarch64_<date>.deb
    ```
5. 克隆 ArtinxHub
    ```bash
    cd $WORKSPACE
    git clone https://mirrors.sustech.edu.cn/git/artinx/artinx-hub.git
    git checkout dev-2026
    ```
6. 通过 SSH 连接小电脑。可以直接用 type-c 口连接，通过 `192.168.55.1` 连接到 Orin。然后 VSCode Remote-SSH 打开 $WORKSPACE/artinx-hub 目录。
7. 参考 `docs/vscode_tutorial/vscode_tutorial.md`，了解 VSCode 配置 C++ 开发环境的原理。正如描述的，建议大家禁用默认的 IntelliSense 语言服务器，换成 clangd 作为语言服务器。我们在前面已经安装了 clangd，所以直接在 VSCode 中安装 clangd 插件即可。
8. 参考 `docs/vscode_tutorial/*.json` 配置自己的 VSCode。如果使用 clangd 的话，`c_cpp_properties.json` 就不需要了，但要配置 `settings.json` 禁用掉 IntelliSense。
9. 不出意外的话，现在就可以使用 VSCode 直接编译运行了。然后生成 `compile_commands.json` 以后，应该能正确识别头文件了。
10. 要读写串口，需要配置串口通讯免Root
    ```bash
    sudo usermod -aG dialout artinx
    ```
    其他临时解决办法: `sudo chmod 777 /dev/<your_serial_port>`

最后，希望大家积极反馈遇到的问题，或者提交PR帮助修缮老文档。任何文档的配置说明都可能存在不准确，大家仅供参考。谢谢！

## 附加任务

帮我测试分支 `draft` 是否能正常编译运行，看看有没有什么问题。谢谢！ 