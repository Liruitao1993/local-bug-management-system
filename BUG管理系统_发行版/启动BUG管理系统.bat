@echo off
title BUG管理系统
echo.
echo ========================================
echo    BUG管理系统 v1.0 - 便携式版本
echo ========================================
echo.
echo 正在检查Python环境...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo.
    echo 请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python环境检查通过
echo.
echo 正在安装依赖包...
python -m pip install -r requirements.txt --quiet --user

if %errorlevel% neq 0 (
    echo.
    echo 警告: 某些依赖包安装失败，但仍可尝试运行
    echo.
)

echo.
echo 正在启动BUG管理系统...
echo 系统将在浏览器中打开: http://localhost:8501
echo 按 Ctrl+C 可以退出程序
echo.
echo ========================================
echo.

python -m streamlit run app.py --server.headless=true --server.port=8501

if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查错误信息
    echo.
    pause
)
