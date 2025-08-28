@echo off
setlocal

echo === 开始构建前端项目 ===

REM 检查是否存在 node_modules
if not exist "node_modules" (
    echo 安装依赖包...
    npm install
)

REM 构建项目
echo 构建生产版本...
npm run build

if %errorlevel% neq 0 (
    echo ❌ 构建失败!
    exit /b 1
)

echo ✅ 构建完成!

REM 检查 dist 目录是否存在
if not exist "dist" (
    echo ❌ dist 目录不存在，构建可能失败
    exit /b 1
)

echo === 准备推送到 GitHub ===

REM 进入 dist 目录
cd dist

REM 初始化 git 仓库（如果不存在）
if not exist ".git" (
    git init
    git branch -M main
)

REM 添加所有文件
git add .

REM 提交
git commit -m "Deploy: %date% %time%"

REM 添加远程仓库（如果不存在）
git remote | findstr origin >nul
if %errorlevel% neq 0 (
    git remote add origin https://github.com/dieWehmut/chatto1.0.0.git
)

REM 推送到 GitHub
echo 推送到 GitHub...
git push -f origin main

if %errorlevel% equ 0 (
    echo ✅ 成功推送到 GitHub!
    echo 🌐 您的网站将在几分钟内部署到: https://diewehmut.github.io/chatto1.0.0
) else (
    echo ❌ 推送失败，请检查 GitHub 权限
    exit /b 1
)

echo === 部署完成 ===
pause
