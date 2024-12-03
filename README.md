# FRP Manager API

基于 FastAPI 的 FRP 管理系统后端 API，支持与 WHMCS 集成。

## 快速开始

### 环境要求

- Python 3.8+
- Redis
- MySQL/SQLite

### 安装部署

1. 克隆仓库：
```bash
git clone https://github.com/inkeds/frp-manager-api.git
cd frp-manager-api
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

4. 初始化数据库：
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

5. 运行服务：
```bash
python -m app.main
```

### Docker 部署

#### 1. 快速开始

使用 Docker Compose 启动所有服务：

```bash
docker-compose up -d
```

访问 API 文档：http://localhost:8000/api/docs

#### 2. 可用的 Docker 镜像

##### Docker Hub
```bash
# 最新版本
docker pull inkeds/frp-manager-api:latest

# 指定版本
docker pull inkeds/frp-manager-api:1.0.0

# 支持的架构
- linux/amd64
- linux/arm64
```

##### GitHub Container Registry
```bash
# 最新版本
docker pull ghcr.io/inkeds/frp-manager-api:latest

# 指定版本
docker pull ghcr.io/inkeds/frp-manager-api:1.0.0
```

#### 3. 环境变量配置

| 变量名 | 描述 | 默认值 | 必填 |
|--------|------|--------|------|
| DATABASE_URL | 数据库连接URL | sqlite:///./data/frp_manager.db | 是 |
| REDIS_URL | Redis连接URL | redis://redis:6379/0 | 是 |
| SECRET_KEY | JWT密钥 | - | 是 |
| WHMCS_API_URL | WHMCS API地址 | - | 是 |
| WHMCS_IDENTIFIER | WHMCS标识符 | - | 是 |
| WHMCS_SECRET | WHMCS密钥 | - | 是 |
| API_URL | API访问地址 | http://localhost:8000 | 否 |
| ENVIRONMENT | 运行环境 | production | 否 |

#### 4. 持久化存储

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

#### 5. 资源限制

各服务的默认资源限制：

| 服务 | CPU限制 | 内存限制 | 最小预留 |
|------|---------|----------|----------|
| api | 1 核 | 1 GB | 512 MB |
| redis | 0.5 核 | 512 MB | - |
| manager | 0.5 核 | 512 MB | - |
| mysql | 1 核 | 1 GB | - |

#### 6. 健康检查

所有服务都配置了健康检查：

- API: 每30秒检查 `/health` 端点
- Redis: 每10秒执行 PING 命令
- MySQL: 每10秒检查数据库连接

#### 7. 日志管理

所有服务使用 JSON 日志驱动：
- 最大文件大小：10MB
- 保留文件数：3个

#### 8. 自定义构建

1. 克隆仓库：
```bash
git clone https://github.com/inkeds/frp-manager-api.git
cd frp-manager-api
```

2. 修改配置：
```bash
# 编辑 docker-compose.yml 和 .env 文件
```

3. 构建并推送：
```bash
# 运行构建脚本
./build_and_push.bat
```

#### 9. 多架构支持

支持的CPU架构：
- AMD64 (x86_64)
- ARM64 (aarch64)

#### 10. 故障排除

1. 检查服务状态：
```bash
docker-compose ps
```

2. 查看服务日志：
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs api
```

3. 重启服务：
```bash
docker-compose restart [service_name]
```

4. 清理并重建：
```bash
docker-compose down -v
docker-compose up -d --build
```

## API 访问地址

### 1. API 文档
默认情况下，API 文档可以通过以下地址访问：

- Swagger UI 文档：`http://localhost:8000/api/docs`
  - 提供交互式 API 文档
  - 支持在线测试 API
  - 包含详细的请求/响应示例

- ReDoc 文档：`http://localhost:8000/api/redoc`
  - 提供更易读的 API 文档
  - 适合文档阅读和分享

### 2. 主要 API 端点

#### 基础 URL
- 开发环境：`http://localhost:8000`
- 生产环境：`https://your-domain.com`

#### API 版本
所有 API 端点都以版本号开头：`/api/v1/`

