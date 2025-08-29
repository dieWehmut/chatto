#!/bin/bash

# 本地 GitHub Pages 部署脚本

echo "🚀 开始构建 GitHub Pages 版本..."

# 检查是否配置了生产环境 API 地址
if [ ! -f .env.production ]; then
    echo "❌ 错误: 未找到 .env.production 文件"
    echo "请先创建 .env.production 文件并配置 VITE_PROD_API_URL"
    exit 1
fi

# 检查 API 地址是否已配置
if grep -q "YOUR_DEBIAN_SERVER_IP" .env.production; then
    echo "❌ 错误: 请在 .env.production 中配置正确的 Debian 服务器地址"
    echo "将 YOUR_DEBIAN_SERVER_IP 替换为您的实际服务器 IP 或域名"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
npm install

# 构建项目
echo "🔨 构建项目..."
npm run build:github

# 检查构建结果
if [ ! -d "dist" ]; then
    echo "❌ 构建失败: dist 目录不存在"
    exit 1
fi

echo "✅ 构建成功!"
echo "📁 dist 目录已生成，包含以下文件:"
ls -la dist/

echo ""
echo "🌐 部署说明:"
echo "1. 将 dist/ 目录下的所有文件上传到您的 GitHub 仓库的 gh-pages 分支"
echo "2. 或者使用 GitHub Actions 自动部署"
echo "3. 确保 GitHub Pages 设置中选择了正确的分支和目录"

echo ""
echo "🔍 预览部署结果:"
echo "可以运行 'npm run preview:github' 来本地预览 GitHub Pages 版本"

echo ""
echo "📋 API 配置信息:"
echo "生产环境 API 地址: $(grep VITE_PROD_API_URL .env.production | cut -d'=' -f2)"
