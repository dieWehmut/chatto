from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import chat, auth
from app.database import engine
from app.models import Base
import os

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="聊天系统 API", description="基于邀请码的聊天系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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