#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def main():
    print("=== PYTHONPATH环境变量检查工具 ===\n")

    # 检查PYTHONPATH
    pythonpath = os.environ.get("PYTHONPATH", "")
    if pythonpath:
        print(f"PYTHONPATH: {pythonpath}")
        paths = pythonpath.split(os.pathsep)
        print(f"\nPYTHONPATH包含{len(paths)}个路径:")
        for i, path in enumerate(paths, 1):
            exists = "存在" if os.path.exists(path) else "不存在"
            print(f"{i}. {path} ({exists})")
    else:
        print("PYTHONPATH未设置")

    # 检查虚拟环境
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        print(f"\n虚拟环境路径: {sys.prefix}")
        site_packages = os.path.join(sys.prefix, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
        print(f"site-packages路径: {site_packages}")
        if os.path.exists(site_packages):
            print("\n已安装的包:")
            for i, pkg in enumerate(sorted(os.listdir(site_packages))[:10], 1):
                print(f"{i}. {pkg}")
            print("...(仅显示前10个包)")
    else:
        print("\n当前不在虚拟环境中")

    # 检查sys.path
    print("\nPython模块搜索路径(sys.path):")
    for i, path in enumerate(sys.path, 1):
        exists = "存在" if os.path.exists(path) else "不存在"
        print(f"{i}. {path} ({exists})")

if __name__ == "__main__":
    main()
