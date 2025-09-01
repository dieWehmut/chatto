# 域名更新配置总结

## 新域名: hc.1343263.xyz

### 已更新的配置文件

1. **前端配置** (`/opt/chatto/frontend/.env.production`)
   - 更新 `VITE_PROD_API_URL` 为 `https://hc.1343263.xyz`

2. **后端配置** (`/opt/chatto/backend/.env`)
   - 添加新域名到 CORS_ORIGINS
   - 更新 SSL 证书路径指向新域名证书

3. **Nginx 配置**
   - `/opt/chatto/nginx-https.conf`: 更新 server_name 和 SSL 证书路径
   - `/opt/chatto/frontend/nginx.conf`: 更新 server_name 和 SSL 证书路径

### 需要执行的步骤

1. **获取 SSL 证书**
   ```bash
   # 1. 编辑脚本中的邮箱地址
   nano /opt/chatto/setup_ssl_new_domain.sh
   
   # 2. 运行脚本获取 SSL 证书
   sudo ./setup_ssl_new_domain.sh
   ```

2. **更新 DNS 记录**
   - 确保域名 `hc.1343263.xyz` 的 A 记录指向您的服务器 IP
   - 如果使用 IPv6，确保 AAAA 记录也正确配置

3. **重启服务**
   ```bash
   # 重启后端服务
   cd /opt/chatto/backend
   ./start-server.sh
   
   # 重新加载 Nginx
   sudo systemctl reload nginx
   ```

4. **测试配置**
   ```bash
   # 测试 HTTPS 连接
   curl -I https://hc.1343263.xyz
   
   # 检查 API 接口
   curl -I https://hc.1343263.xyz/api/health
   ```

### 注意事项

- 运行 SSL 脚本前，请确保已安装 `certbot`
- 确保防火墙已开放 80 和 443 端口
- 如果使用 Docker 部署，需要同时更新 docker-compose.yml 中的配置
- 建议先在测试环境验证配置正确性

### 证书自动续期

Let's Encrypt 证书有效期为 90 天，建议设置自动续期：

```bash
# 添加到 crontab
echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx" | sudo tee -a /etc/crontab
```
