"""本地大脑 HTTP API 服务 - 接收对话，记录归档，话题提取"""

import sys
import os
from datetime import datetime, timezone, timedelta

# 确保模块路径
sys.path.insert(0, "/home/ubuntu/local-brain")

from flask import Flask, request, jsonify
from recorder import record_dialog
from analyzer import extract_topic
from storage import save_topic_entry

app = Flask(__name__)

# 北京时间时区
CST = timezone(timedelta(hours=8))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "local-brain",
        "timestamp": datetime.now(CST).isoformat()
    })


@app.route("/dialog", methods=["POST"])
def dialog():
    """接收对话内容，返回处理结果"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体需为JSON格式"}), 400

    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "content字段不能为空"}), 400

    speaker = data.get("speaker", "用户")
    timestamp = data.get("timestamp", datetime.now(CST).isoformat())

    # 1. 记录原始对话
    raw_path = record_dialog(timestamp, speaker, content)

    # 2. LLM提取话题
    topic_info = extract_topic(speaker, content)

    # 3. 确定最终话题名
    if topic_info.get("matched_topic") and not topic_info.get("is_new"):
        final_topic = topic_info["matched_topic"]
    else:
        final_topic = topic_info.get("topic_name", "未分类")

    # 4. 保存话题档案
    topic_path = save_topic_entry(
        topic_name=final_topic,
        summary=topic_info.get("summary", content[:100]),
        timestamp=timestamp,
        speaker=speaker,
        content=content
    )

    return jsonify({
        "status": "ok",
        "raw_file": raw_path,
        "topic_name": final_topic,
        "topic_file": topic_path,
        "summary": topic_info.get("summary", ""),
        "is_new_topic": topic_info.get("is_new", True)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=18900, debug=False)