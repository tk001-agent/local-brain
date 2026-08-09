"""话题提取模块：调用硅基流动LLM从对话中提取话题，返回话题名和摘要"""

import os
import json
import requests

API_BASE = "https://api.siliconflow.cn/v1"
API_KEY = os.getenv("SILICONFLOW_KEY", "")
MODEL = "Qwen/Qwen2.5-72B-Instruct"

EXTRACT_PROMPT = """你是一个话题提取助手。分析以下对话内容，提取核心话题。

要求：
1. 识别对话讨论的核心话题，用简短中文（不超过15个字）命名
2. 用1-2句话总结对话要点作为摘要
3. 判断该话题是否与以下已有话题相似，如果相似则返回已有话题名（实现话题归类）

已有话题列表：
{topic_list}

请严格按以下JSON格式返回，不要输出其他内容：
{{"topic_name": "话题名", "summary": "摘要", "is_new": true/false, "matched_topic": "已有话题名或null"}}

对话内容：
{speaker}: {content}
"""


def get_existing_topics() -> list:
    """获取已有话题列表"""
    topics_dir = "/home/ubuntu/local-brain/data/topics"
    if not os.path.exists(topics_dir):
        return []
    topics = []
    for f in os.listdir(topics_dir):
        if f.endswith(".md"):
            topics.append(f[:-3])
    return topics


def extract_topic(speaker: str, content: str) -> dict:
    """调用LLM提取话题，返回话题信息"""
    topics = get_existing_topics()
    topic_list_str = "\n".join([f"- {t}" for t in topics]) if topics else "（暂无已有话题）"

    prompt = EXTRACT_PROMPT.format(
        topic_list=topic_list_str,
        speaker=speaker,
        content=content
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是一个精确的话题提取助手，只返回JSON格式结果。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500,
        "response_format": {"type": "json_object"}
    }

    try:
        resp = requests.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        result_text = data["choices"][0]["message"]["content"].strip()

        # 清理可能的markdown代码块标记
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

        return json.loads(result_text)

    except (json.JSONDecodeError, KeyError, requests.RequestException) as e:
        print(f"[analyzer] LLM extraction failed: {e}")
        # 降级：返回基础话题
        return {
            "topic_name": "未分类",
            "summary": content[:100] + ("..." if len(content) > 100 else ""),
            "is_new": True,
            "matched_topic": None
        }