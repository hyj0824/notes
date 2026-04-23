---
id: 857edcf1-49ba-41d9-a9e6-d2d65ed32e46
title: 字符编码与字节流
tags:
  - meta
---


众所周知，Java 的 `char` 是 16 位无符号整数，语义上是一个 UTF-16 码元。这是历史包袱，因为最初设计者认为 UTF-16 可以表示所有字符，一个 `char` 恰好代表了一个字符，多么优雅。但是随着码点的扩充，有的字符在 UTF-16 下必须使用代理对（两个 `char`）来表示，这会带来一些问题。

```java
public class Main {
    public static void main(String[] args) {
        String name = "你😡";
        System.out.println(name.length());
        // 会输出 3
        // 说明 length() 返回的是 UTF-16 码元数量，而不是 Unicode 码点数量
        // 这里 "你" 是一个 Unicode 字符，占用一个 char
        // 而 "😡" 是一个 Unicode 字符，但占用两个 char
        // 因为它的 Unicode 编码超过了 U+FFFF

        for (int i = 0; i < name.length(); i++) {
            System.out.print(name.charAt(i) + " ");
        }
        System.out.println();
        // 用空格截断每个 char，会把代理对拆开，出现乱码

        for (int i = 0; i < name.codePointCount(0, name.length()); i++) {
            int codePoint = name.codePointAt(name.offsetByCodePoints(0, i));
            // 得到码点，也就是一个文字符号的 Unicode 编码
            System.out.print(Character.toString(codePoint) + " ");
        }
        System.out.println();
        // 按 Unicode 码点遍历，能正确分割两个字符

        for (int i = 0; i < name.length(); i++) {
            System.out.print(name.charAt(i));
            System.out.flush();
            // sleep 1000ms
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                break;
            }
        }
        System.out.println();
        // 刷新缓冲区在我这里不会乱码

        System.out.println(name);
    }
}
```

但是 C++ 就非常复杂了。`string/u8string/u16string/u32string/wstring` 到底怎么选择？它们的区别主要在于存储单元的大小，以及对“编码”的语义约定。

一般来说，`string` 就是普通字节序列，没有指定任何编码。字符串字面量会经历“源字符集”到“执行字符集”的转换，具体结果与编译器、编译选项以及平台相关。如果你的源代码以 UTF-8 保存，但程序在 Windows CMD 这种 GBK 代码页的终端上输出 UTF-8 字节流，就会导致乱码。

在 Windows 上，常见的控制点有三层：

- 源文件编码：建议统一 UTF-8 保存。
- 编译器选项：如 MSVC 的 `/utf-8`（设定源文件与执行字符集均为 UTF-8），或 `/execution-charset:utf-8`；GCC/Clang 可用 `-finput-charset=utf-8` 与 `-fexec-charset=utf-8`。
- 终端代码页：CMD/PowerShell 需要切到 UTF-8（如 `chcp 65001`），否则输出的 UTF-8 字节仍会被按 GBK 解码。Windows Terminal 通常默认 UTF-8，问题会少一些。

你也可以考虑使用字面量去指定编码，但仍要注意输出端的编码约定。因为 UTF-8/16/32 是不同的编码，如果你的终端使用 UTF-8 解码，直接输出 UTF-16/32 的字节流肯定会乱码，必须先转换再输出。

另外，`<codecvt>` 在 C++17 起已弃用，示例仅用于理解概念。生产环境可考虑 ICU、Boost.Locale 或平台 API 来做编码转换。

```cpp
#include <string>
#include <iostream>
#include <codecvt> // 已经弃用，仅实验参考
#include <locale>

namespace {
std::string to_utf8(const std::u16string& s) {
    std::wstring_convert<std::codecvt_utf8_utf16<char16_t>, char16_t> conv;
    return conv.to_bytes(s);
}

std::string to_utf8(const std::u8string& s) {
    return std::string(reinterpret_cast<const char*>(s.data()), s.size());
}

std::string to_utf8(const std::u32string& s) {
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
    return conv.to_bytes(s);
}

std::string to_utf8(const std::wstring& s) {
    std::wstring_convert<std::codecvt_utf8<wchar_t>, wchar_t> conv;
    return conv.to_bytes(s);
}
}

int main() {
    std::string s1 = "你好，世界"; // 依赖编解码设置，普通 char 8位
    std::u8string s2 = u8"你好，世界"; // 8 位
    std::u16string s3 = u"你好，世界"; // 16 位
    std::u32string s4 = U"你好，世界"; // 32 位
    std::wstring s5 = L"你好，世界";
    // wchar_t 大小取决于平台，在 Windows 上通常是 16 位，在 Linux 上通常是 32 位

    // 输出 utf8 编码，因为我的终端是这个格式
    std::cout << "s1: " << s1 << std::endl;
    std::cout << "s2: " << to_utf8(s2) << std::endl;
    std::cout << "s3: " << to_utf8(s3) << std::endl;
    std::cout << "s4: " << to_utf8(s4) << std::endl;
    std::cout << "s5: " << to_utf8(s5) << std::endl;

    return 0;
}
```
