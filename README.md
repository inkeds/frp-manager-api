# FRP Manager API

基于 FastAPI 的 FRP 管理系统后端 API，支持与 WHMCS 集成，提供完整的 FRP 服务管理解决方案。

## 快速开始

### 环境要求

- Python 3.8+
- CPU: 1 核心
- 内存: 512MB
- 存储: 1GB

### 功能特性

- 🔒 完整的认证和授权系统
- 🔄 自动化的 FRP 配置管理
- 💳 WHMCS 计费系统集成
- 📊 实时资源使用监控
- 🚀 支持水平扩展
- 📝 详细的操作日志
- 🔍 Prometheus 指标支持
- ⚡ Redis 缓存加速

### 安装部署

1. 克隆仓库
```bash
git clone https://github.com/inkeds/frp-manager-api.git
cd frp-manager-api
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

4. 初始化数据库
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

5. 运行服务
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker 部署

#### 方式一：从 Docker Hub 部署

```bash
docker pull inkeds/frp-manager-api:latest
docker run -d \
  --name frp-manager \
  -p 8000:8000 \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  --env-file .env \
  inkeds/frp-manager-api:latest
```

#### 方式二：使用 Docker Compose

1. 启动所有服务
```bash
docker-compose up -d
```

2. 环境变量配置表

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| ENVIRONMENT | 运行环境 | development | 否 |
| DATABASE_URL | 数据库连接 URL | sqlite:///./data/frp_manager.db | 否 |
| REDIS_URL | Redis 连接 URL | redis://redis:6379/0 | 否 |
| REDIS_PASSWORD | Redis 密码 | - | 是 |
| SECRET_KEY | JWT 密钥 | - | 是 |
| WHMCS_API_URL | WHMCS API 地址 | - | 是* |
| WHMCS_IDENTIFIER | WHMCS 标识符 | - | 是* |
| WHMCS_SECRET | WHMCS 密钥 | - | 是* |

*注：仅在需要 WHMCS 集成时必填

3. 持久化存储
```yaml
volumes:
  # 应用数据
  - ./logs:/app/logs         # 日志文件
  - ./backups:/app/backups   # 备份文件
  - ./configs:/app/configs   # 配置文件
  - ./data:/app/data         # 数据文件

  # Redis数据
  - redis_data:/data

  # MySQL数据（可选）
  - mysql_data:/var/lib/mysql
```

4. 服务资源限制

| 服务 | CPU 限制 | 内存限制 | CPU 预留 | 内存预留 |
|------|----------|-----------|----------|-----------|
| api | 1 核 | 1GB | 0.25 核 | 512MB |
| redis | 0.5 核 | 512MB | - | - |

5. 健康检查
```bash
# 检查 API 服务状态
curl http://localhost:8000/health

# 检查 Redis 状态
docker exec frp-manager-redis redis-cli -a ${REDIS_PASSWORD} ping
```

6. 查看服务日志
```bash
# 查看 API 服务日志
docker-compose logs -f api

# 查看 Redis 日志
docker-compose logs -f redis
```

7. 故障排除
```bash
# 重启单个服务
docker-compose restart api

# 检查服务配置
docker-compose config

# 查看服务状态
docker-compose ps

# 清理所有服务
docker-compose down -v
```

## API 接口文档

### API 文档访问

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 对接 WHMCS

#### 1.1 WHMCS后台配置
1. 进入WHMCS后台 → Setup → Staff Management → API Credentials
2. 点击 "Create New Credential"
3. 记录生成的API Identifier和Secret

#### 1.2 产品配置
1. 创建产品组
   - 进入Setup → Products/Services → Product Groups
   - 创建名为 "FRP Services" 的产品组

2. 创建产品
   - 进入Setup → Products/Services → Products/Services
   - 选择 "FRP Services" 组
   - Product Type选择 "Other"
   - 设置价格和周期

3. 添加自定义字段
   - 在产品配置页面找到 "Custom Fields" 标签
   - 添加以下字段：
     ```
     字段名：frp_port
     类型：Text Box
     描述：FRP端口号
     必填：是
     验证：数字
     ```
     ```
     字段名：frp_protocol
     类型：Dropdown
     选项：tcp,udp,http,https
     描述：FRP协议类型
     必填：是
     ```
     ```
     字段名：frp_domain
     类型：Text Box
     描述：绑定域名（可选）
     必填：否
     ```

### 2. FRP Manager配置

#### 2.1 环境变量设置
在 `.env` 文件中配置：
```env
# WHMCS API设置
WHMCS_URL=https://your-whmcs-url/includes/api.php
WHMCS_API_IDENTIFIER=your-api-identifier
WHMCS_API_SECRET=your-api-secret

# WHMCS产品设置
WHMCS_PRODUCT_ID=1  # FRP产品ID
WHMCS_PRODUCT_GROUP=FRP Services

# FRP设置
FRP_SERVER_ADDR=your-frp-server
FRP_SERVER_PORT=7000
FRP_DASHBOARD_PORT=7500
FRP_DASHBOARD_USER=admin
FRP_DASHBOARD_PASS=admin
```
```

### 3. 重启服务使配置生效

### API 接口说明

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| /api/v1/auth/login | POST | 用户登录 | 无 |
| /api/v1/users/me | GET | 获取当前用户信息 | 用户 |
| /api/v1/configs | GET | 获取 FRP 配置列表 | 用户 |
| /api/v1/configs/{name} | GET | 获取特定配置 | 用户 |
| /api/v1/configs | POST | 创建新配置 | 管理员 |
| /api/v1/monitor/resources | GET | 获取资源使用情况 | 管理员 |
| /metrics | GET | Prometheus 指标 | 无 |
| /health | GET | 健康检查 | 无 |


### API使用示例

1. 同步订单状态：
```bash
curl -X POST http://your-api/api/v1/whmcs/sync \
  -H "Authorization: Bearer your-token" \
  -d '{"order_id": "123"}'
```

2. 获取FRP配置：
```bash
curl -X GET http://your-api/api/v1/frp/config/123 \
  -H "Authorization: Bearer your-token"
```

3. 更新服务状态：
```bash
curl -X PUT http://your-api/api/v1/services/123/status \
  -H "Authorization: Bearer your-token" \
  -d '{"status": "active"}'
```

## 管理面板

### 启动管理面板

#### 1. 本地环境
```bash
# 直接运行管理脚本
python manage.py
```

#### 2. Docker环境
```bash
# 方式1：使用docker-compose运行管理服务
docker-compose up manager

# 方式2：在运行中的容器中执行
docker-compose exec api python manage.py
```
