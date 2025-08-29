# GitHub Pages 部署指南

## 📋 部署前准备

### 1. 配置生产环境 API 地址

编辑 `frontend/.env.production` 文件，将 Debian 服务器地址替换为实际地址：

```bash
# 替换为您的 Debian 服务器实际地址
VITE_PROD_API_URL=http://YOUR_DEBIAN_SERVER_IP:8000
# 或者使用域名
VITE_PROD_API_URL=https://your-domain.com
```

### 2. 后端服务器配置

确保 Debian 服务器上的后端服务：
- 运行在端口 8000
- 配置了正确的 CORS 允许 GitHub Pages 访问
- 防火墙允许外部访问端口 8000

## 🚀 部署方式

### 方式一：手动部署（推荐用于测试）

1. **构建项目**
   ```bash
   cd frontend
   ./deploy-github.sh
   ```

2. **上传文件**
   - 将 `frontend/dist/` 目录下的所有文件
   - 上传到 GitHub 仓库的根目录或 gh-pages 分支

### 方式二：GitHub Actions 自动部署

1. **配置 GitHub Secrets**
   - 进入 GitHub 仓库 Settings -> Secrets and variables -> Actions
   - 添加 Secret：`VITE_PROD_API_URL`，值为您的 Debian 服务器地址

2. **提交代码**
   ```bash
   git add .
   git commit -m "Configure GitHub Pages deployment"
   git push origin main
   ```

3. **启用 GitHub Pages**
   - 进入仓库 Settings -> Pages
   - Source 选择 "Deploy from a branch"
   - Branch 选择 "gh-pages"

## 🧪 本地测试

### 测试本地开发环境

```bash
cd frontend
./test-local.sh
```

### 测试 GitHub Pages 版本

```bash
cd frontend
npm run build:github
npm run preview:github
```

## 🔧 故障排除

### 1. API 连接失败

- **检查后端服务**：确保 Debian 服务器上的后端正在运行
- **检查防火墙**：确保端口 8000 对外开放
- **检查 CORS 配置**：确保后端允许 GitHub Pages 域名访问

### 2. GitHub Pages 404 错误

- 检查 GitHub Pages 设置是否正确
- 确保 dist 目录已正确上传
- 检查 base 路径配置是否正确

### 3. 资源加载失败

- 检查 vite.config.js 中的 base 路径设置
- 确保所有资源使用相对路径

## 📁 目录结构

```
frontend/
├── .env                    # 本地开发环境配置
├── .env.production         # 生产环境配置
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions 部署脚本
├── deploy-github.sh        # 手动部署脚本
├── test-local.sh          # 本地测试脚本
└── dist/                  # 构建输出目录（部署到 GitHub）
```

## 🌐 访问地址

- **本地开发**: http://localhost:5173
- **GitHub Pages**: https://diewehmut.github.io/chatto1.0.0
- **后端 API**: http://YOUR_DEBIAN_SERVER_IP:8000

## 📝 注意事项

1. 确保 Debian 服务器的防火墙配置允许外部访问
2. 如果使用 HTTPS 域名，GitHub Pages 只能访问 HTTPS 的 API
3. 定期检查 CORS 配置，确保包含正确的域名
4. 生产环境中务必更改默认的 SECRET_KEY
