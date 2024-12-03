# FRP Management API

这是一个用于管理FRP（Fast Reverse Proxy）配置的RESTful API服务。

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

## 注意事项

- 确保WHMCS API配置正确
- 在生产环境中使用强密钥
- 定期备份数据
- 监控日志和系统状态
