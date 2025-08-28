# 后端部署指南

## 服务器环境要求

- Python 3.8+
- 推荐使用 Ubuntu/Debian Linux

## 部署步骤

### 1. 准备服务器环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和 pip
sudo apt install python3 python3-pip python3-venv -y

# 安装 Git（如果需要从 GitHub 克隆代码）
sudo apt install git -y
```

### 2. 上传后端代码

将整个 `backend` 文件夹上传到服务器，例如 `/opt/chatto/backend`

### 3. 安装依赖

```bash
cd /opt/chatto/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

在 `.env` 文件中配置：

```bash
# 环境配置
ENVIRONMENT=production

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 数据库配置（SQLite）
DATABASE_URL=sqlite:///./chat.db

# 文件上传配置
UPLOAD_DIR=uploads

# 跨域设置 - 替换为你的前端域名
CORS_ORIGINS=https://diewehmut.github.io/chatto1.0.0

# 安全设置 - 请生成一个强密钥
SECRET_KEY=请替换为一个强密钥
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 5. 创建必要的目录

```bash
mkdir -p uploads
chmod 755 uploads
```

### 6. 运行服务器

#### 方式 1: 直接运行（开发测试用）

```bash
python run_server.py
```

#### 方式 2: 使用 systemd 服务（推荐生产环境）

创建服务文件：

```bash
sudo nano /etc/systemd/system/chatto.service
```

服务文件内容：

```ini
[Unit]
Description=Chatto Chat API Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/chatto/backend
Environment=PATH=/opt/chatto/backend/venv/bin
ExecStart=/opt/chatto/backend/venv/bin/python run_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start chatto

# 设置开机自启
sudo systemctl enable chatto

# 查看服务状态
sudo systemctl status chatto
```

### 7. 配置防火墙（如果需要）

```bash
# 允许 8000 端口
sudo ufw allow 8000

# 如果使用 Nginx 反向代理，允许 80 和 443
sudo ufw allow 80
sudo ufw allow 443
```

### 8. 使用 Nginx 反向代理（可选但推荐）

安装 Nginx：

```bash
sudo apt install nginx -y
```

创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/chatto
```

配置内容：

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件上传大小限制
    client_max_body_size 50M;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/chatto /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 维护命令

```bash
# 查看服务日志
sudo journalctl -u chatto -f

# 重启服务
sudo systemctl restart chatto

# 停止服务
sudo systemctl stop chatto

# 更新代码后重启
cd /opt/chatto/backend
source venv/bin/activate
git pull  # 如果使用 git
sudo systemctl restart chatto
```

## 故障排除

1. **端口被占用**: 检查端口使用情况 `sudo netstat -tlnp | grep 8000`
2. **权限问题**: 确保 uploads 目录有正确的写权限
3. **数据库问题**: 检查 SQLite 数据库文件权限
4. **CORS 错误**: 确保 `.env` 中的 CORS_ORIGINS 包含前端域名