#### 核心端点
```
# 认证
POST    /api/v1/auth/login            # 用户登录
POST    /api/v1/auth/refresh          # 刷新令牌

# 用户管理
GET     /api/v1/users/me              # 获取当前用户信息
POST    /api/v1/users                 # 创建新用户
GET     /api/v1/users/{id}            # 获取用户信息
PUT     /api/v1/users/{id}            # 更新用户信息
DELETE  /api/v1/users/{id}            # 删除用户

# FRP 服务
GET     /api/v1/frp/services          # 获取服务列表
POST    /api/v1/frp/services          # 创建新服务
GET     /api/v1/frp/services/{id}     # 获取服务详情
PUT     /api/v1/frp/services/{id}     # 更新服务
DELETE  /api/v1/frp/services/{id}     # 删除服务

# WHMCS 集成
POST    /api/v1/whmcs/sync            # 同步订单
GET     /api/v1/whmcs/products        # 获取产品列表
POST    /api/v1/whmcs/webhook         # Webhook 接收

# 系统监控
GET     /api/v1/monitor/status        # 系统状态
GET     /api/v1/monitor/resources     # 资源使用
GET     /metrics                      # Prometheus 指标
GET     /health                       # 健康检查
```

### 3. API 使用示例

1. 获取访问令牌：
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

2. 使用令牌访问 API：
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer your-access-token"
```

3. 创建 FRP 服务：
```bash
curl -X POST http://localhost:8000/api/v1/frp/services \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-service",
    "protocol": "http",
    "local_port": 80,
    "remote_port": 8080,
    "domain": "example.com"
  }'
```

## 系统要求

### 最低配置
- CPU: 1核
- 内存: 1GB RAM
- 磁盘空间: 10GB
- Docker运行环境

### 推荐配置
- CPU: 2核或更多
- 内存: 2GB RAM或更多
- 磁盘空间: 20GB或更多
- Docker运行环境
- 稳定的网络连接

## 功能特性

- 创建、读取、更新和删除FRP配置
- JSON格式配置存储
- RESTful API接口
- 跨域支持
- 错误处理
- WHMCS集成
- 用户认证和授权
- Docker支持

## 部署方式

### 使用Docker（推荐）

1. 复制环境变量文件并填写配置：
```bash
cp .env.example .env
```

2. 编辑.env文件，填写必要的配置信息：
- WHMCS API配置
- 数据库连接信息（如果使用MySQL）
- JWT密钥

3. 使用Docker Compose启动服务：
```bash
docker-compose up -d
```

服务将在 http://localhost:8000 启动

### 手动部署

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量

3. 运行服务：
```bash
python main.py
```

服务将在 http://localhost:8000 启动

## API端点

### 获取所有配置
```
GET /configs
```

### 获取特定配置
```
GET /configs/{name}
```

### 创建新配置
```
POST /configs
```

请求体示例：
```json
{
    "name": "my-frp",
    "type": "client",
    "config": {
        "server_addr": "example.com",
        "server_port": 7000,
        "token": "your-token"
    }
}
```

### 更新配置
```
PUT /configs/{name}
```

请求体示例：
```json
{
    "config": {
        "server_addr": "new-example.com",
        "server_port": 7001,
        "token": "new-token"
    }
}
```

### 删除配置
```
DELETE /configs/{name}
```

## API 接口文档

### API 文档访问

- Swagger UI: `http://your-domain:8000/api/docs`
- ReDoc: `http://your-domain:8000/api/redoc`

### API 接口说明

#### 认证相关接口

```
POST /api/v1/auth/login
- 用户登录
- 参数：
  {
    "username": "string",
    "password": "string"
  }
- 返回：JWT token
```

#### 用户管理接口

```
POST /api/v1/users
- 创建用户
- 需要管理员权限
- 参数：
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "role": "client"
  }

GET /api/v1/users/me
- 获取当前用户信息
- 需要认证

GET /api/v1/users/{user_id}
- 获取指定用户信息
- 需要管理员权限

PUT /api/v1/users/{user_id}
- 更新用户信息
- 需要管理员权限

DELETE /api/v1/users/{user_id}
- 删除用户
- 需要管理员权限
```

#### FRP 服务管理接口

