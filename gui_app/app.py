from utils.visualizer import Visualizer
from utils.prediction_model import PredictionModel
from utils.data_processor import DataProcessor
from utils.data_fetcher import DataFetcher
from utils.config_manager import ConfigManager
from views.settings_view import SettingsView
from views.prediction_view import PredictionView
from views.news_view import NewsView
from views.stock_view import StockView
from views.home_view import HomeView
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkthemes
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import json
import os
import sys
import threading
import time
from datetime import datetime
import logging
from PIL import Image, ImageTk

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入自定义模块

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False


class AIInvestmentAdvisorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI投资顾问")
        self.root.geometry("1200x800")

        # 设置主题
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("arc")

        # 初始化配置管理器
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

        # 初始化日志
        self.setup_logging()

        # 初始化数据组件
        self.data_fetcher = DataFetcher(self.config)
        self.data_processor = DataProcessor(self.config)
        self.prediction_model = PredictionModel(self.config)
        self.visualizer = Visualizer(self.config)

        # 创建主界面
        self.create_main_ui()

        # 初始化数据
        self.init_data()

        # 设置自动刷新
        self.setup_auto_refresh()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 记录应用启动
        self.logger.info("AI投资顾问应用已启动")

    def setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'ai_investment_advisor.log')

        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # 配置日志
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def create_main_ui(self):
        """创建主界面"""
        # 创建顶部框架
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        # 创建标题
        self.title_label = ttk.Label(
            self.top_frame,
            text="AI投资顾问",
            font=('Arial', 16, 'bold')
        )
        self.title_label.pack(side=tk.LEFT, padx=10, pady=5)

        # 创建状态显示
        self.status_label = ttk.Label(
            self.top_frame,
            text="系统状态: 正常",
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # 创建主容器
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 创建侧边栏
        self.sidebar = ttk.Frame(self.main_container, width=200)
        self.main_container.add(self.sidebar, weight=0)

        # 创建内容区域
        self.content_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.content_frame, weight=1)

        # 创建侧边栏导航
        self.create_sidebar()

        # 创建底部状态栏
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.system_info_label = ttk.Label(
            self.bottom_frame,
            text=f"系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            font=('Arial', 9)
        )
        self.system_info_label.pack(side=tk.LEFT, padx=10, pady=2)

        # 创建进度条
        self.progress = ttk.Progressbar(
            self.bottom_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='determinate'
        )
        self.progress.pack(side=tk.RIGHT, padx=10, pady=2)

        # 初始化视图
        self.current_view = None
        self.views = {}

        # 显示首页
        self.show_view('home')

    def create_sidebar(self):
        """创建侧边栏导航"""
        # 导航按钮样式
        nav_style = ttk.Style()
        nav_style.configure('Nav.TButton', font=('Arial', 10))

        # 导航按钮
        nav_buttons = [
            ('首页', 'home', self.show_home),
            ('股票分析', 'stock', self.show_stock),
            ('新闻资讯', 'news', self.show_news),
            ('预测结果', 'prediction', self.show_prediction),
            ('设置', 'settings', self.show_settings)
        ]

        for text, view_id, command in nav_buttons:
            btn = ttk.Button(
                self.sidebar,
                text=text,
                style='Nav.TButton',
                command=command
            )
            btn.pack(fill=tk.X, padx=5, pady=5)

    def show_view(self, view_id):
        """显示指定视图"""
        # 隐藏当前视图
        if self.current_view:
            self.current_view.pack_forget()

        # 显示新视图
        if view_id not in self.views:
            # 创建新视图
            if view_id == 'home':
                self.views[view_id] = HomeView(self.content_frame, self)
            elif view_id == 'stock':
                self.views[view_id] = StockView(self.content_frame, self)
            elif view_id == 'news':
                self.views[view_id] = NewsView(self.content_frame, self)
            elif view_id == 'prediction':
                self.views[view_id] = PredictionView(self.content_frame, self)
            elif view_id == 'settings':
                self.views[view_id] = SettingsView(self.content_frame, self)

        self.current_view = self.views[view_id]
        self.current_view.pack(fill=tk.BOTH, expand=True)

        # 更新状态栏
        self.update_status(f"当前视图: {self.get_view_name(view_id)}")

    def get_view_name(self, view_id):
        """获取视图名称"""
        view_names = {
            'home': '首页',
            'stock': '股票分析',
            'news': '新闻资讯',
            'prediction': '预测结果',
            'settings': '设置'
        }
        return view_names.get(view_id, '未知')

    def show_home(self):
        """显示首页"""
        self.show_view('home')

    def show_stock(self):
        """显示股票分析"""
        self.show_view('stock')

    def show_news(self):
        """显示新闻资讯"""
        self.show_view('news')

    def show_prediction(self):
        """显示预测结果"""
        self.show_view('prediction')

    def show_settings(self):
        """显示设置"""
        self.show_view('settings')

    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=f"系统状态: {message}")
        self.logger.info(f"状态更新: {message}")

    def update_progress(self, value):
        """更新进度条"""
        self.progress['value'] = value
        self.root.update_idletasks()

    def show_error(self, title, message):
        """显示错误对话框"""
        messagebox.showerror(title, message)
        self.logger.error(f"错误: {title} - {message}")

    def show_info(self, title, message):
        """显示信息对话框"""
        messagebox.showinfo(title, message)
        self.logger.info(f"信息: {title} - {message}")

    def show_warning(self, title, message):
        """显示警告对话框"""
        messagebox.showwarning(title, message)
        self.logger.warning(f"警告: {title} - {message}")

    def init_data(self):
        """初始化数据"""
        # 在后台线程中初始化数据
        threading.Thread(target=self._init_data_thread, daemon=True).start()

    def _init_data_thread(self):
        """初始化数据线程"""
        try:
            self.update_status("正在初始化数据...")
            self.update_progress(10)

            # 获取股票列表
            stock_symbols = self.config.get('stock_symbols', [])
            if not stock_symbols:
                self.update_progress(0)
                self.update_status("数据初始化完成")
                return

            self.update_progress(30)

            # 获取新闻数据
            news_query = self.config.get(
                'news_query', 'artificial intelligence')
            self.news_data = self.data_fetcher.fetch_news_data(news_query)

            self.update_progress(60)

            # 获取股票数据
            self.stock_data = {}
            for symbol in stock_symbols:
                self.stock_data[symbol] = self.data_fetcher.fetch_stock_data(
                    symbol)
                self.update_progress(
                    60 + (30 / len(stock_symbols)) * (list(stock_symbols).index(symbol) + 1))

            # 处理数据
            self.processed_data = {}
            for symbol, data in self.stock_data.items():
                self.processed_data[symbol] = self.data_processor.process_stock_data(
                    data)

            self.update_progress(90)

            # 更新视图
            if 'home' in self.views:
                self.views['home'].update_data(self.stock_data, self.news_data)

            if 'stock' in self.views:
                self.views['stock'].update_stock_list(
                    list(self.stock_data.keys()))

            if 'news' in self.views:
                self.views['news'].update_news(self.news_data)

            self.update_progress(100)
            self.update_status("数据初始化完成")

        except Exception as e:
            self.update_progress(0)
            self.update_status("数据初始化失败")
            self.show_error("初始化错误", f"初始化数据时出错: {str(e)}")

    def setup_auto_refresh(self):
        """设置自动刷新"""
        # 更新系统时间
        self.update_system_time()

        # 设置定时刷新
        refresh_interval = self.config.get('refresh_interval', 300)  # 默认5分钟
        self.root.after(refresh_interval * 1000, self.auto_refresh)

    def update_system_time(self):
        """更新系统时间"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.system_info_label.config(text=f"系统时间: {current_time}")
        self.root.after(1000, self.update_system_time)

    def auto_refresh(self):
        """自动刷新数据"""
        try:
            self.update_status("正在刷新数据...")
            self.update_progress(0)

            # 获取新闻数据
            news_query = self.config.get(
                'news_query', 'artificial intelligence')
            self.news_data = self.data_fetcher.fetch_news_data(news_query)

            self.update_progress(30)

            # 获取股票数据
            stock_symbols = self.config.get('stock_symbols', [])
            for symbol in stock_symbols:
                self.stock_data[symbol] = self.data_fetcher.fetch_stock_data(
                    symbol)
                self.processed_data[symbol] = self.data_processor.process_stock_data(
                    self.stock_data[symbol])
                self.update_progress(
                    30 + (60 / len(stock_symbols)) * (list(stock_symbols).index(symbol) + 1))

            # 更新视图
            if 'home' in self.views:
                self.views['home'].update_data(self.stock_data, self.news_data)

            if 'news' in self.views:
                self.views['news'].update_news(self.news_data)

            if 'stock' in self.views and hasattr(self.views['stock'], 'current_symbol'):
                current_symbol = self.views['stock'].current_symbol
                if current_symbol in self.stock_data:
                    self.views['stock'].update_stock_data(
                        current_symbol, self.stock_data[current_symbol])

            self.update_progress(100)
            self.update_status("数据刷新完成")

        except Exception as e:
            self.update_progress(0)
            self.update_status("数据刷新失败")
            self.show_error("刷新错误", f"刷新数据时出错: {str(e)}")

        # 设置下次刷新
        refresh_interval = self.config.get('refresh_interval', 300)  # 默认5分钟
        self.root.after(refresh_interval * 1000, self.auto_refresh)

    def on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出AI投资顾问吗？"):
            self.logger.info("AI投资顾问应用已关闭")
            self.root.destroy()


def main():
    # 创建主窗口
    root = ThemedTk(theme="arc")

    # 创建应用
    app = AIInvestmentAdvisorApp(root)

    # 运行应用
    root.mainloop()


if __name__ == "__main__":
    main()
