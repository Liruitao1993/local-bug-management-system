#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUG管理系统 - PyInstaller 打包脚本
用于将Streamlit应用程序打包成Windows可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理.spec文件
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        print(f"清理文件: {spec_file}")
        spec_file.unlink()

def create_streamlit_launcher():
    """创建Streamlit启动器"""
    launcher_content = '''#!/usr/bin/env python3
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
        print("\\n程序已退出")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()
'''
    
    with open('streamlit_launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    print("创建Streamlit启动器: streamlit_launcher.py")

def create_pyinstaller_spec():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import streamlit as st
from pathlib import Path

# 获取Streamlit安装路径
streamlit_path = Path(st.__file__).parent

# 收集Streamlit相关数据文件
streamlit_datas = [
    (str(streamlit_path / "static"), "streamlit/static"),
    (str(streamlit_path / "runtime"), "streamlit/runtime"),
]

# 收集项目数据文件
project_datas = [
    ('app.py', '.'),
    ('database.py', '.'),
    ('requirements.txt', '.'),
]

# 隐含导入
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.state',
    'streamlit.components.v1',
    'pandas',
    'plotly',
    'plotly.express',
    'plotly.graph_objects',
    'openpyxl',
    'sqlite3',
    'hashlib',
    'secrets',
    'threading',
    'io',
    'os',
    'time',
]

block_cipher = None

a = Analysis(
    ['streamlit_launcher.py'],
    pathex=[],
    binaries=[],
    datas=streamlit_datas + project_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BUG管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('bug_manager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("创建PyInstaller配置文件: bug_manager.spec")

def build_executable():
    """执行打包构建"""
    print("开始构建可执行文件...")
    
    # 使用PyInstaller进行打包
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm', 
        'bug_manager.spec'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def copy_additional_files():
    """复制额外的文件到dist目录"""
    dist_dir = Path('dist/BUG管理系统')
    if not dist_dir.exists():
        print("dist目录不存在，跳过文件复制")
        return
    
    # 复制数据库文件（如果存在）
    if os.path.exists('bugs.db'):
        shutil.copy2('bugs.db', dist_dir / 'bugs.db')
        print("复制数据库文件: bugs.db")
    
    # 复制上传目录（如果存在）
    if os.path.exists('uploads'):
        shutil.copytree('uploads', dist_dir / 'uploads', dirs_exist_ok=True)
        print("复制上传目录: uploads")
    
    # 创建README文件
    readme_content = '''# BUG管理系统

## 使用说明

1. 双击运行 "BUG管理系统.exe"
2. 程序会自动在浏览器中打开 http://localhost:8501
3. 如果浏览器没有自动打开，请手动访问该地址

## 默认账户

- 管理员: admin / admin123
- 项目经理: pm / pm123  
- 测试人员: tester / test123

## 注意事项

- 程序运行时请保持控制台窗口打开
- 数据保存在程序同目录的 bugs.db 文件中
- 上传的文件保存在 uploads 目录中
- 按 Ctrl+C 可以退出程序

## 系统要求

- Windows 7 或更高版本
- 无需安装Python环境
'''
    
    with open(dist_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("创建说明文件: README.txt")

def main():
    """主函数"""
    print("=" * 50)
    print("BUG管理系统 - 可执行文件构建工具")
    print("=" * 50)
    
    # 步骤1: 清理构建目录
    print("\\n步骤1: 清理之前的构建文件")
    clean_build_dirs()
    
    # 步骤2: 创建启动器
    print("\\n步骤2: 创建Streamlit启动器")
    create_streamlit_launcher()
    
    # 步骤3: 创建PyInstaller配置
    print("\\n步骤3: 创建PyInstaller配置文件")
    create_pyinstaller_spec()
    
    # 步骤4: 执行构建
    print("\\n步骤4: 执行PyInstaller构建")
    if build_executable():
        # 步骤5: 复制额外文件
        print("\\n步骤5: 复制额外文件")
        copy_additional_files()
        
        print("\\n" + "=" * 50)
        print("构建完成!")
        print("可执行文件位置: dist/BUG管理系统/BUG管理系统.exe")
        print("=" * 50)
        
        # 询问是否立即测试
        response = input("\\n是否立即测试exe文件? (y/n): ")
        if response.lower() in ['y', 'yes', '是']:
            test_executable()
    else:
        print("\\n构建失败，请检查错误信息")

def test_executable():
    """测试可执行文件"""
    exe_path = Path('dist/BUG管理系统/BUG管理系统.exe')
    if exe_path.exists():
        print(f"\\n正在启动: {exe_path}")
        try:
            subprocess.Popen([str(exe_path)], cwd=exe_path.parent)
            print("程序已启动，请检查浏览器是否打开了应用")
        except Exception as e:
            print(f"启动失败: {e}")
    else:
        print("找不到可执行文件")

if __name__ == '__main__':
    main()