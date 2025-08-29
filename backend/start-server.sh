#!/bin/bash

# 后端启动脚本

echo "🚀 启动聊天系统后端服务..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📚 安装 Python 依赖..."
    pip install -r requirements.txt
fi

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在，使用默认配置"
    echo "建议创建 .env 文件并配置相应参数"
fi

# 显示配置信息
echo ""
echo "📋 服务器配置:"
echo "   主机: $(grep SERVER_HOST .env 2>/dev/null | cut -d'=' -f2 || echo '0.0.0.0')"
echo "   端口: $(grep SERVER_PORT .env 2>/dev/null | cut -d'=' -f2 || echo '8000')"
echo "   数据库: $(grep DATABASE_URL .env 2>/dev/null | cut -d'=' -f2 || echo 'sqlite:///./chat.db')"

echo ""
echo "🌐 访问地址:"
echo "   本地: http://127.0.0.1:8000"
echo "   局域网: http://$(hostname -I | awk '{print $1}'):8000"
echo "   API 文档: http://127.0.0.1:8000/docs"

echo ""
echo "🔥 启动服务器..."
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务器
python run_server.py
