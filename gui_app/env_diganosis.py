#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境诊断脚本 - 检查Python环境和依赖包问题
"""

import sys
import os
import subprocess
import importlib
import platform
import site
import json
from pathlib import Path

def check_python_version():
    """检查Python版本信息"""
    print("\n=== Python版本信息 ===")
    print(f"Python版本: {sys.version}")
    print(f"Python实现: {platform.python_implementation()}")
    print(f"Python可执行文件路径: {sys.executable}")
    return {
        "version": sys.version,
        "implementation": platform.python_implementation(),
        "executable": sys.executable
    }

def check_virtualenv():
    """检查是否在虚拟环境中"""
    print("\n=== 虚拟环境检查 ===")
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"是否在虚拟环境中: {'是' if in_venv else '否'}")
    
    if in_venv:
        print(f"虚拟环境路径: {sys.prefix}")
        print(f"基础Python路径: {sys.base_prefix}")
    
    return {
        "in_virtualenv": in_venv,
        "venv_path": sys.prefix if in_venv else None,
        "base_python_path": sys.base_prefix if in_venv else None
    }

def check_site_packages():
    """检查site-packages路径"""
    print("\n=== Site-packages路径 ===")
    site_packages = site.getsitepackages()
    print("Site-packages路径:")
    for path in site_packages:
        print(f"  - {path}")
        if os.path.exists(path):
            print(f"    状态: 存在")
        else:
            print(f"    状态: 不存在")
    
    return {
        "site_packages": site_packages,
        "site_packages_exist": [os.path.exists(path) for path in site_packages]
    }

def check_package_installed(package_name):
    """检查特定包是否已安装"""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', '未知版本')
        file_path = getattr(module, '__file__', '未知路径')
        return {
            "installed": True,
            "version": version,
            "file_path": file_path
        }
    except ImportError:
        return {
            "installed": False,
            "version": None,
            "file_path": None
        }

def check_specific_packages():
    """检查特定包的安装情况"""
    print("\n=== 特定包检查 ===")
    packages = [
        {"name": "sklearn", "import_name": "sklearn"},
        {"name": "scikit-learn", "import_name": "sklearn"},
        {"name": "beautifulsoup4", "import_name": "bs4"},
        {"name": "Pillow", "import_name": "PIL"},
        {"name": "pip", "import_name": "pip"},
        {"name": "setuptools", "import_name": "setuptools"}
    ]
    
    results = {}
    for pkg in packages:
        print(f"\n检查包: {pkg['name']}")
        result = check_package_installed(pkg['import_name'])
        results[pkg['name']] = result
        
        if result['installed']:
            print(f"  状态: 已安装")
            print(f"  版本: {result['version']}")
            print(f"  路径: {result['file_path']}")
        else:
            print(f"  状态: 未安装")
    
    return results

def check_pip_list():
    """检查pip list输出"""
    print("\n=== Pip List ===")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return {"success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        print(f"执行pip list失败: {e}")
        return {"success": False, "error": str(e)}

def check_path_environment():
    """检查PATH环境变量"""
    print("\n=== PATH环境变量 ===")
    paths = os.environ.get('PATH', '').split(os.pathsep)
    print("PATH环境变量包含的路径:")
    for path in paths:
        print(f"  - {path}")
    
    return {"paths": paths}

def check_python_path():
    """检查PYTHONPATH环境变量"""
    print("\n=== PYTHONPATH环境变量 ===")
    python_path = os.environ.get('PYTHONPATH', '')
    if python_path:
        paths = python_path.split(os.pathsep)
        print("PYTHONPATH环境变量包含的路径:")
        for path in paths:
            print(f"  - {path}")
            if os.path.exists(path):
                print(f"    状态: 存在")
            else:
                print(f"    状态: 不存在")
        return {"python_path": paths, "exists": [os.path.exists(path) for path in paths]}
    else:
        print("PYTHONPATH环境变量未设置")
        return {"python_path": None, "exists": None}

def check_import_error(package_name):
    """尝试导入包并捕获详细错误信息"""
    print(f"\n=== 尝试导入 {package_name} ===")
    try:
        importlib.import_module(package_name)
        print(f"成功导入 {package_name}")
        return {"success": True, "error": None}
    except ImportError as e:
        print(f"导入 {package_name} 失败: {e}")
        return {"success": False, "error": str(e)}

def check_specific_import_errors():
    """检查特定包的导入错误"""
    packages = ["sklearn", "bs4", "PIL"]
    results = {}
    for pkg in packages:
        results[pkg] = check_import_error(pkg)
    return results

def generate_diagnosis_report():
    """生成完整的诊断报告"""
    print("开始环境诊断...")
    
    # 收集所有诊断信息
    report = {
        "python_info": check_python_version(),
        "virtualenv": check_virtualenv(),
        "site_packages": check_site_packages(),
        "packages": check_specific_packages(),
        "pip_list": check_pip_list(),
        "path_env": check_path_environment(),
        "python_path": check_python_path(),
        "import_errors": check_specific_import_errors()
    }
    
    # 保存报告到JSON文件
    report_path = os.path.join(os.getcwd(), "env_diagnosis_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n诊断报告已保存到: {report_path}")
    return report

def main():
    """主函数"""
    try:
        report = generate_diagnosis_report()
        
        # 提供一些基本的故障排除建议
        print("\n=== 基本故障排除建议 ===")
        
        # 检查是否在虚拟环境中
        if not report["virtualenv"]["in_virtualenv"]:
            print("- 建议使用虚拟环境来隔离项目依赖")
        
        # 检查特定包是否安装
        missing_packages = []
        for pkg_name, pkg_info in report["packages"].items():
            if not pkg_info["installed"]:
                missing_packages.append(pkg_name)
        
        if missing_packages:
            print(f"- 以下包似乎未正确安装: {', '.join(missing_packages)}")
            print("  尝试使用以下命令重新安装:")
            for pkg in missing_packages:
                print(f"    pip install --force-reinstall {pkg}")
        
        # 检查导入错误
        import_errors = []
        for pkg_name, error_info in report["import_errors"].items():
            if not error_info["success"]:
                import_errors.append(pkg_name)
        
        if import_errors:
            print(f"- 以下包导入失败: {', '.join(import_errors)}")
            print("  可能的原因:")
            print("    1. 包安装不完整")
            print("    2. 包安装路径不在Python搜索路径中")
            print("    3. 包之间存在依赖冲突")
            print("    4. Python环境配置问题")
        
        # 检查pip list是否成功
        if not report["pip_list"]["success"]:
            print("- pip命令执行失败，可能pip本身有问题")
            print("  尝试重新安装pip:")
            print("    python -m ensurepip")
            print("    python -m pip install --upgrade pip")
        
        print("\n=== 诊断完成 ===")
        print("详细诊断报告已保存到 env_diagnosis_report.json")
        print("请检查报告中的详细信息，并根据上述建议进行故障排除")
        
    except Exception as e:
        print(f"诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()