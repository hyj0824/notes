import sys
import os
import uuid
from pathlib import Path

def constuct_front_matter(title, tags, uuid=uuid.uuid4()):
    return f"""---
id: {uuid}
title: {title}
tags:
""" + "\n".join([f"  - {tag.strip()}" for tag in tags]) + "\n---\n\n"

def has_frontmatter(filename):
    with open(filename, "rb") as f:
        first_line = f.readline()
        # Handle UTF-8 BOM and avoid locale-dependent decoding issues on Windows.
        first_line = first_line.lstrip(b"\xef\xbb\xbf")
        return first_line.strip() == b"---"

def prompt_for_title_and_tags(default_title="Untitled", default_tags=["no-tag"]):
    print(f"Press enter for default values...")
    title = input(f"Enter title for the note: ") or default_title
    tags = input(f"Enter tags for the note (comma separated): ").split(",")
    if tags == [""]:
        tags = default_tags
    return title, tags

if __name__ == "__main__":
    # 从参数获取文件名，可以有多个参数
    # 遍历参数列表的文件

    # 如果没有参数，提示用户输入文件名
    if len(sys.argv) < 2:
        title, tags = prompt_for_title_and_tags()
        uuid = uuid.uuid4()
        front_matter = constuct_front_matter(title, tags, uuid)
        filename = f"{uuid}/index.md"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8", newline="\n") as f:
            f.write(front_matter)
        print(f"Created new note: {filename}")

    for filename in sys.argv[1:]:
        print(f"\n\nProcessing file: {filename}")
        # 检查文件是否存在
        if not os.path.exists(filename):
            # 创建新文件
            with open(filename, "w", encoding="utf-8", newline="\n") as f:
                pass

        if(has_frontmatter(filename)):
            print(f"File already has front matter: {filename}")
            continue
        else:
            print(f"{filename} does not have front matter, inserting...")
            title, tags = prompt_for_title_and_tags(Path(filename).stem)
            uuid = uuid.uuid4()
            front_matter = constuct_front_matter(title, tags, uuid)
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            with open(filename, "w", encoding="utf-8", newline="\n") as f:
                f.write(front_matter + content)
            print(f"Inserted front matter into: {filename}")
            # 移动到对应位置
            new_filename = f"{uuid}/index.md"
            os.makedirs(os.path.dirname(new_filename), exist_ok=True)
            os.rename(filename, new_filename)
            print(f"Moved {filename} to {new_filename}")
