#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_pythonpath():
    """检查当前PYTHONPATH环境变量"""
    print("当前PYTHONPATH环境变量:")
    pythonpath = os.environ.get('PYTHONPATH', '')
    if pythonpath:
        print(pythonpath)
        paths = pythonpath.split(os.pathsep)
        print(f"\nPYTHONPATH包含{len(paths)}个路径:")
        for i, path in enumerate(paths, 1):
            exists = "存在" if os.path.exists(path) else "不存在"
            print(f"{i}. {path} ({exists})")
    else:
        print("PYTHONPATH未设置")
    return pythonpath

def check_python_paths():
    """检查Python模块搜索路径"""
    print("\nPython模块搜索路径(sys.path):")
    for i, path in enumerate(sys.path, 1):
        exists = "存在" if os.path.exists(path) else "不存在"
        print(f"{i}. {path} ({exists})")

def check_virtualenv():
    """检查是否在虚拟环境中"""
    print("\n虚拟环境检查:")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("当前处于虚拟环境中")
        print(f"虚拟环境路径: {sys.prefix}")
        return True
    else:
        print("当前不在虚拟环境中")
        return False

def explain_pythonpath():
    """解释PYTHONPATH的作用和重要性"""
    print("\n=== PYTHONPATH环境变量详解 ===")
    print("1. PYTHONPATH的作用:")
    print("   - PYTHONPATH是Python解释器用来搜索模块的环境变量")
    print("   - 它告诉Python解释器在哪些目录中查找导入的模块")
    print("   - 它会添加到sys.path列表的前面，优先于标准库路径被搜索")
    
    print("\n2. PYTHONPATH的重要性:")
    print("   - 允许导入不在标准位置的模块")
    print("   - 方便开发过程中测试本地模块")
    print("   - 可以覆盖标准库中的同名模块(需谨慎使用)")
    
    print("\n3. 为什么PYTHONPATH未设置时依赖包仍能正常导入:")
    print("   - Python解释器有默认的模块搜索路径")
    print("   - 虚拟环境(.venv)会自动将site-packages目录添加到sys.path")
    print("   - pip安装的包会放在site-packages目录中")
    print("   - Python解释器会按以下顺序搜索模块:")
    print("     a. 当前目录")
    print("     b. PYTHONPATH中的目录(如果设置了)")
    print("     c. 标准库目录")
    print("     d. site-packages目录(第三方包安装位置)")
    print("     e. 其他系统特定路径")

def setup_pythonpath_recommendation():
    """提供设置PYTHONPATH的建议"""
    print("\n=== PYTHONPATH设置建议 ===")
    print("1. 虚拟环境中是否需要设置PYTHONPATH:")
    print("   - 通常情况下，虚拟环境中不需要设置PYTHONPATH")
    print("   - 虚拟环境已经自动配置了正确的模块搜索路径")
    print("   - 如果项目结构特殊，可能需要添加项目根目录到PYTHONPATH")
    
    print("\n2. 如何设置PYTHONPATH:")
    print("   - 临时设置(仅当前终端会话有效):")
    print("     export PYTHONPATH=/path/to/your/modules:$PYTHONPATH")
    print("   - 永久设置(添加到shell配置文件):")
    print("     echo 'export PYTHONPATH=/path/to/your/modules:$PYTHONPATH' >> ~/.bashrc")
    print("     source ~/.bashrc")
    
    print("\n3. 避免PYTHONPATH相关问题的最佳实践:")
    print("   - 尽量避免设置全局PYTHONPATH")
    print("   - 在虚拟环境中使用相对导入或绝对导入")
    print("   - 使用setup.py或pyproject.toml正确配置项目")
    print("   - 考虑使用.pth文件代替PYTHONPATH")
    print("   - 在代码中动态修改sys.path(作为最后手段)")

