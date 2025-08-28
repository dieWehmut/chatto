# HCChat 部署指南

## 部署到 Debian 服务器

### 前提条件
- Debian 服务器（推荐 Ubuntu 20.04+ 或 Debian 11+）
- SSH 访问权限
- 域名（可选）

### 部署步骤

1. **准备服务器**
   ```bash
   # 在本地执行
   chmod +x deploy_debian.sh
   ./deploy_debian.sh YOUR_SERVER_IP USERNAME
   ```

2. **手动部署（如果自动脚本失败）**
   ```bash
   # 在服务器上执行
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv nginx
   
   # 创建项目目录
   sudo mkdir -p /opt/hcchat
   sudo chown www-data:www-data /opt/hcchat
   
   # 上传代码（在本地执行）
   rsync -avz backend/ user@server:/opt/hcchat/backend/
   
   # 在服务器上安装依赖
   cd /opt/hcchat/backend
   python3 -m venv ../venv
   source ../venv/bin/activate
   pip install -r requirements.txt
   
   # 配置服务
   sudo cp systemd_service.conf /etc/systemd/system/hcchat.service
   sudo systemctl daemon-reload
   sudo systemctl enable hcchat
   sudo systemctl start hcchat
   
   # 配置 Nginx
   sudo cp nginx.conf /etc/nginx/sites-available/hcchat
   sudo ln -s /etc/nginx/sites-available/hcchat /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **配置环境变量**
   ```bash
   cd /opt/hcchat/backend
   cp .env.example .env
   # 编辑 .env 文件，设置正确的配置
   nano .env
   ```

### 服务管理命令
```bash
# 查看服务状态
sudo systemctl status hcchat

# 重启服务
sudo systemctl restart hcchat

# 查看日志
sudo journalctl -u hcchat -f

# 重新加载 Nginx
sudo systemctl reload nginx
```

## 部署到 GitHub Pages

### 前提条件
- GitHub 仓库
- 启用 GitHub Pages

### 部署步骤

1. **启用 GitHub Pages**
   - 进入仓库设置
   - 找到 "Pages" 部分
   - Source 选择 "GitHub Actions"

2. **推送代码**
   ```bash
   git add .
   git commit -m "Add deployment configurations"
   git push origin main
   ```

3. **自动部署**
   - GitHub Actions 会自动构建和部署
   - 访问 `https://yourusername.github.io/chatto/`

### 注意事项

**对于 GitHub Pages 部署：**
- 仅支持静态前端，后端 API 需要单独部署
- 需要配置 API 基础 URL 指向您的后端服务器
- 适合演示和前端开发

**对于 Debian 服务器部署：**
- 完整的前后端应用
- 支持文件上传和数据库
- 适合生产环境

## SSL 证书配置（推荐）

使用 Let's Encrypt 免费 SSL：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

## 性能优化

1. **启用 Gzip 压缩**（已在 nginx.conf 中配置）
2. **配置缓存**（已在 nginx.conf 中配置）
3. **使用 CDN**（可选）
4. **数据库优化**：考虑使用 PostgreSQL 替代 SQLite

## 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   sudo journalctl -u hcchat -n 50
   ```

2. **Nginx 配置错误**
   ```bash
   sudo nginx -t
   ```

3. **权限问题**
   ```bash
   sudo chown -R www-data:www-data /opt/hcchat
   ```

4. **端口被占用**
   ```bash
   sudo netstat -tlnp | grep :8000
   ```