```
GET /api/v1/frp/services
- 获取所有 FRP 服务列表
- 需要认证
- 支持分页和筛选

POST /api/v1/frp/services
- 创建新的 FRP 服务
- 需要认证
- 参数：
  {
    "name": "string",
    "protocol": "tcp|udp|http|https",
    "local_port": int,
    "remote_port": int,
    "domain": "string (可选)"
  }

GET /api/v1/frp/services/{service_id}
- 获取特定服务详情
- 需要认证

PUT /api/v1/frp/services/{service_id}
- 更新服务配置
- 需要认证

DELETE /api/v1/frp/services/{service_id}
- 删除服务
- 需要认证

GET /api/v1/frp/services/{service_id}/status
- 获取服务运行状态
- 需要认证

POST /api/v1/frp/services/{service_id}/restart
- 重启服务
- 需要认证
```

#### WHMCS 集成接口

```
POST /api/v1/whmcs/sync
- 同步 WHMCS 订单状态
- 需要管理员权限
- 参数：
  {
    "order_id": "string"
  }

GET /api/v1/whmcs/products
- 获取 WHMCS 产品列表
- 需要管理员权限

POST /api/v1/whmcs/webhook
- WHMCS Webhook 接收端点
- 处理订单状态变更
```

#### 系统监控接口

```
GET /api/v1/monitor/status
- 获取系统状态
- 需要管理员权限

GET /api/v1/monitor/resources
- 获取资源使用情况
- 需要管理员权限

GET /metrics
- Prometheus 指标接口
- 需要管理员权限
```

### API 认证说明

1. 获取访问令牌：
```bash
curl -X POST http://your-domain:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

2. 使用访问令牌：
```bash
curl -X GET http://your-domain:8000/api/v1/users/me \
  -H "Authorization: Bearer your-access-token"
```

### 错误码说明

```
200: 成功
400: 请求参数错误
401: 未认证
403: 权限不足
404: 资源不存在
429: 请求过于频繁
500: 服务器内部错误
```

## 配置文件存储

所有配置文件都存储在 `configs` 目录下，以JSON格式保存。每个配置文件以配置名称命名，例如：`my-frp.json`。

## 数据持久化

### 使用SQLite（默认）
- 数据文件存储在 `./data` 目录
- FRP配置文件存储在 `./configs` 目录

### 使用MySQL
1. 在docker-compose.yml中取消MySQL服务的注释
2. 在.env中配置MySQL连接信息：
```env
DATABASE_URL=mysql+pymysql://user:password@db/frp_manager
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_USER=your-user
MYSQL_PASSWORD=your-password
```

## 开发环境设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. 安装开发依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件
```

4. 运行开发服务器：
```bash
uvicorn main:app --reload
```

## 监控和日志

### 日志文件
- 位置: ./logs/
- 格式: 按日期分割
- 自动轮转: 保留最近5个文件
- 最大文件大小: 10MB

### 监控阈值
- CPU使用率 > 80% 触发警告
- 内存使用率 > 80% 触发警告
- 磁盘使用率 > 80% 触发警告

## 管理系统使用说明

FRP管理系统提供了一个交互式的管理面板，可以方便地进行系统管理、监控和维护。

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

### 功能菜单

管理面板提供以下功能：

1. **系统状态检查**
   - 检查CPU、内存、磁盘使用情况
   - 验证系统要求
   - 显示系统配置信息

2. **查看系统详细信息**
   - 显示完整的系统状态
   - 查看性能指标
   - 检查系统资源使用情况

3. **查看健康状态**
   - 检查服务运行状态
   - 显示警告和错误信息
   - 验证系统组件状态

4. **查看日志**
   - 浏览系统日志文件
   - 查看错误和警告记录
   - 支持实时日志查看

5. **性能监控**
   - 实时监控系统性能
   - 显示资源使用趋势
   - 查看性能指标统计

6. **管理FRP配置**
   - 查看所有配置
   - 添加新配置
   - 修改现有配置
   - 删除配置

7. **用户管理**
   - 查看所有用户
   - 添加新用户
   - 修改用户信息
   - 删除用户

8. **重启服务**
   - 安全重启API服务
   - 重启Docker容器
   - 刷新系统配置

