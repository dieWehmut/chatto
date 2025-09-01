#!/bin/bash

# GitHub Pages 部署脚本
# 用于部署到单独的 GitHub Pages 仓库

set -e

echo "🚀 开始部署到 GitHub Pages..."

# 检查是否在 frontend 目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 请在 frontend 目录下运行此脚本"
    exit 1
fi

# 设置部署仓库信息（请根据你的实际仓库修改）
DEPLOY_REPO="https://github.com/dieWehmut/chatto1.0.0.git"
DEPLOY_BRANCH="main"  # 或者 "gh-pages"，根据你的设置

echo "📦 安装依赖..."
npm ci

echo "🔨 构建项目（生产模式）..."
npm run build:github

echo "📁 准备部署目录..."
cd dist

# 初始化 git 仓库
git init
git add .
git commit -m "Deploy to GitHub Pages - $(date '+%Y-%m-%d %H:%M:%S')"

echo "🌐 推送到 GitHub Pages 仓库..."
echo "仓库地址: $DEPLOY_REPO"
echo "分支: $DEPLOY_BRANCH"

# 添加远程仓库并推送
git remote add origin $DEPLOY_REPO
git branch -M $DEPLOY_BRANCH
git push -f origin $DEPLOY_BRANCH

echo "✅ 部署完成！"
echo "📡 你的应用应该很快可以在以下地址访问:"
echo "   https://diewehmut.github.io/chatto1.0.0"
echo ""
echo "🔗 API 配置:"
echo "   前端将连接到: https://hc.lan"
echo "   请确保 hc.lan 服务正在运行"

# 清理
cd ..
rm -rf dist
