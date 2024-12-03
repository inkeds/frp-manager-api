# FRP Management API

这是一个用于管理FRP（Fast Reverse Proxy）配置的RESTful API服务。

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

## 故障排除

### 常见问题
1. 服务无法启动
- 检查系统要求
- 检查配置文件
- 查看日志文件

2. 性能问题
- 检查系统资源使用情况
- 查看警告信息
- 检查日志文件

3. 连接问题
- 检查网络配置
- 验证WHMCS API配置
- 检查数据库连接

### 日志查看
```bash
# 查看最新日志
tail -f logs/main_YYYYMMDD.log

# 查看错误日志
grep ERROR logs/main_YYYYMMDD.log
```

## 安全建议

1. 生产环境配置
- 使用强密码
- 启用HTTPS
- 限制API访问IP
- 定期更新密钥

2. 监控建议
- 定期检查系统状态
- 设置资源告警
- 监控异常访问
- 定期备份数据

3. 维护建议
- 定期检查日志
- 清理过期数据
- 更新系统补丁
- 检查系统资源

## 支持和反馈

如遇到问题：
1. 检查系统状态
2. 查看详细指标
3. 检查日志文件
4. 联系技术支持
