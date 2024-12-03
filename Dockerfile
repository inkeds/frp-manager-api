FROM python:3.9-slim as builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置pip环境变量
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# 运行阶段
FROM python:3.9-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    less \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 设置环境变量
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    API_URL=http://localhost:8000

# 创建非root用户和必要目录
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p logs backups && \
    chown -R appuser:appuser /app logs backups

# 复制应用文件
COPY --chown=appuser:appuser *.py .
COPY --chown=appuser:appuser .env.example .env

# 复制并设置入口脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 切换到非root用户
USER appuser

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["python", "main.py"]
