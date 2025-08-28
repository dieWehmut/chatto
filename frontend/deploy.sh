#!/bin/bash

# 前端构建并推送到 GitHub Pages 的脚本

echo "=== 开始构建前端项目 ==="

# 检查是否存在 node_modules
if [ ! -d "node_modules" ]; then
    echo "安装依赖包..."
    npm install
fi

# 构建项目
echo "构建生产版本..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 构建失败!"
    exit 1
fi

echo "✅ 构建完成!"

# 检查 dist 目录是否存在
if [ ! -d "dist" ]; then
    echo "❌ dist 目录不存在，构建可能失败"
    exit 1
fi

echo "=== 准备推送到 GitHub ==="

# 进入 dist 目录
cd dist

# 初始化 git 仓库（如果不存在）
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# 添加所有文件
git add .

# 提交
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"

# 添加远程仓库（如果不存在）
if ! git remote | grep -q origin; then
    git remote add origin https://github.com/dieWehmut/chatto1.0.0.git
fi

# 推送到 GitHub
echo "推送到 GitHub..."
git push -f origin main

if [ $? -eq 0 ]; then
    echo "✅ 成功推送到 GitHub!"
    echo "🌐 您的网站将在几分钟内部署到: https://diewehmut.github.io/chatto1.0.0"
else
    echo "❌ 推送失败，请检查 GitHub 权限"
    exit 1
fi

echo "=== 部署完成 ==="
