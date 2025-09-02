#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单命令运行脚本
用于检查依赖安装状态、自动安装缺失依赖并运行主程序
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

# 定义常量
VENV_NAME = "venv"
REQUIREMENTS_FILE = "requirements.txt"
MAIN_REQUIREMENTS = ["scikit-learn", "beautifulsoup4", "Pillow"]
MAIN_PROGRAM = "start.py"

def run_command(command, cwd=None, check=True):
    """
    执行命令并处理错误
    
    Args:
        command (str): 要执行的命令
        cwd (str, optional): 工作目录
        check (bool, optional): 是否检查返回码
    
    Returns:
        subprocess.CompletedProcess: 命令执行结果
    """
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
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

def get_pip_path():
    """获取虚拟环境中的pip路径"""
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(VENV_NAME, "Scripts", "pip")
    else:  # Unix/Linux/MacOS
        pip_path = os.path.join(VENV_NAME, "bin", "pip")
    return pip_path

def get_python_path():
    """获取虚拟环境中的python路径"""
    if os.name == 'nt':  # Windows
        python_path = os.path.join(VENV_NAME, "Scripts", "python")
    else:  # Unix/Linux/MacOS
        python_path = os.path.join(VENV_NAME, "bin", "python")
    return python_path

def check_venv_exists():
    """检查虚拟环境是否存在"""
    venv_path = Path(VENV_NAME)
    return venv_path.exists()

def create_virtual_environment():
    """创建新的虚拟环境"""
    print(f"创建新的虚拟环境: {VENV_NAME}")
    try:
        import venv
        venv.create(VENV_NAME, with_pip=True)
        print("虚拟环境创建成功")
        return True
    except Exception as e:
        print(f"创建虚拟环境失败: {e}")
        return False

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

def check_dependencies():
    """检查所有依赖是否已安装"""
    print("检查依赖安装状态...")
    missing_packages = []
    
    for package in MAIN_REQUIREMENTS:
        if not check_package_installed(package):
            missing_packages.append(package)
            print(f"缺失依赖: {package}")
        else:
            print(f"依赖已安装: {package}")
    
    return missing_packages

def install_missing_packages(packages):
    """
    安装缺失的包
    
    Args:
        packages (list): 缺失的包列表
    
    Returns:
        bool: 是否全部安装成功
    """
    if not packages:
        return True
    
    print("安装缺失的依赖...")
    pip_path = get_pip_path()
    
    # 如果虚拟环境不存在，尝试创建
    if not check_venv_exists():
        print("虚拟环境不存在，尝试创建...")
        if not create_virtual_environment():
            print("无法创建虚拟环境，尝试使用系统Python安装")
            pip_path = "pip"
    
    # 升级pip
    run_command(f"{pip_path} install --upgrade pip", check=False)
    
    # 安装缺失的包
    for package in packages:
        print(f"安装 {package}...")
        result = run_command(f"{pip_path} install {package}", check=False)
        if result.returncode != 0:
            print(f"安装 {package} 失败")
            return False
    
    return True

def run_main_program():
    """运行主程序"""
    if not os.path.exists(MAIN_PROGRAM):
        print(f"错误: 找不到主程序 {MAIN_PROGRAM}")
        return False
    
    print(f"运行主程序 {MAIN_PROGRAM}...")
    
    # 如果虚拟环境存在，使用虚拟环境中的Python
    if check_venv_exists():
        python_path = get_python_path()
    else:
        python_path = "python"
    
    # 运行主程序
    result = run_command(f"{python_path} {MAIN_PROGRAM}", check=False)
    return result.returncode == 0

def main():
    """主函数"""
    print("系统启动中...")
    
    # 检查依赖
    missing_packages = check_dependencies()
    
    # 如果有缺失的依赖，尝试安装
    if missing_packages:
        print("发现缺失的依赖，尝试自动安装...")
        if not install_missing_packages(missing_packages):
            print("无法自动安装所有依赖，请手动安装以下包:")
            for package in missing_packages:
                print(f"  - {package}")
            print("然后重试运行此脚本")
            sys.exit(1)
        
        # 再次检查依赖
        missing_packages = check_dependencies()
        if missing_packages:
            print("以下依赖仍然缺失:")
            for package in missing_packages:
                print(f"  - {package}")
            print("请手动安装这些依赖，然后重试")
            sys.exit(1)
    
    print("所有依赖已满足，准备运行主程序...")
    
    # 运行主程序
    if run_main_program():
        print("程序执行完成")
    else:
        print("程序执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main()