9. **备份数据**
   - 创建系统备份
   - 管理备份文件
   - 自动备份功能

0. **退出程序**
   - 安全退出管理面板

### 使用技巧

1. **日志查看**
   ```bash
   # 实时查看最新日志
   tail -f logs/main_YYYYMMDD.log

   # 搜索错误信息
   grep ERROR logs/main_YYYYMMDD.log
   ```

2. **性能监控**
   - 使用`Ctrl+C`退出实时监控
   - 监控数据每2秒更新一次
   - 支持查看历史数据

3. **配置管理**
   - 修改配置前先创建备份
   - 使用JSON格式编辑配置
   - 保存前验证配置格式

4. **用户管理**
   - 遵循最小权限原则
   - 定期更新用户密码
   - 及时删除未使用的账户

5. **备份策略**
   - 定期创建系统备份
   - 保留多个备份版本
   - 定期清理旧备份

### 常见问题解决

1. **管理面板无法启动**
   - 检查Python环境
   - 验证依赖包安装
   - 检查配置文件权限

2. **Docker环境问题**
   - 确保Docker服务运行
   - 检查容器网络连接
   - 验证卷挂载权限

3. **配置更新失败**
   - 检查配置文件格式
   - 验证文件权限
   - 查看错误日志

4. **性能监控异常**
   - 检查系统资源使用
   - 验证监控服务状态
   - 查看连接日志

### 最佳实践

1. **日常维护**
   - 定期检查系统状态
   - 及时更新配置文件
   - 定期清理日志文件

2. **安全建议**
   - 定期更改密码
   - 限制访问权限
   - 保持系统更新

3. **性能优化**
   - 监控资源使用
   - 及时清理缓存
   - 优化配置参数

4. **故障恢复**
   - 保持最新备份
   - 记录配置更改
   - 建立应急方案

## 性能优化

### 1. 缓存层
- Redis缓存服务用于提高频繁访问数据的响应速度
- 支持单个和批量缓存操作
- 可配置的TTL（生存时间）
- 支持计数器和原子操作

### 2. 数据库查询优化
- 实现智能分页
- 关系预加载避免N+1查询问题
- 批量查询优化
- 高效的搜索查询实现

### 3. 后台任务处理
- 异步任务队列
- 长时间运行任务的后台处理
- 任务状态跟踪
- 错误处理和重试机制

### 4. 系统监控
- 详细的健康检查端点
- Prometheus指标收集
- Sentry错误跟踪
- 请求处理时间监控

## 性能建议

### 1. 缓存使用
- 对频繁访问的数据使用Redis缓存
- 合理设置缓存TTL
- 使用批量操作减少网络往返

### 2. 数据库查询
- 使用分页避免大量数据查询
- 合理使用索引
- 预加载必要的关联数据

### 3. 并发处理
- 使用后台任务处理耗时操作
- 合理设置工作进程数
- 使用连接池管理资源

### 4. API使用建议
- 使用批量接口减少请求次数
- 合理使用过滤和搜索参数
- 遵循API速率限制

## WHMCS集成

### WHMCS后台配置

#### 1.1 API凭证设置
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

### 3. 对接流程说明

#### 3.1 订单处理流程
1. 客户下单
   - 客户在WHMCS选购FRP产品
   - 填写端口、协议等信息
   - 完成支付

2. 自动开通
   - WHMCS发送Webhook到FRP Manager
   - FRP Manager收到通知后：
     - 验证订单信息
     - 分配端口资源
     - 生成FRP配置
     - 启动FRP服务

3. 状态更新
   - FRP Manager定期检查服务状态
   - 同步到期时间到WHMCS
   - 处理续费和停用

#### 3.2 API使用示例

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

### 4. 常见问题处理

1. WHMCS连接问题
   - 检查API凭证是否正确
   - 确认WHMCS URL是否可访问
   - 查看WHMCS API日志

2. 端口分配问题
   - 检查端口是否被占用
   - 确认端口范围设置
   - 查看端口分配日志

3. 服务自动化问题
   - 确认Webhook设置
   - 检查任务队列状态
   - 查看自动化日志

## 技术支持

如遇到问题：
1. 查看详细日志
2. 检查系统状态
3. 联系技术支持
