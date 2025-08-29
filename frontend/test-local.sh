#!/bin/bash

# 本地测试脚本

echo "🧪 启动本地测试环境..."

# 检查后端是否运行
echo "🔍 检查后端服务..."
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务正在运行 (http://127.0.0.1:8000)"
else
    echo "❌ 后端服务未运行，请先启动后端服务"
    echo "在 backend 目录运行: python run_server.py"
    echo ""
fi

# 启动前端开发服务器
echo "🚀 启动前端开发服务器..."
echo "本地访问地址: http://localhost:5173"
echo "局域网访问地址: http://$(hostname -I | awk '{print $1}'):5173"
echo ""
echo "按 Ctrl+C 停止服务"

npm run dev
