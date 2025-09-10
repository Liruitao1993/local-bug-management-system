#!/bin/bash

echo "========================================"
echo "   BUG管理系统 v1.0 - 便携式版本"
echo "========================================"
echo

echo "正在检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3环境"
    echo "请先安装Python 3.7或更高版本"
    exit 1
fi

echo "Python环境检查通过"
echo

echo "正在安装依赖包..."
python3 -m pip install -r requirements.txt --quiet --user

echo
echo "正在启动BUG管理系统..."
echo "系统将在浏览器中打开: http://localhost:8501"
echo "按 Ctrl+C 可以退出程序"
echo
echo "========================================"
echo

python3 -m streamlit run app.py --server.headless=true --server.port=8501
