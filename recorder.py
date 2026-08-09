"""原始对话记录模块：按日期归档到 data/raw/YYYY/MM/DD.md"""

import os
from datetime import datetime

RAW_DIR = "/home/ubuntu/local-brain/data/raw"


def record_dialog(timestamp: str, speaker: str, content: str) -> str:
    """将对话记录写入按日期归档的md文件，返回文件路径"""
    try:
        dt = datetime.fromisoformat(timestamp)
    except (ValueError, TypeError):
        dt = datetime.now()

    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")
    time_str = dt.strftime("%H:%M:%S")

    dir_path = os.path.join(RAW_DIR, year, month)
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, f"{day}.md")
    is_new = not os.path.exists(file_path)

    with open(file_path, "a", encoding="utf-8") as f:
        if is_new:
            f.write(f"# {dt.strftime('%Y-%m-%d')} 对话记录\n\n")
        f.write(f"## [{time_str}] {speaker}\n\n")
        f.write(f"{content.strip()}\n\n")

    return file_path