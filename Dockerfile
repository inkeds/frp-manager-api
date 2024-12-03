FROM python:3.9 as builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设置pip环境变量
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# 升级pip和工具
RUN pip install --upgrade pip setuptools wheel

# 首先安装基础依赖
COPY requirements-base.txt .
RUN pip install -r requirements-base.txt

# 然后安装其他依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 运行阶段
FROM python:3.9-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 创建非root用户和必要目录
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p logs backups && \
    chown -R appuser:appuser /app logs backups

# 复制应用文件
COPY --chown=appuser:appuser . .

# 切换到非root用户
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
