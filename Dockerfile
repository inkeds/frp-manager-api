FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    less \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY *.py .
COPY .env.example .env

# 创建必要的目录
RUN mkdir -p logs backups

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV API_URL=http://localhost:8000

# 添加管理脚本入口点
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

# 默认命令为启动API服务
CMD ["python", "main.py"]
