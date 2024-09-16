---
id: 0334ebcc-7d92-4434-a8b9-2d0a33658598
title: Git简介
tags:
  - git
---


推荐使用：

- [Sourcetree | Free Git GUI for Mac and Windows](https://www.sourcetreeapp.com/)
- [Visualizing Git](https://git-school.github.io/visualizing-git/)

## 基本概念及操作

Git 的备份节点（commit）在底层构成一张 DAG，产生的新 commit 会指向**执行命令前**所在的 commit（例如：merge 节点有多个前继，指向的是 merge 前的 commit）因此，每个仓库仅有一个汇点——inital commit。

分支、HEAD、Tag 仅仅是指向它们的指针，指针变动（甚至删除）并不会改变它们指向的节点，而只会导致你无法通过上述的**单向**指向关系找到原来的节点，即产生了 `unreachable` 的节点（类似 memory leak）这些 `unreachable` 节点及其相关文件会定期被 git 清理掉，也就是GC。

### 备份与还原

- Add 告诉 git 能管理哪些文件、记录哪些文件的变动（create/delete/modify）
- Add 会将修改先同步暂存区，暂存区可以理解为一个准备提交的 commit
- Commit 就是确认暂存区的修改，命名并创建备份点
- Push 修改远程，改动历史时 push 要加-f
- `git log --oneline` 查看 commit 链

```bash
# 更新已经追踪的文件，未追踪要add
# git add .
git commit -a
git push

# 前跳一次 reset默认的mixed就很好用
git reset HEAD^

# reset错了返回未来 用reflog查HEAD的移动记录
git reflog
git reset <commit>

# 仅恢复某个文件/目录
git checkout <commit> <path>
```

### Checkout

[当使用git checkout命令时，Git会切换到指定的分支，但如果后面接的是文件名或路径，Git则不会切换分支，而是把文件从.git目录中复制一份覆盖到当前的工作目录。](../assets/58561_Git从入门到精通_高见龙.pdf#page=72&selection=63,6,73,16)与 reset --mixed 相反，它不会修改暂存区，只会修改工作区。

```bash
# 移动HEAD
git checkout test
git checkout <commit>

# 不移动HEAD
git checkout . # 从暂存区覆盖工作区
git checkout HEAD~2 <path> # 拿两个版本前的文件覆盖
```

### 切换新任务

暂存区并不能存下你手边的任务！它不固定在原来所在的 commit 上。Checkout 切换前请任选：

1. 直接 commit
2. 用 stash

### 合并分支

分支合并的两种方式，所有合并操作都是别的 commit 合并入 HEAD，且都不会对别的分支产生影响。

```bash
# 1.merge多个commit
# 注：pull底层就是把origin/x合并到x
git checkout main
git merge test new
# 解决冲突
git commit -a

# 2.rebase 把从lca开始的修改叠加到某一个commit上
git rebase test
# 解决冲突
git add .
git rebase --continue
```

### 其他

```shell
# author email
git config --global user.name "hyj0824"
git config --global user.email "2417179808@qq.com"

# commit图
git log --oneline --graph

# rm + git add：删除文件并stage
git rm *

# 取消文件追踪不删除文件 make it untracked
git rm --cached *
git restore --staged *

# reset HEAD^1后再做一次commit，也就是修改最新commit
git commit --amend -m "xxx"
git commit --amend --no-edit # 不修改message
git commit --allow-empty -m "a" # 空commit

# 记录变动并合并到最新commit
git commit -a --amend --no-edit

# 删除远端分支
git push origin :new

# cherry-pick 仅拉取特定的commit内容，而不是从lca开始的全部commit
git cherry-pick "sha1" "sha2"

# 立刻 gc
git fsck --unreachable
git reflog expire --all --expire=now
git gc --prune=now

# 路径显示中文
git config --global core.quotepath false
```

## 修改代理

```bash
git config --global http.proxy socks5://127.0.0.1:20170
git config --global https.proxy socks5://127.0.0.1:1080

git config --global http.proxy http://127.0.0.1:20171
git config --global https.proxy https://127.0.0.1:8080

git config --global --unset http.proxy
git config --global --unset https.proxy

git config -l --global
```

## Rebase

合并可以用 `git rebase <base commit>`，不仅仅可以合并分支，还可以合并 commit。

> [!note] [Rebase的过程大概是这样的](../assets/58561_Git从入门到精通_高见龙.pdf#page=152&selection=16,8,18,9)
> 1. **确定公共祖先**：当前 commit 与 base commit 的 lca。
> 2. **取出更改**：取出当前 commit 从公共祖先开始的所有提交。
> 3. **应用更改**：将这些提交更改依次接续到 base commit 后方。

在 `rebase` 过程中，如果出现冲突，Git 会停止并允许你手动解决这些冲突。解决冲突后，你需要使用 `git add` 将更改加入暂存区，然后使用 `git rebase --continue` 命令继续 `rebase` 过程。

`rebase` 操作的好处是可以将项目的历史变得更加清晰，因为它避免了不必要的合并提交，使得项目的历史看起来像是一条直线。这对于查看项目的历史和维护项目非常有用。

更精细化的修改需要使用 `git rebase -i` 的交互式操作，它允许你指定从公共祖先开始的每个提交分别采取怎样的操作：

1. **pick**：这是默认操作，即按照原来的顺序将 lca 链上的提交依次应用到 base commit 后方。
2. **reword**：修改某个提交的消息，这会在应用该提交之前暂停变基过程，允许你编辑提交消息。
3. **squash**：将提交合并到前一个提交中，并让你给合并后的提交提供一个新的提交消息。
4. **fixup**：将提交合并到前一个提交中，沿用前一个提交的消息。
5. **edit**：对某个提交进行修改、添加新的 commit 或修复错误。这会暂停变基过程，允许你进行所需的更改，然后继续变基。
6. **drop**：这个选项用于删除某个提交。如果你不再需要某个提交，可以将其行的 `pick` 改为 `drop`。

> [!note] [单次Commit的文件太多了，可能会想把它拆解得更细](../assets/58561_Git从入门到精通_高见龙.pdf#page=185&selection=87,16,89,19)
> 用 edit 暂停，reset 到 HEAD^，一个一个 add+commit。

**squash 和 fixup 不能用在 rebase -i 列表的首个 commit，因为它前面就是要保留的 base commit，无法与之合并成新 commit**

## HEAD

[HEAD是一个指标，指向某一个分支，通常可以把它当作“当前所在分支”来看待。](../assets/58561_Git从入门到精通_高见龙.pdf#page=77&selection=91,0,96,4)（如：refs/heads/master）。分支也是个指针，指向分支上最新的 commit。例如：HEAD -> refs/heads/master -> b 431 fa 7

HEAD 如果没有指向本地的分支，则称之为 detached head（断头 HEAD）。可能发生这个状态的原因有：

1. 使用 Checkout 指令直接跳到某个 Commit，而不是 Branch。
2. Rebase 的过程其实也是处于不断的 detached HEAD 状态。
3. 切换到某个远端分支的时候。

断头 HEAD 约等于创建一个叫 HEAD 的临时分支，可以允许你任意 checkout 某个 commit 开始工作，提交新的 commit 与主干分叉。但要切换到其他分支或 commit 时，你可以任选：

### 创建一个新分支

不切回原分支，给这个临时分支一个名字：`git switch -c <new-branch-name>`

```powershell
PS C:\Users\24171\Documents\GitHub\Playground> git checkout 41cb26f
Note: switching to '41cb26f'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

```

checkout 回原来的 branch，然后用：`git branch <new-branch-name> <commit>`

```powershell
PS C:\Users\24171\Documents\GitHub\Playground> git commit -a
[detached HEAD c599bef]         modified:   note.md
 1 file changed, 3 insertions(+), 6 deletions(-)
PS C:\Users\24171\Documents\GitHub\Playground> git checkout master
Warning: you are leaving 2 commits behind, not connected to
any of your branches:

  c599bef       modified:   note.md
  9a7602e       new file:   note.md

If you want to keep them by creating a new branch, this may be a good time
to do so with:

 git branch <new-branch-name> c599bef

Switched to branch 'master'
```

### 不新建分支

Checkout 回原来的 branch，使用提示中的 sha 1 来 merge/rebase。

## .gitignore

以”#”号开头表示注释；
以斜杠“/”开头表示目录；
以星号“\*”通配多个字符；
以问号“?”通配单个字符
以方括号“\[\]”包含单个字符的匹配列表；
以叹号“!”表示不忽略 (跟踪) 匹配到的文件或目录；

```bash
*.txt , *.xls  # 表示过滤某种类型的文件
target/  # 表示过滤这个文件夹下的所有文件
/test/a.txt , /test/b.xls  # 表示指定过滤某个文件下具体文件
!*.java , !/dir/test/     # !开头表示不过滤
*.[ab]    # 支持通配符：过滤所有以.a或者.b为扩展名的文件
/test  # 仅仅忽略项目根目录下的 test 文件，不包括 child/test等非根目录的test目录
```

已追踪的文件，必须先取消追踪，才能被. Gitignore 忽略。因为其仅影响 git add 找未追踪文件，而不是找文件修改。

## Fun Facts

> [!note] [在空目录中随便放一个文件就行了。如果当前还没有文件可以放，或者不知道该放什么文件，通常可以放一个名为“.keep”或“.gitkeep”的空文件，让Git能“感应”到这个目录的存在](../assets/58561_Git从入门到精通_高见龙.pdf#page=61&selection=23,14,37,8)
> 空的目录无法被 add 检测，因为 git add 只关心文件内容生成 blob 对象，git commit 后才组织 tree 对象形成目录。

> [!note] [其实，Git并不是很在意空间的浪费，能够快速、有效率地操作才是Git关注的重点。](../assets/58561_Git从入门到精通_高见龙.pdf#page=110&selection=99,0,103,6)
> 基本上 commit 时优先记录整个文件，而不是差异。

> [!note] [Git根据这串信息，把原本放在.git/objects中以SHA-1计算命名的目录及文件，一个一个地复原成原来的样子](../assets/58561_Git从入门到精通_高见龙.pdf#page=106&selection=0,3,7,5)
> 跟主席树一样，死去的 oi 又开始攻击我。

> [!note] [想要知道某个文件的某一行代码是谁写的吗？在Git中可使用git blame命令帮你找出来](../assets/58561_Git从入门到精通_高见龙.pdf#page=66&selection=32,10,38,6)

> [!note] [就像是推送空的内容去更新在线的cat分支的内容，也算是变相地把该分支删除。](../assets/58561_Git从入门到精通_高见龙.pdf#page=260&selection=51,0,53,19)
> ```bash
> git push origin :cat
> git push origin master:cat
> ```
> A: B means push A as B

[Git是根据文件的“内容”来计算SHA-1的值，所以文件的名称不重要，重要的是文件的内容。当更改文件名时，Git并不会为此做出一个新的Blob对象，而只是指向原来的那个Blob对象。但因为文件名变了，所以Git会为此做出一个新的Tree对象。](../assets/58561_Git从入门到精通_高见龙.pdf#page=56&selection=25,0,46,3)