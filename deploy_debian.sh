#!/bin/bash

# Debian服务器部署脚本
# 使用方法: ./deploy_debian.sh [服务器IP] [用户名]

SERVER_IP=${1:-"your-server-ip"}
USERNAME=${2:-"root"}
PROJECT_NAME="hcchat"
REMOTE_PATH="/opt/$PROJECT_NAME"

echo "开始部署到 Debian 服务器..."
echo "服务器: $USERNAME@$SERVER_IP"
echo "部署路径: $REMOTE_PATH"

# 检查服务器连接
echo "检查服务器连接..."
ssh $USERNAME@$SERVER_IP "echo '服务器连接成功'"

if [ $? -ne 0 ]; then
    echo "错误: 无法连接到服务器"
    exit 1
fi

# 在服务器上创建项目目录
echo "创建项目目录..."
ssh $USERNAME@$SERVER_IP "mkdir -p $REMOTE_PATH"

# 同步后端代码
echo "上传后端代码..."
rsync -avz --delete \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='chat.db' \
    --exclude='.env' \
    backend/ $USERNAME@$SERVER_IP:$REMOTE_PATH/backend/

# 上传前端构建产物
echo "构建前端代码..."
cd frontend
npm run build
echo "上传前端代码..."
rsync -avz --delete dist/ $USERNAME@$SERVER_IP:$REMOTE_PATH/frontend/

cd ..

# 上传部署配置
echo "上传部署配置文件..."
scp nginx.conf $USERNAME@$SERVER_IP:$REMOTE_PATH/
scp systemd_service.conf $USERNAME@$SERVER_IP:$REMOTE_PATH/hcchat.service
scp requirements.txt $USERNAME@$SERVER_IP:$REMOTE_PATH/

# 在服务器上执行安装脚本
echo "在服务器上安装依赖..."
ssh $USERNAME@$SERVER_IP << 'EOF'
    cd /opt/hcchat
    
    # 更新系统
    apt update
    
    # 安装Python和pip
    apt install -y python3 python3-pip python3-venv nginx supervisor
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 安装Python依赖
    pip install -r requirements.txt
    
    # 创建数据库目录
    mkdir -p /opt/hcchat/data
    
    # 配置Nginx
    cp nginx.conf /etc/nginx/sites-available/hcchat
    ln -sf /etc/nginx/sites-available/hcchat /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    
    # 配置systemd服务
    cp hcchat.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable hcchat
    systemctl start hcchat
    
    echo "部署完成！"
    systemctl status hcchat
EOF

echo "部署脚本执行完成！"
echo "请访问 http://$SERVER_IP 查看应用"
