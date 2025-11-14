@echo off
chcp 65001 >nul
echo ========================================
echo 安装 Anki Feynman Learning 插件依赖
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo 开始安装依赖到 vendor 目录...
echo.

REM 安装依赖到 vendor 目录
pip install -r requirements.txt -t vendor --upgrade

echo.
if errorlevel 1 (
    echo 安装失败！
) else (
    echo 安装成功！
    echo.
    echo 依赖已安装到 vendor 目录
)

echo.
pause

