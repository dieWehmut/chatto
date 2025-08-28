# 🚀 Chatto 聊天系统部署指南

## 📋 部署准备清单

### ✅ 已完成的准备工作

1. **后端代码优化**
   - ✅ 支持环境变量配置
   - ✅ 生产/开发环境切换
   - ✅ CORS 配置优化
   - ✅ 创建了 `.env.example` 配置模板

2. **前端代码优化**
   - ✅ 支持 GitHub Pages 部署
   - ✅ API 地址环境变量配置
   - ✅ 构建配置优化
   - ✅ 成功构建了 dist 目录

3. **部署脚本**
   - ✅ Windows 部署脚本 (`deploy.bat`)
   - ✅ Linux/macOS 部署脚本 (`deploy.sh`)

## 🗄️ 部署架构

```
前端 (GitHub Pages)
    ↓ HTTPS 请求
后端服务器 (您的服务器:8000端口)
    ↓
SQLite 数据库 + 文件上传
```

## 🎯 部署步骤

### 第一步：部署后端到服务器

1. **将 `backend` 文件夹上传到您的服务器**
2. **按照 `backend/DEPLOYMENT.md` 的详细说明进行部署**
3. **重要：记下您的服务器 IP 地址或域名**

### 第二步：配置前端服务器地址

在部署前端之前，您需要配置后端服务器地址：

```bash
# 编辑前端配置文件
d:\WorkFiles\chatto\frontend\.env.production
```

将 `YOUR_SERVER_IP` 替换为实际的服务器地址：
```bash
# 示例 - 使用 IP 地址
VITE_PROD_API_URL=http://192.168.1.100:8000

# 示例 - 使用域名
VITE_PROD_API_URL=http://your-server.com:8000

# 如果使用 HTTPS (推荐)
VITE_PROD_API_URL=https://your-server.com:8000
```

### 第三步：部署前端到 GitHub Pages

运行部署脚本：
```bash
# Windows 用户
d:\WorkFiles\chatto\frontend\deploy.bat

# 或者手动执行
cd d:\WorkFiles\chatto\frontend
npm run build
```

然后将 `dist` 目录的内容推送到 GitHub 仓库 `https://github.com/dieWehmut/chatto1.0.0`

## 📁 当前项目状态

### ✅ 前端构建完成
- 构建输出目录: `d:\WorkFiles\chatto\frontend\dist`
- 包含文件:
  - `index.html` (主页面)
  - `assets/` (CSS、JS、图片资源)

### 📝 配置文件位置

**后端配置:**
- 配置模板: `backend\.env.example`
- 部署文档: `backend\DEPLOYMENT.md`

**前端配置:**
- 生产环境配置: `frontend\.env.production`
- 部署脚本: `frontend\deploy.bat` / `frontend\deploy.sh`
- 部署文档: `frontend\DEPLOYMENT.md`

## 🔧 下一步操作

### 1. 后端部署
```bash
# 在您的服务器上执行
cd /path/to/backend
cp .env.example .env
# 编辑 .env 配置文件
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_server.py
```

### 2. 前端配置和部署
```bash
# 在本地执行
cd d:\WorkFiles\chatto\frontend

# 1. 编辑 .env.production，设置正确的后端地址
notepad .env.production

# 2. 重新构建
npm run build

# 3. 部署到 GitHub
deploy.bat  # Windows
# 或者
./deploy.sh  # Linux/macOS
```

### 3. 启用 GitHub Pages

1. 访问 https://github.com/dieWehmut/chatto1.0.0/settings/pages
2. 选择 "Deploy from a branch"
3. 选择 "main" 分支
4. 保存设置

## 🌐 访问地址

部署完成后，您的应用将在以下地址可用：
- **前端**: https://diewehmut.github.io/chatto1.0.0
- **后端**: http://您的服务器IP:8000

## ⚠️ 重要提醒

1. **安全性**: 生产环境请使用 HTTPS
2. **CORS**: 确保后端 CORS 设置包含前端域名
3. **防火墙**: 确保服务器 8000 端口对外开放
4. **备份**: 定期备份数据库和上传的文件

## 🔍 故障排除

如果遇到问题，请查看：
- 后端部署文档: `backend/DEPLOYMENT.md`
- 前端部署文档: `frontend/DEPLOYMENT.md`
- 浏览器开发者工具的网络和控制台选项卡

---

**📞 需要帮助？**
请确保按照每个步骤的详细文档进行操作，如有问题请检查日志文件。
