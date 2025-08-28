from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import chat, auth
from app.database import engine
from app.models import Base
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="聊天系统 API", description="基于邀请码的聊天系统")

# 从环境变量获取CORS配置
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
if not cors_origins or cors_origins == [""]:
    # 默认开发环境配置
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite 默认端口
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://diewehmut.github.io",  # GitHub Pages 域名
        "https://diewehmut.github.io/chatto1.0.0",  # GitHub Pages 子路径
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
else:
    # 生产环境配置
    allowed_origins = [origin.strip() for origin in cors_origins]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录用于文件下载
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(chat.router, prefix="/chat", tags=["聊天"])

@app.get("/")
def read_root():
    return {"message": "欢迎使用聊天系统 API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}