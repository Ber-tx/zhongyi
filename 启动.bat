@echo off
chcp 65001
title 中医体质辨识系统

echo.
echo  ================================
echo    中医体质辨识系统 正在启动...
echo  ================================
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 没有检测到 Docker，请先安装 Docker Desktop
    echo 下载地址：https://www.docker.com/products/docker-desktop
    pause
    exit
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [提示] Docker 未运行，正在启动请等待约30秒...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 30 /nobreak >nul
)

docker image inspect zhongyi-frontend >nul 2>&1
if errorlevel 1 (
    echo [首次运行] 正在导入系统镜像，约需5-10分钟，请勿关闭窗口...
    docker load -i zhongyi-images.tar
    echo 镜像导入完成！
)

echo 正在启动所有服务...
docker-compose up -d

echo 等待服务就绪...
timeout /t 20 /nobreak >nul

echo.
echo  ================================
echo    启动完成！
echo    浏览器访问：http://localhost
echo  ================================
echo.
start http://localhost
pause