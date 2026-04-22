---
id: 0f19ddc0-a12f-4111-8612-3a20f15cb17a
title: Linux and Shell
tags:
  - Linux
  - 计算机基础
---

## 阅读资料

https://zhuanlan.zhihu.com/p/102176365

https://www.runoob.com/linux/linux-shell.html

仅仅复制粘贴我不熟悉（反直觉）的 case。

## Shell vars

```
等号两侧避免使用空格：
# 正确的赋值
variable_name=value

# 有可能会导致错误
variable_name = value
```

```
除了显式地直接赋值，还可以用语句给变量赋值，如：

for file in `ls /etc`  
或  
for file in $(ls /etc)

避免使用反引号（老语法）
```

使用变量值要加$，赋值不需要加。
推荐给所有变量加上花括号，避免解释器混淆。

```bash
myUrl="https://www.google.com"
readonly myUrl
myUrl="https://www.runoob.com"
# /bin/sh: NAME: This variable is read only.
```

使用 `unset variable_name` 可以删除变量。变量被删除后不能再次使用（即没有值）。unset 命令不能删除只读变量。

你可以使用单引号 ' 或双引号 " 来定义字符串。Like python。



## Parameters

| =变量           | 含义                    |
| ------------- | --------------------- |
| `$1`          | 函数或脚本的​**​第一个参数​**​   |
| `$0`          | 脚本本身的名称               |
| `$2`, `$3`... | 函数或脚本的第二、第三个参数        |
| `$#`          | 传递给函数或脚本的​**​参数个数​**​ |
| `$@`          | 所有的参数列表               |
>[!attention] 脚本参数 vs. 函数参数
>​​脚本参数​​：在​​脚本主体​​中使用的 $1、$2等，指的是执行脚本时通过命令行传递给脚本的参数。
>函数参数​​：在​​函数内部​​使用的 $1、$2等，指的是在调用函数时传递给该函数的参数。
>函数内部的 $1会屏蔽脚本主体中的 $1。

- 使用 ​**​`"$1"`​**​ 并用双引号括起来是个好习惯。防止当参数中包含空格或特殊字符时，被Shell错误解析.
- **第十个及以后的参数​**​：获取第十个及以后的参数时，不能写成 `$10`，而必须使用 ​**​`${10}`​**
- 一个良好的习惯是检查参数是否提供。在忘记输入参数时给出提示：

```bash
chk() {
    if [ $# -eq 0 ]; then
        echo "Please input a parameter"
        return 1
    elif [$1 -eq 1]
    then
	    echo "equals to 1"
	else
		echo "not equals to 1"
    fi
}

# use `source ${file}`
# function calling
mdc
mdc 12
```

- **整数比较**：
    - `-eq` : 等于（equal）
    - `-ne` : 不等于（not equal）
    - `-gt` : 大于（greater than）
    - `-lt` : 小于（less than）
    - `-ge` : 大于或等于（greater than or equal）
    - `-le` : 小于或等于（less than or equal）
- **字符串比较**：
    - `=`, `==` : 等于
    - `!=` : 不等于
    - `<`, `>` : 比较字符串的字典序（需使用 `[[ ... ]]`）
- **文件测试**：
    - `-e` : 文件存在
    - `-f` : 普通文件存在
    - `-d` : 目录存在
    - `-r` : 文件可读
    - `-w` : 文件可写
    - `-x` : 文件可执行

## 查看命令运行时间

为了容易地完成测量，可以将命令包装在 **time** 命令中，就像这样：**`time { ../configure ... && make && make install; }`**。

1 SBU

Real    1 m 23.843 s
User    3 m 5.491 s
Sys     1 m 4.481 s

Real 并不等于 user+sys 的总和。Real 代表的是程序从开始到结束的全部时间，即使程序不占 CPU 也统计时间。而 user+sys 是程序占用 CPU 的总时间，因此 real 总是大于或者等于 user+sys 的（单核）。

## Linux 系统代理

```bash
sudo vim /etc/profile.d/proxy.sh

 # set proxy config via profile.d - should apply for all users
export http_proxy="http://10.10.1.10:8080/"
export https_proxy="http://10.10.1.10:8080/"
export ftp_proxy="http://10.10.1.10:8080/"
export no_proxy="127.0.0.1,localhost"
# For curl
export HTTP_PROXY="http://10.10.1.10:8080/"
export HTTPS_PROXY="http://10.10.1.10:8080/"
export FTP_PROXY="http://10.10.1.10:8080/"
export NO_PROXY="127.0.0.1,localhost"
#将要从代理中排除的其他IP添加到NO_PROXY和no_proxy环境变量中

sudo chmod +x /etc/profile.d/proxy.sh
```

[【ubuntu】系统代理的设置\_ubuntu network proxy-CSDN博客](https://blog.csdn.net/u011119817/article/details/110856212)