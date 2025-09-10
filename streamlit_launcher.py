#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUG管理系统启动器
这个文件用于在exe环境中正确启动Streamlit应用
"""

import sys
import os
from pathlib import Path
import streamlit.web.cli as stcli

def main():
    """主启动函数"""
    # 获取当前执行文件的目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe运行
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是Python脚本运行
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # 设置工作目录
    os.chdir(application_path)
    
    # 设置Streamlit配置
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    
    # Streamlit应用文件路径
    app_file = os.path.join(application_path, 'app.py')
    
    if not os.path.exists(app_file):
        print(f"错误: 找不到应用文件 {app_file}")
        sys.exit(1)
    
    print("正在启动BUG管理系统...")
    print("系统将在浏览器中自动打开")
    print("如果没有自动打开，请访问: http://localhost:8501")
    print("按 Ctrl+C 退出程序")
    
    # 模拟命令行参数启动Streamlit
    sys.argv = ['streamlit', 'run', app_file, '--server.headless=true']
    
    try:
        stcli.main()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()
