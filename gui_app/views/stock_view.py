
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class StockView(ttk.Frame):
    def __init__(self, parent, app):
        """初始化股票分析视图"""
        super().__init__(parent)
        self.app = app
        self.current_symbol = None
        self.stock_data = {}
        self.processed_data = {}
        self.fundamental_data = {}
        self.technical_signals = {}

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        """创建UI组件"""
        # 创建顶部框架 - 股票搜索和选择
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 创建股票搜索框
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(search_frame, text="股票代码:").pack(side=tk.LEFT, padx=(0, 5))

        self.stock_entry = ttk.Entry(search_frame, width=10)
        self.stock_entry.pack(side=tk.LEFT, padx=(0, 5))

        # 创建搜索按钮
        search_button = ttk.Button(
            search_frame,
            text="搜索",
            command=self.search_stock
        )
        search_button.pack(side=tk.LEFT, padx=(0, 10))

        # 创建股票下拉框
        ttk.Label(search_frame, text="或选择:").pack(side=tk.LEFT, padx=(0, 5))

        self.stock_var = tk.StringVar()
        self.stock_dropdown = ttk.Combobox(
            search_frame,
            textvariable=self.stock_var,
            width=10,
            state="readonly"
        )
        self.stock_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        self.stock_dropdown.bind(
            "<<ComboboxSelected>>", self.on_stock_selected)

        # 创建刷新按钮
        refresh_button = ttk.Button(
            search_frame,
            text="刷新",
            command=self.refresh_data
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        # 创建时间范围选择
        ttk.Label(search_frame, text="时间范围:").pack(side=tk.LEFT, padx=(0, 5))

        self.period_var = tk.StringVar(value="1y")
        period_dropdown = ttk.Combobox(
            search_frame,
            textvariable=self.period_var,
            values=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            width=5,
            state="readonly"
        )
        period_dropdown.pack(side=tk.LEFT)

        # 创建中间框架 - 分为左右两部分
        middle_frame = ttk.Frame(self)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建左侧框架 - K线图和技术指标
        left_frame = ttk.Frame(middle_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建图表框架
        chart_frame = ttk.LabelFrame(left_frame, text="K线图", padding=5)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        # 创建图表
        self.fig, self.axes = plt.subplots(4, 1, figsize=(8, 10), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 创建技术指标框架
        indicators_frame = ttk.LabelFrame(left_frame, text="技术指标", padding=5)
        indicators_frame.pack(fill=tk.X, pady=(5, 0))

        # 创建技术指标选择
        self.show_volume = tk.BooleanVar(value=True)
        self.show_indicators = tk.BooleanVar(value=True)

        volume_check = ttk.Checkbutton(
            indicators_frame,
            text="显示成交量",
            variable=self.show_volume,
            command=self.update_chart
        )
        volume_check.pack(side=tk.LEFT, padx=5)

        indicators_check = ttk.Checkbutton(
            indicators_frame,
            text="显示技术指标",
            variable=self.show_indicators,
            command=self.update_chart
        )
        indicators_check.pack(side=tk.LEFT, padx=5)

        # 创建右侧框架 - 基本面数据和技术信号
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))

        # 创建基本面数据框架
        fundamental_frame = ttk.LabelFrame(
            right_frame, text="基本面数据", padding=5)
        fundamental_frame.pack(fill=tk.BOTH, expand=True)

        # 创建基本面数据表格
        self.create_fundamental_table(fundamental_frame)

        # 创建技术信号框架
        signals_frame = ttk.LabelFrame(right_frame, text="技术信号", padding=5)
        signals_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 创建技术信号表格
        self.create_signals_table(signals_frame)

        # 创建底部框架 - 数据表格
        bottom_frame = ttk.LabelFrame(self, text="历史数据", padding=5)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # 创建数据表格
        self.create_data_table(bottom_frame)

    def create_fundamental_table(self, parent):
        """创建基本面数据表格"""
        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ('指标', '值')
        self.fundamental_table = ttk.Treeview(
            table_frame, columns=columns, show='headings', height=10)

        # 设置列标题
        self.fundamental_table.heading('指标', text='指标')
        self.fundamental_table.heading('值', text='值')
        self.fundamental_table.column('指标', width=120)
        self.fundamental_table.column('值', width=120)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.fundamental_table.yview)
        self.fundamental_table.configure(yscroll=scrollbar.set)

        # 放置表格和滚动条
        self.fundamental_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_signals_table(self, parent):
        """创建技术信号表格"""
        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ('指标', '信号')
        self.signals_table = ttk.Treeview(
            table_frame, columns=columns, show='headings', height=6)

        # 设置列标题
        self.signals_table.heading('指标', text='指标')
        self.signals_table.heading('信号', text='信号')
        self.signals_table.column('指标', width=120)
        self.signals_table.column('信号', width=120)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.signals_table.yview)
        self.signals_table.configure(yscroll=scrollbar.set)

        # 放置表格和滚动条
        self.signals_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_data_table(self, parent):
        """创建数据表格"""
        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ('日期', '开盘', '最高', '最低', '收盘', '成交量')
        self.data_table = ttk.Treeview(
            table_frame, columns=columns, show='headings')

        # 设置列标题
        for col in columns:
            self.data_table.heading(col, text=col)
            self.data_table.column(col, width=100)

        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.data_table.yview)
        h_scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.HORIZONTAL, command=self.data_table.xview)
        self.data_table.configure(
            yscroll=v_scrollbar.set, xscroll=h_scrollbar.set)

        # 放置表格和滚动条
        self.data_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_stock_list(self, stock_symbols):
        """更新股票列表"""
        self.stock_dropdown['values'] = stock_symbols
        if stock_symbols and not self.stock_var.get():
            self.stock_var.set(stock_symbols[0])
            self.select_stock(stock_symbols[0])

    def select_stock(self, symbol):
        """选择股票"""
        self.current_symbol = symbol
        self.stock_var.set(symbol)
        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, symbol)

        # 更新数据
        self.update_stock_data(symbol)

    def search_stock(self):
        """搜索股票"""
        symbol = self.stock_entry.get().upper()
        if symbol:
            self.select_stock(symbol)

    def on_stock_selected(self, event):
        """股票选择事件处理"""
        symbol = self.stock_var.get()
        if symbol:
            self.select_stock(symbol)

    def refresh_data(self):
        """刷新数据"""
        if self.current_symbol:
            self.update_stock_data(self.current_symbol)

    def update_stock_data(self, symbol):
        """更新股票数据"""
        try:
            self.app.update_status(f"正在获取 {symbol} 的数据...")
            self.app.update_progress(10)

            # 获取股票数据
            period = self.period_var.get()
            stock_data = self.app.data_fetcher.fetch_stock_data(symbol, period)

            if stock_data.empty:
                self.app.show_error("数据错误", f"无法获取 {symbol} 的数据")
                return

            self.app.update_progress(30)

            # 处理股票数据
            processed_data = self.app.data_processor.process_stock_data(
                stock_data)

            self.app.update_progress(50)

            # 获取基本面数据
            fundamental_data = self.app.data_fetcher.fetch_stock_fundamentals(
                symbol)
            processed_fundamental = self.app.data_processor.process_fundamental_data(
                fundamental_data)

            self.app.update_progress(70)

            # 计算技术信号
            technical_signals = self.app.data_processor.calculate_technical_signals(
                processed_data)

            self.app.update_progress(90)

            # 保存数据
            self.stock_data[symbol] = stock_data
            self.processed_data[symbol] = processed_data
            self.fundamental_data[symbol] = processed_fundamental
            self.technical_signals[symbol] = technical_signals

            # 更新UI
            self.update_chart()
            self.update_fundamental_table()
            self.update_signals_table()
            self.update_data_table()

            self.app.update_progress(100)
            self.app.update_status(f"{symbol} 数据已更新")

        except Exception as e:
            self.app.update_progress(0)
            self.app.update_status("数据更新失败")
            self.app.show_error("更新错误", f"更新 {symbol} 数据时出错: {str(e)}")

    def update_chart(self):
        """更新图表"""
        if self.current_symbol not in self.processed_data:
            return

        try:
            # 获取数据
            data = self.processed_data[self.current_symbol]

            # 清空图表
            for ax in self.axes:
                ax.clear()

            # 绘制K线图
            self.app.visualizer._plot_candlestick(self.axes[0], data)

            # 添加移动平均线
            if self.show_indicators.get() and 'MA20' in data.columns:
                self.axes[0].plot(data.index, data['MA20'],
                                  label='MA20', color='blue', alpha=0.75)

            if self.show_indicators.get() and 'MA50' in data.columns:
                self.axes[0].plot(data.index, data['MA50'],
                                  label='MA50', color='red', alpha=0.75)

            # 添加布林带
            if self.show_indicators.get() and all(col in data.columns for col in ['BB_upper', 'BB_middle', 'BB_lower']):
                self.axes[0].plot(data.index, data['BB_upper'],
                                  label='布林带上轨', color='gray', alpha=0.5, linestyle='--')
                self.axes[0].plot(data.index, data['BB_middle'],
                                  label='布林带中轨', color='gray', alpha=0.5)
                self.axes[0].plot(data.index, data['BB_lower'],
                                  label='布林带下轨', color='gray', alpha=0.5, linestyle='--')
                self.axes[0].fill_between(
                    data.index, data['BB_upper'], data['BB_lower'], color='gray', alpha=0.1)

            # 设置标题和图例
            self.axes[0].set_title(f'{self.current_symbol} 股价走势')
            self.axes[0].legend(loc='upper left')

            # 绘制成交量
            if self.show_volume.get():
                self.app.visualizer._plot_volume(self.axes[1], data)

            # 绘制RSI
            if self.show_indicators.get() and 'RSI' in data.columns:
                self.app.visualizer._plot_rsi(self.axes[2], data)

            # 绘制MACD
            if self.show_indicators.get() and all(col in data.columns for col in ['MACD', 'MACD_signal', 'MACD_hist']):
                self.app.visualizer._plot_macd(self.axes[3], data)

            # 调整布局
            self.fig.tight_layout()

            # 更新画布
            self.canvas.draw()

        except Exception as e:
            self.app.show_error("图表错误", f"更新图表时出错: {str(e)}")

    def update_fundamental_table(self):
        """更新基本面数据表格"""
        if self.current_symbol not in self.fundamental_data:
            return

        # 清空表格
        for item in self.fundamental_table.get_children():
            self.fundamental_table.delete(item)

        # 获取基本面数据
        fundamental = self.fundamental_data[self.current_symbol]

        # 添加数据到表格
        fundamental_items = [
            ('股票代码', fundamental.get('symbol', '')),
            ('公司名称', fundamental.get('name', '')),
            ('行业', fundamental.get('industry', '')),
            ('市值', f"{fundamental.get('market_cap', 0):,.0f}"),
            ('市盈率(TTM)', f"{fundamental.get('trailing_pe', 0):.2f}"),
            ('市盈率(前瞻)', f"{fundamental.get('forward_pe', 0):.2f}"),
            ('市净率', f"{fundamental.get('price_to_book', 0):.2f}"),
            ('股息率', f"{fundamental.get('dividend_yield', 0):.2%}"),
            ('贝塔系数', f"{fundamental.get('beta', 0):.2f}"),
            ('利润率', f"{fundamental.get('profit_margins', 0):.2%}"),
            ('营收增长', f"{fundamental.get('revenue_growth', 0):.2%}"),
            ('收益增长', f"{fundamental.get('earnings_growth', 0):.2%}")
        ]

        for item in fundamental_items:
            self.fundamental_table.insert('', 'end', values=item)

    def update_signals_table(self):
        """更新技术信号表格"""
        if self.current_symbol not in self.technical_signals:
            return

        # 清空表格
        for item in self.signals_table.get_children():
            self.signals_table.delete(item)

        # 获取技术信号
        signals = self.technical_signals[self.current_symbol]

        # 添加数据到表格
        for indicator, signal in signals.items():
            self.signals_table.insert('', 'end', values=(indicator, signal))

    def update_data_table(self):
        """更新数据表格"""
        if self.current_symbol not in self.stock_data:
            return

        # 清空表格
        for item in self.data_table.get_children():
            self.data_table.delete(item)

        # 获取股票数据
        data = self.stock_data[self.current_symbol]

        # 添加最近20条数据到表格
        recent_data = data.tail(20).reset_index()
        for _, row in recent_data.iterrows():
            date_str = row['Date'].strftime(
                '%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date'])
            self.data_table.insert('', 'end', values=(
                date_str,
                f"{row['Open']:.2f}",
                f"{row['High']:.2f}",
                f"{row['Low']:.2f}",
                f"{row['Close']:.2f}",
                f"{row['Volume']:,}"
            ))
