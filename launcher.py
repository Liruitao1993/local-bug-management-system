#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版BUG管理系统启动器
用于PyInstaller打包
"""

import sys
import os
import webbrowser
import subprocess
import time
from pathlib import Path

def main():
    """主启动函数"""
    print("正在启动BUG管理系统...")
    
    # 获取当前执行文件的目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe运行
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是Python脚本运行
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # 设置工作目录
    os.chdir(application_path)
    
    # Streamlit应用文件路径
    app_file = os.path.join(application_path, 'app.py')
    
    if not os.path.exists(app_file):
        print(f"错误: 找不到应用文件 {app_file}")
        input("按回车键退出...")
        sys.exit(1)
    
    print("系统将在浏览器中自动打开")
    print("访问地址: http://localhost:8501")
    print("按 Ctrl+C 退出程序")
    print("-" * 50)
    
    try:
        # 启动Streamlit应用
        cmd = [sys.executable, '-m', 'streamlit', 'run', app_file, '--server.headless=true', '--server.port=8501']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待服务启动
        time.sleep(3)
        
        # 尝试打开浏览器
        try:
            webbrowser.open('http://localhost:8501')
        except:
            print("无法自动打开浏览器，请手动访问: http://localhost:8501")
        
        print("服务已启动，请检查浏览器")
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()