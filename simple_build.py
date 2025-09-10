#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版BUG管理系统打包脚本
使用目录模式构建，避免复杂依赖
"""

import os
import subprocess
import shutil
from pathlib import Path

def main():
    print("=" * 50)
    print("BUG管理系统 - 简化版打包工具")
    print("=" * 50)
    
    # 清理之前的构建
    if os.path.exists('dist'):
        print("清理之前的构建...")
        shutil.rmtree('dist')
    
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    print("开始构建简化版exe...")
    
    # 使用简化的PyInstaller命令
    cmd = [
        'pyinstaller',
        '--distpath=dist',
        '--workpath=build', 
        '--specpath=.',
        '--name=BUG管理系统',
        '--console',
        '--noconfirm',
        '--clean',
        '--add-data=app.py;.',
        '--add-data=database.py;.',
        'launcher.py'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        
        # 复制数据文件
        dist_dir = Path('dist/BUG管理系统')
        if dist_dir.exists():
            print("复制数据文件...")
            
            # 复制数据库文件
            if os.path.exists('bugs.db'):
                shutil.copy2('bugs.db', dist_dir / 'bugs.db')
                print("- 复制数据库文件")
            
            # 复制上传目录
            if os.path.exists('uploads'):
                shutil.copytree('uploads', dist_dir / 'uploads', dirs_exist_ok=True)
                print("- 复制上传目录")
            
            # 创建启动脚本
            start_script = dist_dir / "启动BUG管理系统.bat"
            with open(start_script, 'w', encoding='gb2312') as f:
                f.write('@echo off\n')
                f.write('title BUG管理系统\n')
                f.write('echo 正在启动BUG管理系统...\n')
                f.write('echo 系统将在浏览器中打开 http://localhost:8501\n')
                f.write('echo 按 Ctrl+C 可以退出程序\n')
                f.write('echo.\n')
                f.write('"BUG管理系统.exe"\n')
                f.write('pause\n')
            print("- 创建启动脚本")
            
            # 创建说明文件
            readme_content = '''BUG管理系统 v1.0

== 使用说明 ==

1. 双击运行 "启动BUG管理系统.bat" 或 "BUG管理系统.exe"
2. 程序会自动在浏览器中打开 http://localhost:8501
3. 如果浏览器没有自动打开，请手动访问该地址

== 默认账户 ==

管理员: admin / admin123
项目经理: pm / pm123
测试人员: tester / test123

== 功能特点 ==

✓ 用户权限控制
✓ BUG提交与管理
✓ 编辑和删除BUG
✓ 研发人员管理
✓ 数据统计分析
✓ Excel导出功能

== 技术支持 ==

- 数据保存在 bugs.db 文件中
- 上传文件保存在 uploads 目录中
- 按 Ctrl+C 退出程序
- 支持 Windows 7 及以上版本

== 注意事项 ==

- 请勿删除程序目录中的任何文件
- 建议定期备份 bugs.db 数据库文件
- 程序运行时保持控制台窗口打开
'''
            
            with open(dist_dir / 'README.txt', 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print("- 创建说明文件")
            
            print(f"\n{'=' * 50}")
            print("构建完成!")
            print(f"程序位置: {dist_dir}")
            print(f"启动方式: 双击 {dist_dir}/启动BUG管理系统.bat")
            print(f"{'=' * 50}")
            
            return True
        else:
            print("错误: 未找到构建输出目录")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

if __name__ == '__main__':
    main()