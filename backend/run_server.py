#!/usr/bin/env python3
"""
启动聊天服务器的脚本
设置正确的Python路径并启动FastAPI应用
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 加载环境变量
load_dotenv()

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )
