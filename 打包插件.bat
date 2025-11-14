@echo off
chcp 65001 >nul
echo ========================================
echo Anki Feynman Learning 插件打包工具
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo 开始打包插件...
echo.

REM 运行打包脚本
python build_addon.py

echo.
if errorlevel 1 (
    echo 打包失败！
) else (
    echo 打包成功！
)

echo.
pause

