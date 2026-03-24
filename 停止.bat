@echo off
chcp 65001
echo 正在停止系统...
docker-compose down
echo 系统已停止
pause