---
id: 9c073705-bbdb-4749-8113-7ff7648a8131
title: Windows
tags:
  - 计算机基础
---


## Windows-terminal

修改快捷键，新终端为 ctrl-shift-n，关闭为 ctrl-w。
### 自定义 profile

![[25bc9f3cb8607470.webp]]

只要是在命令行中运行产生新 shell 的命令，就都可以写一个 profile。填在命令行那块儿。例如 mingw、cygwin、conda、ssh、docker run 等等。你可以填这个

```
ssh hyj0824@192.168.1.17
```

## Powershell

### 准备工作

使用 Windows PowerShell 5.0 或 5.1 更新 PSReadLine 通常有两个步骤。首先，您需要确保您运行的是 `1.6.0` 或更高版本的 PowerShellGet。为此，您需要在提升的 Windows PowerShell 会话中运行以下命令。

```powershell
Install-Module -Name PowerShellGet -Force
```

接下来，确保关闭所有 PowerShell 会话，并在提升的 `cmd.exe` 提示符下运行以下代码。这是从 `cmd.exe` 运行的原因是，默认情况下，PSReadLine 已加载，如果在内存中则无法更新。

```powershell
powershell -noprofile -command "Install-Module PSReadLine -Force -SkipPublisherCheck -AllowPrerelease"
```

ref：[在 PowerShell 中使用 PSReadLine](https://cn.linux-console.net/?p=7394)

安装其他必要的 Module

```powershell
Install-Module git-posh
```

### 修改 $profile

```powershell
function runlinux{
	docker run -it --rm -v Files:/root maxxing/compiler-dev bash
}

Import-Module PSReadLine
Set-PSReadlineKeyHandler -Chord Tab -Function MenuComplete
Set-PSReadLineOption -PredictionSource History -PredictionViewStyle ListView
# set Ctrl-D/d
Set-PSReadlineKeyHandler -Chord Ctrl+d,Ctrl+D -Function DeleteLine

# winget 补全参数
Register-ArgumentCompleter -Native -CommandName winget -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
        [Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = [System.Text.Utf8Encoding]::new()
        $Local:word = $wordToComplete.Replace('"', '""')
        $Local:ast = $commandAst.ToString().Replace('"', '""')
        winget complete --word="$Local:word" --commandline "$Local:ast" --position $cursorPosition | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
}
# git 补全参数
Import-Module posh-git
```

### PowerShell 链接

软链接（符号链接）

```
New-Item -ItemType SymbolicLink -Path "新建的符号链接文件或文件夹路径" -Target "源文件或源文件夹"
```

硬链接（仅文件）

```
New-Item -ItemType HardLink -Path "新建的硬链接文件路径" -Target "源文件"
```

## Windows 快速黑屏

`scrnsave.scr`
