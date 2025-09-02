#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖安装脚本
用于直接安装系统Python环境下的必要依赖包
"""

import os
import sys
import subprocess
import importlib

# 定义常量
REQUIREMENTS_FILE = "requirements.txt"
MAIN_REQUIREMENTS = ["scikit-learn", "beautifulsoup4", "Pillow"]

def run_command(command, check=True):
    """
    执行命令并处理错误
    
    Args:
        command (str): 要执行的命令
        check (bool, optional): 是否检查返回码
    
    Returns:
        subprocess.CompletedProcess: 命令执行结果
    """
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if check:
            sys.exit(1)
        return e

def check_python_version():
    """检查Python版本是否满足要求"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("错误: 需要Python 3.6或更高版本")
        sys.exit(1)
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")

def upgrade_pip():
    """升级pip到最新版本"""
    print("升级pip...")
    pip_command = "pip3" if os.path.exists("/usr/bin/pip3") else "pip"
    run_command(f"{pip_command} install --upgrade pip")

def install_requirements():
    """安装requirements.txt中的所有依赖"""
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"警告: 未找到 {REQUIREMENTS_FILE} 文件")
        return
    
    print(f"从 {REQUIREMENTS_FILE} 安装依赖...")
    pip_command = "pip3" if os.path.exists("/usr/bin/pip3") else "pip"
    run_command(f"{pip_command} install -r {REQUIREMENTS_FILE}")

def install_main_requirements():
    """安装主要依赖包"""
    print("安装主要依赖包...")
    pip_command = "pip3" if os.path.exists("/usr/bin/pip3") else "pip"
    for package in MAIN_REQUIREMENTS:
        print(f"安装 {package}...")
        run_command(f"{pip_command} install {package}")

def check_package_installed(package_name):
    """
    检查包是否已安装
    
    Args:
        package_name (str): 包名
    
    Returns:
        bool: 是否已安装
    """
    try:
        # 将包名转换为导入名
        import_name = package_name
        if package_name == "scikit-learn":
            import_name = "sklearn"
        elif package_name == "beautifulsoup4":
            import_name = "bs4"
        elif package_name == "Pillow":
            import_name = "PIL"
            
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def verify_installation():
    """验证主要依赖包是否安装成功"""
    print("验证安装...")
    python_command = "python3" if os.path.exists("/usr/bin/python3") else "python"
    
    for package in MAIN_REQUIREMENTS:
        try:
            # 将包名转换为导入名
            import_name = package
            if package == "scikit-learn":
                import_name = "sklearn"
            elif package == "beautifulsoup4":
                import_name = "bs4"
            elif package == "Pillow":
                import_name = "PIL"
                
            result = run_command(
                f'{python_command} -c "import {import_name}; print(f\'{package} 版本: {{getattr({import_name}, \"__version__\", \"未知\")}}\')"',
                check=False
            )
            if result.returncode != 0:
                print(f"错误: {package} 安装失败")
                return False
        except Exception as e:
            print(f"验证 {package} 时出错: {e}")
            return False
    
    print("所有主要依赖包安装成功")
    return True

def main():
    """主函数"""
    print("开始安装依赖...")
    
    # 检查Python版本
    check_python_version()
    
    # 升级pip
    upgrade_pip()
    
    # 安装依赖
    install_requirements()
    install_main_requirements()
    
    # 验证安装
    if verify_installation():
        print("依赖安装完成!")
    else:
        print("依赖安装失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()