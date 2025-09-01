#!/bin/bash

# 为新域名 hc.1343263.xyz 获取 SSL 证书
# 确保您已经安装了 certbot

DOMAIN="${DOMAIN:-hc.1343263.xyz}"
EMAIL="${EMAIL:-}"

echo "正在为域名 $DOMAIN 获取 SSL 证书..."

# 安装 certbot（如果未安装）
if ! command -v certbot &> /dev/null; then
    echo "安装 certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# 停止 Nginx 服务以释放端口
sudo systemctl stop nginx

# 选择邮箱参数
if [ -z "$EMAIL" ]; then
    EMAIL_FLAG="--register-unsafely-without-email"
else
    EMAIL_FLAG="--email $EMAIL --no-eff-email"
fi

# 使用 certbot 获取证书（standalone 模式，临时占用 80 端口）
sudo certbot certonly --standalone \
    $EMAIL_FLAG \
    --agree-tos \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    echo "证书获取成功！"
    
    # 复制证书到项目目录
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/chatto/ssl/$DOMAIN.fullchain.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/chatto/ssl/$DOMAIN.key

    # 设置正确的权限
    sudo chown hc:hc /opt/chatto/ssl/$DOMAIN.*
    sudo chmod 600 /opt/chatto/ssl/$DOMAIN.key
    sudo chmod 644 /opt/chatto/ssl/$DOMAIN.fullchain.pem

    echo "证书位置："
    echo "  - 完整链证书: /opt/chatto/ssl/$DOMAIN.fullchain.pem"
    echo "  - 私钥: /opt/chatto/ssl/$DOMAIN.key"
else
    echo "证书获取失败，使用自签名证书..."
fi

# 重新启动 Nginx
sudo systemctl start nginx

# 检查 Nginx 配置
echo "正在验证 Nginx 配置..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "Nginx 配置正确！正在重新加载..."
    sudo systemctl reload nginx
    echo "域名 $DOMAIN 的配置完成！"
else
    echo "Nginx 配置有误，请检查配置文件。"
fi
