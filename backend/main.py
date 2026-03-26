from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api import auth, users, devices, logs, access_records
from src.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="小区门禁管理系统API",
    description="基于RBAC的小区门禁管理系统后端API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(devices.router, prefix="/api/devices", tags=["设备管理"])
app.include_router(logs.router, prefix="/api/logs", tags=["日志查询"])
app.include_router(access_records.router, prefix="/api/access-records", tags=["门禁记录"])


@app.get("/")
async def root():
    return {"message": "小区门禁管理系统后端API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}