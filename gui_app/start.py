#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI投资顾问GUI应用启动脚本
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import logging

# 添加项目路径到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def check_dependencies():
    """检查依赖包是否安装"""
    required_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'scikit-learn': 'sklearn',         # ← 关键
        'tensorflow': 'tensorflow',
        'yfinance': 'yfinance',
        'requests': 'requests',
        'beautifulsoup4': 'bs4',           # ← 关键
        'textblob': 'textblob',
        'nltk': 'nltk',
        'ta': 'ta',
        'tqdm': 'tqdm',
        'Pillow': 'PIL',                   # ← 关键
        'ttkthemes': 'ttkthemes',
    }

    missing_packages = []

    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)

    if missing_packages:
        messagebox.showerror(
            "缺少依赖包",
            f"缺少以下依赖包：\n{', '.join(missing_packages)}\n\n请使用以下命令安装：\npip install -r requirements.txt"
        )
        return False

    return True


def setup_directories():
    """设置必要的目录"""
    directories = [
        'data',
        'data/logs',
        'data/models',
        'static/images'
    ]

    for directory in directories:
        dir_path = os.path.join(current_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"创建目录: {dir_path}")


def main():
    """主函数"""
    # 检查依赖包
    if not check_dependencies():
        sys.exit(1)

    # 设置目录
    setup_directories()

    try:
        # 导入主应用
        from app import AIInvestmentAdvisorApp

        # 创建主窗口
        root = tk.Tk()
        root.title("AI投资顾问")

        # 设置窗口图标（如果存在）
        icon_path = os.path.join(current_dir, 'static', 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)

        # 设置窗口大小和位置
        window_width = 1200
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 创建应用
        app = AIInvestmentAdvisorApp(root)

        # 运行应用
        root.mainloop()

    except Exception as e:
        logging.error(f"启动应用时出错: {str(e)}")
        messagebox.showerror("启动错误", f"启动应用时出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
