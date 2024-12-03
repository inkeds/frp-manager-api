from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
import sentry_sdk
from prometheus_client import make_asgi_app
import time
import asyncio

from app.core.config import get_settings
from app.api.v1.endpoints import users
from app.services.background_tasks import task_manager
from app.services.cache_service import cache_service

settings = get_settings()

# 初始化Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# 请求处理中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 启动事件
@app.on_event("startup")
async def startup():
    # 初始化Redis限速器
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_client)
    
    # 启动后台任务处理器
    asyncio.create_task(task_manager.start())

# 关闭事件
@app.on_event("shutdown")
async def shutdown():
    # 停止后台任务处理器
    await task_manager.stop()

# 注册路由
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)

# 健康检查端点
@app.get("/health")
@RateLimiter(times=60, seconds=60)
async def health_check():
    # 检查Redis连接
    try:
        await cache_service.set("health_check", "ok", ttl=10)
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"

    # 检查后台任务处理器
    task_processor_status = "healthy" if task_manager.running else "stopped"

    return {
        "status": "healthy",
        "components": {
            "redis": redis_status,
            "task_processor": task_processor_status,
            "api": "healthy"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
