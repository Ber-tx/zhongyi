@echo off
setlocal

chcp 65001 >nul 2>nul

echo =================================
echo   ID Card Reader Service (x86)
echo =================================
echo.

where dotnet >nul 2>nul
if errorlevel 1 (
    echo [ERROR] dotnet runtime not found.
    echo Install .NET 8 runtime first: https://dotnet.microsoft.com/download
    pause
    exit /b 1
)

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%IdCardReaderService"
set "PUBLISH_DIR=%PROJECT_DIR%\bin\Release\net8.0\win-x86\publish"

if not exist "%PROJECT_DIR%\IdCardReaderService.csproj" (
    echo [ERROR] Project file not found:
    echo %PROJECT_DIR%\IdCardReaderService.csproj
    pause
    exit /b 1
)

echo Listening: http://127.0.0.1:9009
echo Health   : http://127.0.0.1:9009/api/idcard/health
echo Press CTRL+C to stop.
echo.

if exist "%PUBLISH_DIR%\IdCardReaderService.dll" (
    cd /d "%PUBLISH_DIR%"
    dotnet "IdCardReaderService.dll"
) else (
    echo [INFO] Publish output not found, fallback to dotnet run...
    cd /d "%PROJECT_DIR%"
    dotnet restore "%PROJECT_DIR%\IdCardReaderService.csproj" --configfile "%SCRIPT_DIR%NuGet.config" --ignore-failed-sources
    if errorlevel 1 (
        echo [ERROR] dotnet restore failed.
        pause
        exit /b 1
    )

    dotnet build "%PROJECT_DIR%\IdCardReaderService.csproj" -c Release --no-restore
    if errorlevel 1 (
        echo [ERROR] dotnet build failed.
        pause
        exit /b 1
    )

    dotnet run --project "%PROJECT_DIR%\IdCardReaderService.csproj" -c Release --no-build
)

pause
