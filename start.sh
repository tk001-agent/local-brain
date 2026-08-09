#!/bin/bash
# 本地大脑启动脚本
set -e

cd /home/ubuntu/local-brain

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -q -r requirements.txt

# 确保数据目录存在
mkdir -p data/raw data/topics

# 启动服务
echo "Starting local-brain on port 18900..."
exec gunicorn -w 2 -b 0.0.0.0:18900 server:app