@echo off
chcp 65001 > nul
title 复制 torch/ultralytics 到打包目录

:: ============================================================
:: 打包完成后执行此脚本
:: 把 torch、torchvision、ultralytics 手动复制进打包目录
:: ============================================================

set PYTHON_SITE=C:\Users\30542\AppData\Local\Programs\Python\Python310\Lib\site-packages
set DIST=C:\zhongyi-build\dist-commercial\ai-service-temp\tcm_ai_service

echo.
echo 正在检查打包目录结构...

:: 判断是新版 PyInstaller（有 _internal）还是旧版
if exist "%DIST%\_internal" (
    echo 检测到新版 PyInstaller，目标目录：_internal
    set TARGET=%DIST%\_internal
) else (
    echo 检测到旧版 PyInstaller，目标目录：tcm_ai_service 根目录
    set TARGET=%DIST%
)

echo 目标路径：%TARGET%
echo.

:: ── 复制 torch ──────────────────────────────────────────
echo [1/3] 正在复制 torch...（约 2~3GB，需要几分钟）
if not exist "%TARGET%\torch" (
    xcopy /E /Y /Q "%PYTHON_SITE%\torch" "%TARGET%\torch\"
    echo ✅ torch 复制完成
) else (
    echo ⚠️  torch 已存在，跳过
)

:: ── 复制 torchvision ────────────────────────────────────
echo [2/3] 正在复制 torchvision...
if not exist "%TARGET%\torchvision" (
    xcopy /E /Y /Q "%PYTHON_SITE%\torchvision" "%TARGET%\torchvision\"
    echo ✅ torchvision 复制完成
) else (
    echo ⚠️  torchvision 已存在，跳过
)

:: ── 复制 ultralytics ────────────────────────────────────
echo [3/3] 正在复制 ultralytics...
if not exist "%TARGET%\ultralytics" (
    xcopy /E /Y /Q "%PYTHON_SITE%\ultralytics" "%TARGET%\ultralytics\"
    echo ✅ ultralytics 复制完成
) else (
    echo ⚠️  ultralytics 已存在，跳过
)

:: ── 复制模型文件 ─────────────────────────────────────────
echo 正在复制 YOLO 模型文件...
if not exist "%DIST%\models" mkdir "%DIST%\models"
copy /Y "models\tongue_best.pt" "%DIST%\models\" > nul
echo ✅ 模型文件复制完成

:: ── 整理到最终目录 ───────────────────────────────────────
echo 正在整理到最终发布目录...
if not exist "C:\zhongyi-build\dist-commercial\ai-service" mkdir "C:\zhongyi-build\dist-commercial\ai-service"
xcopy /E /Y /Q "%DIST%\*" "C:\zhongyi-build\dist-commercial\ai-service\"
echo ✅ 整理完成

echo.
echo ============================================
echo   AI 服务打包完成！
echo   输出目录：C:\zhongyi-build\dist-commercial\ai-service\
echo ============================================
echo.
pause
