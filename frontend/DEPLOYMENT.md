# 前端部署到 GitHub Pages 指南

## 部署前准备

### 1. 配置后端服务器地址

在部署前，您需要先配置前端连接的后端服务器地址。

编辑 `frontend/.env.production` 文件：

```bash
# 将 YOUR_SERVER_IP 替换为您的实际服务器 IP 或域名
VITE_PROD_API_URL=http://192.168.1.100:8000

# 如果您的后端支持 HTTPS，建议使用 https://
# VITE_PROD_API_URL=https://your-domain.com:8000
```

### 2. 确保后端服务器配置了正确的 CORS

在您的后端服务器 `.env` 文件中，确保包含：

```bash
CORS_ORIGINS=https://diewehmut.github.io/chatto1.0.0
```

## 自动部署

### Windows 系统

双击运行 `deploy.bat` 文件，或在命令行中执行：

```cmd
deploy.bat
```

### Linux/macOS 系统

```bash
chmod +x deploy.sh
./deploy.sh
```

## 手动部署步骤

如果自动部署脚本无法使用，可以按以下步骤手动部署：

### 1. 安装依赖并构建

```bash
cd frontend
npm install
npm run build
```

### 2. 推送到 GitHub Pages

```bash
cd dist

# 初始化 git 仓库
git init
git branch -M main

# 添加所有文件
git add .

# 提交更改
git commit -m "Deploy to GitHub Pages"

# 添加远程仓库
git remote add origin https://github.com/dieWehmut/chatto1.0.0.git

# 推送到 GitHub
git push -f origin main
```

### 3. 在 GitHub 启用 Pages

1. 访问 https://github.com/dieWehmut/chatto1.0.0/settings/pages
2. 在 "Source" 部分选择 "Deploy from a branch"
3. 选择 "main" 分支
4. 点击 "Save"

## 访问您的应用

部署完成后，您的应用将在以下地址可用：

```
https://diewehmut.github.io/chatto1.0.0
```

## 重要注意事项

1. **HTTPS vs HTTP**: GitHub Pages 强制使用 HTTPS，但如果您的后端只支持 HTTP，浏览器可能会阻止混合内容请求。建议为后端配置 SSL 证书。

2. **跨域问题**: 确保后端配置了正确的 CORS 设置，允许来自 `https://diewehmut.github.io` 的请求。

3. **文件上传**: 如果您的应用支持文件上传，确保后端服务器有足够的存储空间和正确的权限设置。

## 故障排除

### 常见问题

1. **网络请求失败**

   - 检查 `.env.production` 中的 API 地址是否正确
   - 确认后端服务器正在运行并可访问

2. **CORS 错误**

   - 检查后端 CORS 配置
   - 确保包含 `https://diewehmut.github.io/chatto1.0.0`

3. **页面空白**
   - 检查浏览器控制台的错误信息
   - 确认 `vite.config.js` 中的 base 路径设置正确

## 更新部署

每次需要更新前端时，只需要：

1. 修改代码
2. 重新运行部署脚本：`deploy.bat` (Windows) 或 `deploy.sh` (Linux/macOS)

这将自动构建新版本并推送到 GitHub Pages。
