FROM python:3.11-slim

# 安裝必要工具
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

# 安裝 uv
RUN pip install uv

WORKDIR /app
COPY . .

# 使用 uv 安裝套件
RUN uv pip install -r requirements.txt --system

CMD ["python", "main.py"]
