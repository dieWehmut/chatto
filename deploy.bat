@echo off
echo HCChat 部署工具
echo.
echo 请选择部署目标:
echo 1. 构建前端 (用于 GitHub Pages)
echo 2. 准备 Debian 服务器部署文件
echo 3. 查看部署状态
echo.

set /p choice=请输入选项 (1-3): 

if "%choice%"=="1" goto build_frontend
if "%choice%"=="2" goto prepare_debian
if "%choice%"=="3" goto check_status
goto end

:build_frontend
echo 开始构建前端...
cd frontend
call npm install
if %ERRORLEVEL% neq 0 (
    echo NPM 安装失败
    cd ..
    goto end
)

call npm run build:github
if %ERRORLEVEL% neq 0 (
    echo 构建失败，退出部署
    cd ..
    goto end
)

echo 前端构建完成！
echo 构建产物在 frontend/dist 目录中
echo.
echo GitHub Actions 将自动处理部署
echo 请推送代码到 main 分支以触发自动部署
cd ..
goto end

:prepare_debian
echo 准备 Debian 部署文件...
echo 正在检查必需文件...
if not exist "nginx.conf" echo 错误: nginx.conf 不存在
if not exist "systemd_service.conf" echo 错误: systemd_service.conf 不存在
if not exist "deploy_debian.sh" echo 错误: deploy_debian.sh 不存在
echo.
echo 部署准备清单:
echo ✓ nginx.conf - Nginx 配置文件
echo ✓ systemd_service.conf - 系统服务配置
echo ✓ deploy_debian.sh - 自动部署脚本
echo ✓ backend/.env.example - 环境配置模板
echo.
echo 下一步: 执行 deploy_debian.sh 脚本进行服务器部署
echo 使用方法: bash deploy_debian.sh [服务器IP] [用户名]
goto end

:check_status
echo 检查部署状态...
echo.
echo 要检查的项目:
echo 1. GitHub Actions 状态: https://github.com/dieWehmut/chatto/actions
echo 2. GitHub Pages 地址: https://dieWehmut.github.io/chatto/
echo 3. 服务器状态需要登录服务器查看
echo.
goto end

:end
echo.
pause
