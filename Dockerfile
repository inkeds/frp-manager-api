FROM python:3.9-slim as builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    default-libmysqlclient-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 设置pip环境变量
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

# 复制依赖文件
COPY requirements.txt .

# 分步安装依赖
RUN pip install --upgrade pip setuptools wheel && \
    # 基础依赖
    pip install fastapi==0.104.1 uvicorn==0.24.0 python-dotenv==1.0.0 && \
    # 数据库依赖
    pip install sqlalchemy==2.0.23 pymysql==1.1.0 psycopg2-binary==2.9.9 && \
    # 认证和加密
    pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 bcrypt==4.0.1 && \
    # 其他依赖
    pip install -r requirements.txt

# 运行阶段
FROM python:3.9-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    less \
    libpq5 \
    default-mysql-client \
    libffi7 \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
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
