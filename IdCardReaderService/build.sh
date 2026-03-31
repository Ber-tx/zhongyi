#!/bin/bash
# IdCardReaderService 构建、发布脚本

echo "=== 中医 AI - 身份证读卡服务 (x86) ==="
echo ""

# 检查 .NET SDK
if ! command -v dotnet &> /dev/null; then
    echo "错误: 未找到 .NET SDK"
    echo "请先安装 .NET 6.0 SDK from https://dotnet.microsoft.com/download"
    exit 1
fi

echo "构建配置："
echo "  Framework: .NET 6.0"
echo "  Platform: x86 (32-bit)"
echo "  Mode: Release"
echo ""

# 进入项目目录
cd IdCardReaderService

# 清理旧的构建
echo "清理旧文件..."
rm -rf bin/Release
dotnet clean

# 恢复依赖
echo "恢复 NuGet 包..."
dotnet restore

# 构建
echo "编译项目..."
dotnet build -c Release

if [ $? -ne 0 ]; then
    echo "编译失败!"
    exit 1
fi

# 发布
echo "发布应用..."
dotnet publish -c Release -r win-x86 --self-contained=true

if [ $? -ne 0 ]; then
    echo "发布失败!"
    exit 1
fi

echo ""
echo "✓ 构建完成！"
echo ""
echo "发布路径: ./bin/Release/net6.0/win-x86/publish/"
echo ""
echo "下一步："
echo "  1. 将读卡器 DLL 文件复制到 Libs/ 目录"
echo "  2. 重新运行此脚本进行发布"
echo "  3. 在目标 Windows x86 机器上运行: IdCardReaderService.exe"
echo ""
