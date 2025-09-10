#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUG管理系统 - 便携式发行版创建工具
创建包含Python环境的完整发行版
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_portable_release():
    """创建便携式发行版"""
    print("=" * 60)
    print("BUG管理系统 - 便携式发行版创建工具")
    print("=" * 60)
    
    # 创建发行版目录
    release_dir = Path("BUG管理系统_发行版")
    if release_dir.exists():
        print("清理旧的发行版...")
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    print(f"创建发行版目录: {release_dir}")
    
    # 复制核心文件
    core_files = ['app.py', 'database.py', 'requirements.txt']
    for file in core_files:
        if os.path.exists(file):
            shutil.copy2(file, release_dir / file)
            print(f"复制: {file}")
    
    # 复制数据文件
    if os.path.exists('bugs.db'):
        shutil.copy2('bugs.db', release_dir / 'bugs.db')
        print("复制: bugs.db")
    
    if os.path.exists('uploads'):
        shutil.copytree('uploads', release_dir / 'uploads')
        print("复制: uploads目录")
    
    # 创建便携式启动脚本
    start_script_content = '''@echo off
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
'''
    
    with open(release_dir / "启动BUG管理系统.bat", 'w', encoding='gb2312') as f:
        f.write(start_script_content)
    print("创建: 启动脚本")
    
    # 创建Linux/Mac启动脚本
    linux_script = '''#!/bin/bash

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
'''
    
    with open(release_dir / "启动BUG管理系统.sh", 'w', encoding='utf-8') as f:
        f.write(linux_script)
    
    # 设置执行权限（在Windows上不会生效，但不会出错）
    try:
        os.chmod(release_dir / "启动BUG管理系统.sh", 0o755)
    except:
        pass
    print("创建: Linux/Mac启动脚本")
    
    # 创建详细说明文档
    readme_content = '''# BUG管理系统 v1.0 - 便携式发行版

## 🚀 快速开始

### Windows用户
1. 双击运行 `启动BUG管理系统.bat`
2. 首次运行会自动安装依赖包（需要网络连接）
3. 系统会在浏览器中自动打开

### Linux/Mac用户
1. 打开终端，进入程序目录
2. 执行: `./启动BUG管理系统.sh`
3. 或执行: `bash 启动BUG管理系统.sh`

### 手动启动
```bash
# 安装依赖
pip install -r requirements.txt

# 启动系统
streamlit run app.py
```

## 🔑 默认账户

| 角色 | 用户名 | 密码 | 权限说明 |
|------|--------|------|----------|
| 管理员 | admin | admin123 | 全部权限 |
| 项目经理 | pm | pm123 | BUG管理、人员查看 |
| 测试人员 | tester | test123 | BUG提交、查看 |

## 📋 功能特点

✅ **权限控制**: 基于角色的访问控制  
✅ **BUG管理**: 提交、编辑、删除、分配  
✅ **用户管理**: 用户账户和权限管理  
✅ **数据统计**: 多维度统计分析和可视化  
✅ **文件管理**: 截图和日志文件上传  
✅ **数据导出**: Excel格式导出功能  

## 🛠️ 系统要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows 7+, macOS 10.12+, Linux
- **浏览器**: Chrome, Firefox, Safari, Edge
- **网络**: 首次运行需要网络连接安装依赖

## 📁 文件说明

```
BUG管理系统_发行版/
├── app.py                    # 主应用程序
├── database.py               # 数据库操作模块
├── requirements.txt          # Python依赖包列表
├── bugs.db                   # SQLite数据库文件
├── uploads/                  # 上传文件目录
├── 启动BUG管理系统.bat        # Windows启动脚本
├── 启动BUG管理系统.sh         # Linux/Mac启动脚本
└── README.md                 # 说明文档

```

## 🔧 配置说明

### 默认设置
- **端口**: 8501
- **数据库**: bugs.db (SQLite)
- **上传目录**: uploads/
- **访问地址**: http://localhost:8501

### 修改配置
如需修改端口或其他设置，可编辑启动脚本中的参数：
```bash
streamlit run app.py --server.port=YOUR_PORT
```

## 📊 数据管理

### 数据备份
定期备份以下文件：
- `bugs.db` - 所有BUG和用户数据
- `uploads/` - 上传的截图和日志文件

### 数据恢复
将备份的文件复制回程序目录即可

## 🐛 故障排除

### 常见问题

1. **Python未找到**
   - 确保已安装Python 3.7+
   - 将Python添加到系统PATH

2. **依赖安装失败**
   - 检查网络连接
   - 手动执行: `pip install -r requirements.txt`

3. **端口占用**
   - 修改启动脚本中的端口号
   - 或关闭占用8501端口的程序

4. **浏览器不自动打开**
   - 手动访问: http://localhost:8501
   - 检查防火墙设置

### 日志查看
程序运行时的详细日志会显示在控制台中，如遇问题请查看错误信息。

## 📞 技术支持

如遇问题，请提供以下信息：
- 操作系统版本
- Python版本
- 错误信息截图
- 控制台日志输出

## 📄 许可证

本软件仅供学习和内部使用，请勿用于商业用途。

---
*BUG管理系统 v1.0 - 轻量级本地BUG跟踪解决方案*
'''
    
    with open(release_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("创建: 详细说明文档")
    
    # 创建压缩包
    print("\n正在创建压缩包...")
    with zipfile.ZipFile("BUG管理系统_v1.0_便携版.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, release_dir.parent)
                zipf.write(file_path, arc_name)
    
    print("✅ 压缩包创建完成: BUG管理系统_v1.0_便携版.zip")
    
    print("\n" + "=" * 60)
    print("🎉 便携式发行版创建完成!")
    print("=" * 60)
    print(f"📁 发行版目录: {release_dir.absolute()}")
    print(f"📦 压缩包: BUG管理系统_v1.0_便携版.zip")
    print("\n📋 使用说明:")
    print("1. 解压压缩包到任意目录")
    print("2. Windows: 双击 '启动BUG管理系统.bat'")
    print("3. Linux/Mac: 执行 './启动BUG管理系统.sh'")
    print("4. 首次运行会自动安装依赖包")
    print("5. 在浏览器中访问 http://localhost:8501")
    print("=" * 60)

if __name__ == '__main__':
    create_portable_release()