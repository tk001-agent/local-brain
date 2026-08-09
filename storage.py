"""话题档案存储：按话题分类保存到 data/topics/话题名.md"""

import os
from datetime import datetime

TOPICS_DIR = "/home/ubuntu/local-brain/data/topics"


def save_topic_entry(topic_name: str, summary: str, timestamp: str, speaker: str, content: str) -> str:
    """将话题条目追加到话题档案，返回文件路径"""
    os.makedirs(TOPICS_DIR, exist_ok=True)

    # 安全文件名：保留中文、字母、数字、下划线、短横线
    safe_name = "".join(
        c for c in topic_name
        if c.isalnum() or c in "_-"
        or '\u4e00' <= c <= '\u9fff'
        or '\u3400' <= c <= '\u4dbf'
    )
    if not safe_name:
        safe_name = "未分类"
    file_path = os.path.join(TOPICS_DIR, f"{safe_name}.md")

    try:
        dt = datetime.fromisoformat(timestamp)
    except (ValueError, TypeError):
        dt = datetime.now()

    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    is_new = not os.path.exists(file_path)

    with open(file_path, "a", encoding="utf-8") as f:
        if is_new:
            f.write(f"# {topic_name}\n\n")
            f.write(f"> 创建时间：{dt.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

        f.write(f"## {time_str} | {speaker}\n\n")
        f.write(f"**摘要：** {summary}\n\n")
        f.write(f"**原文：**\n\n{content.strip()}\n\n")
        f.write("---\n\n")

    return file_path