def create_setup_script():
    """创建环境变量设置脚本"""
    print("\n=== 创建环境变量设置脚本 ===")
    
    # 确定shell类型
    shell = os.environ.get('SHELL', '/bin/bash')
    shell_config = None
    if 'bash' in shell:
        shell_config = os.path.expanduser('~/.bashrc')
    elif 'zsh' in shell:
        shell_config = os.path.expanduser('~/.zshrc')
    elif 'fish' in shell:
        shell_config = os.path.expanduser('~/.config/fish/config.fish')
    
    # 创建设置脚本
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setup_pythonpath.sh')
    with open(script_path, 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('# PYTHONPATH环境变量设置脚本\n\n')
        f.write('# 检查是否在虚拟环境中\n')
        f.write('if [[ -n "$VIRTUAL_ENV" ]]; then\n')
        f.write('    echo "检测到虚拟环境: $VIRTUAL_ENV"\n')
        f.write('    echo "在虚拟环境中，通常不需要设置PYTHONPATH"\n')
        f.write('    echo "如果确实需要设置，请确保路径包含项目根目录"\n')
        f.write('    read -p "是否要继续设置PYTHONPATH? (y/n): " answer\n')
        f.write('    if [[ "$answer" != "y" ]]; then\n')
        f.write('        exit 0\n')
        f.write('    fi\n')
        f.write('fi\n\n')
        f.write('# 获取当前PYTHONPATH\n')
        f.write('current_pythonpath=$PYTHONPATH\n\n')
        f.write('# 询问用户要添加的路径\n')
        f.write('read -p "请输入要添加到PYTHONPATH的路径(多个路径用冒号分隔): " new_paths\n\n')
        f.write('# 设置新的PYTHONPATH\n')
        f.write('if [[ -n "$current_pythonpath" ]]; then\n')
        f.write('    export PYTHONPATH="$new_paths:$current_pythonpath"\n')
        f.write('else\n')
        f.write('    export PYTHONPATH="$new_paths"\n')
        f.write('fi\n\n')
        f.write('echo "PYTHONPATH已设置为: $PYTHONPATH"\n\n')
        f.write('# 询问是否永久保存\n')
        f.write('read -p "是否要永久保存此设置? (y/n): " save_answer\n')
        f.write('if [[ "$save_answer" == "y" ]]; then\n')
        if shell_config:
            f.write(f'    echo "export PYTHONPATH=\\"$PYTHONPATH\\"" >> {shell_config}\n')
            f.write(f'    echo "设置已保存到 {shell_config}"\n')
            f.write(f'    echo "请运行以下命令使设置生效: source {shell_config}"\n')
        else:
            f.write('    echo "无法确定shell配置文件，请手动将以下行添加到您的shell配置文件中:"\n')
            f.write('    echo "export PYTHONPATH=\\"$PYTHONPATH\\""\n')
        f.write('fi\n')
    
    # 使脚本可执行
    os.chmod(script_path, 0o755)
    print(f"已创建设置脚本: {script_path}")
    print("运行此脚本可以交互式地设置PYTHONPATH")
    
    return script_path

def create_pythonpath_checker():
    """创建PYTHONPATH检查工具"""
    print("\n=== 创建PYTHONPATH检查工具 ===")
    
    checker_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'check_pythonpath.py')
    with open(checker_path, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('# -*- coding: utf-8 -*-\n\n')
        f.write('import os\n')
        f.write('import sys\n\n')
        f.write('def main():\n')
        f.write('    print("=== PYTHONPATH环境变量检查工具 ===\\n")\n\n')
        f.write('    # 检查PYTHONPATH\n')
        f.write('    pythonpath = os.environ.get("PYTHONPATH", "")\n')
        f.write('    if pythonpath:\n')
        f.write('        print(f"PYTHONPATH: {pythonpath}")\n')
        f.write('        paths = pythonpath.split(os.pathsep)\n')
        f.write('        print(f"\\nPYTHONPATH包含{len(paths)}个路径:")\n')
        f.write('        for i, path in enumerate(paths, 1):\n')
        f.write('            exists = "存在" if os.path.exists(path) else "不存在"\n')
        f.write('            print(f"{i}. {path} ({exists})")\n')
        f.write('    else:\n')
        f.write('        print("PYTHONPATH未设置")\n\n')
        f.write('    # 检查虚拟环境\n')
        f.write('    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):\n')
        f.write('        print(f"\\n虚拟环境路径: {sys.prefix}")\n')
        f.write('        site_packages = os.path.join(sys.prefix, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")\n')
        f.write('        print(f"site-packages路径: {site_packages}")\n')
        f.write('        if os.path.exists(site_packages):\n')
        f.write('            print("\\n已安装的包:")\n')
        f.write('            for i, pkg in enumerate(sorted(os.listdir(site_packages))[:10], 1):\n')
        f.write('                print(f"{i}. {pkg}")\n')
        f.write('            print("...(仅显示前10个包)")\n')
        f.write('    else:\n')
        f.write('        print("\\n当前不在虚拟环境中")\n\n')
        f.write('    # 检查sys.path\n')
        f.write('    print("\\nPython模块搜索路径(sys.path):")\n')
        f.write('    for i, path in enumerate(sys.path, 1):\n')
        f.write('        exists = "存在" if os.path.exists(path) else "不存在"\n')
        f.write('        print(f"{i}. {path} ({exists})")\n\n')
        f.write('if __name__ == "__main__":\n')
        f.write('    main()\n')
    
    # 使脚本可执行
    os.chmod(checker_path, 0o755)
    print(f"已创建检查工具: {checker_path}")
    print("运行此脚本可以检查当前PYTHONPATH设置和Python模块搜索路径")
    
    return checker_path

def main():
    """主函数"""
    print("=== PYTHONPATH环境变量分析工具 ===\n")
    
    # 检查当前PYTHONPATH
    check_pythonpath()
    
    # 检查Python模块搜索路径
    check_python_paths()
    
    # 检查虚拟环境
    in_virtualenv = check_virtualenv()
    
    # 解释PYTHONPATH
    explain_pythonpath()
    
    # 提供设置建议
    setup_pythonpath_recommendation()
    
    # 创建设置脚本
    setup_script = create_setup_script()
    
    # 创建检查工具
    checker_script = create_pythonpath_checker()
    
    print("\n=== 总结 ===")
    print("1. PYTHONPATH是Python解释器用来搜索模块的环境变量")
    print("2. 虚拟环境中通常不需要设置PYTHONPATH")
    print("3. 即使PYTHONPATH未设置，依赖包仍能正常导入，因为:")
    print("   - Python有默认的模块搜索路径")
    print("   - 虚拟环境自动配置了site-packages目录")
    print("4. 已创建以下工具:")
    print(f"   - 设置脚本: {setup_script}")
    print(f"   - 检查工具: {checker_script}")
    print("5. 最佳实践:")
    print("   - 尽量避免设置全局PYTHONPATH")
    print("   - 在虚拟环境中使用相对导入或绝对导入")
    print("   - 使用setup.py或pyproject.toml正确配置项目")
    print("   - 考虑使用.pth文件代替PYTHONPATH")

if __name__ == "__main__":
    main()