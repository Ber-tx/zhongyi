@echo off
chcp 65001
title TCM AI System Launcher

echo ===============================
echo 启动 中医AI诊断系统
echo ===============================

echo.

echo 启动 Spring Boot 后端服务...
start cmd /k "cd /d %~dp0demo && mvn spring-boot:run"

echo 启动 Flask AI 服务...
start cmd /k "cd /d %~dp0tcm-ai-service && python main.py"

timeout /t 2

echo 启动 脉搏算法服务...
start cmd /k "cd /d %~dp0pulse2 && python main.py"

timeout /t 2

echo 启动 Vue3 前端...
start cmd /k "cd /d %~dp0Vue/zhongyi && npm run dev"

echo 启动浏览器...
start http://localhost:5173


echo.
echo ===============================
echo 系统启动完成
echo ===============================

pause