import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import logging
from datetime import datetime


class SettingsView(ttk.Frame):
    def __init__(self, parent, app):
        """初始化设置视图"""
        super().__init__(parent)
        self.app = app
        self.config = self.app.config_manager.config

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        """创建UI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建笔记本控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建各个标签页
        self.create_api_tab()
        self.create_stock_tab()
        self.create_news_tab()
        self.create_model_tab()
        self.create_ui_tab()
        self.create_about_tab()

        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 创建按钮
        save_button = ttk.Button(
            button_frame,
            text="保存设置",
            command=self.save_settings
        )
        save_button.pack(side=tk.RIGHT, padx=(5, 0))

        reset_button = ttk.Button(
            button_frame,
            text="重置为默认",
            command=self.reset_settings
        )
        reset_button.pack(side=tk.RIGHT, padx=(5, 0))

        export_button = ttk.Button(
            button_frame,
            text="导出配置",
            command=self.export_config
        )
        export_button.pack(side=tk.RIGHT, padx=(5, 0))

        import_button = ttk.Button(
            button_frame,
            text="导入配置",
            command=self.import_config
        )
        import_button.pack(side=tk.RIGHT)

    def create_api_tab(self):
        """创建API设置标签页"""
        # 创建API设置框架
        api_frame = ttk.Frame(self.notebook)
        self.notebook.add(api_frame, text="API设置")

        # 创建API密钥设置
        api_keys_frame = ttk.LabelFrame(api_frame, text="API密钥", padding=10)
        api_keys_frame.pack(fill=tk.X, padx=10, pady=10)

        # News API
        ttk.Label(api_keys_frame, text="News API:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.news_api_var = tk.StringVar(
            value=self.config.get('api_keys', {}).get('news_api', ''))
        news_api_entry = ttk.Entry(
            api_keys_frame, textvariable=self.news_api_var, width=50, show="*")
        news_api_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Alpha Vantage API
        ttk.Label(api_keys_frame, text="Alpha Vantage API:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.alpha_vantage_var = tk.StringVar(
            value=self.config.get('api_keys', {}).get('alpha_vantage', ''))
        alpha_vantage_entry = ttk.Entry(
            api_keys_frame, textvariable=self.alpha_vantage_var, width=50, show="*")
        alpha_vantage_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Quandl API
        ttk.Label(api_keys_frame, text="Quandl API:").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.quandl_var = tk.StringVar(
            value=self.config.get('api_keys', {}).get('quandl', ''))
        quandl_entry = ttk.Entry(
            api_keys_frame, textvariable=self.quandl_var, width=50, show="*")
        quandl_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        # 创建数据源设置
        data_source_frame = ttk.LabelFrame(api_frame, text="数据源设置", padding=10)
        data_source_frame.pack(fill=tk.X, padx=10, pady=10)

        # 使用模拟数据
        self.use_mock_data_var = tk.BooleanVar(value=self.config.get(
            'data_settings', {}).get('use_mock_data', True))
        mock_data_check = ttk.Checkbutton(
            data_source_frame,
            text="使用模拟数据",
            variable=self.use_mock_data_var
        )
        mock_data_check.pack(anchor=tk.W, pady=5)

        # 历史数据年限
        ttk.Label(data_source_frame, text="历史数据年限:").pack(
            anchor=tk.W, pady=(10, 0))
        years_frame = ttk.Frame(data_source_frame)
        years_frame.pack(fill=tk.X, pady=5)

        self.historical_years_var = tk.IntVar(value=self.config.get(
            'data_settings', {}).get('historical_data_years', 5))
        years_spinbox = ttk.Spinbox(
            years_frame,
            from_=1,
            to=10,
            textvariable=self.historical_years_var,
            width=5
        )
        years_spinbox.pack(side=tk.LEFT)

        ttk.Label(years_frame, text="年").pack(side=tk.LEFT, padx=(5, 0))

        # 最大新闻文章数
        ttk.Label(data_source_frame, text="最大新闻文章数:").pack(
            anchor=tk.W, pady=(10, 0))
        news_frame = ttk.Frame(data_source_frame)
        news_frame.pack(fill=tk.X, pady=5)

        self.max_news_var = tk.IntVar(value=self.config.get(
            'data_settings', {}).get('max_news_articles', 100))
        news_spinbox = ttk.Spinbox(
            news_frame,
            from_=10,
            to=500,
            increment=10,
            textvariable=self.max_news_var,
            width=5
        )
        news_spinbox.pack(side=tk.LEFT)

        ttk.Label(news_frame, text="篇").pack(side=tk.LEFT, padx=(5, 0))

    def create_stock_tab(self):
        """创建股票设置标签页"""
        # 创建股票设置框架
        stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(stock_frame, text="股票设置")

        # 创建股票列表设置
        stock_list_frame = ttk.LabelFrame(stock_frame, text="股票列表", padding=10)
        stock_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建股票列表框架
        list_frame = ttk.Frame(stock_list_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建股票列表
        columns = ('代码', '名称')
        self.stock_tree = ttk.Treeview(
            list_frame, columns=columns, show='headings')

        # 设置列标题
        self.stock_tree.heading('代码', text='代码')
        self.stock_tree.heading('名称', text='名称')
        self.stock_tree.column('代码', width=100)
        self.stock_tree.column('名称', width=150)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        self.stock_tree.configure(yscroll=scrollbar.set)

        # 放置列表和滚动条
        self.stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建按钮框架
        button_frame = ttk.Frame(stock_list_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 添加按钮
        add_button = ttk.Button(
            button_frame,
            text="添加",
            command=self.add_stock
        )
        add_button.pack(side=tk.LEFT, padx=(0, 5))

        remove_button = ttk.Button(
            button_frame,
            text="删除",
            command=self.remove_stock
        )
        remove_button.pack(side=tk.LEFT, padx=(0, 5))

        # 创建股票输入框架
        input_frame = ttk.Frame(stock_list_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(input_frame, text="股票代码:").pack(side=tk.LEFT, padx=(0, 5))

        self.stock_code_var = tk.StringVar()
        stock_code_entry = ttk.Entry(
            input_frame, textvariable=self.stock_code_var, width=10)
        stock_code_entry.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Label(input_frame, text="股票名称:").pack(side=tk.LEFT, padx=(0, 5))

        self.stock_name_var = tk.StringVar()
        stock_name_entry = ttk.Entry(
            input_frame, textvariable=self.stock_name_var, width=15)
        stock_name_entry.pack(side=tk.LEFT)

        # 初始化股票列表
        self.init_stock_list()

    def create_news_tab(self):
        """创建新闻设置标签页"""
        # 创建新闻设置框架
        news_frame = ttk.Frame(self.notebook)
        self.notebook.add(news_frame, text="新闻设置")

        # 创建新闻查询设置
        query_frame = ttk.LabelFrame(news_frame, text="新闻查询", padding=10)
        query_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(query_frame, text="默认查询关键词:").pack(anchor=tk.W, pady=5)

        self.news_query_var = tk.StringVar(
            value=self.config.get('news_query', 'artificial intelligence'))
        query_entry = ttk.Entry(
            query_frame, textvariable=self.news_query_var, width=50)
        query_entry.pack(fill=tk.X, pady=5)

        # 创建新闻来源设置
        source_frame = ttk.LabelFrame(news_frame, text="新闻来源", padding=10)
        source_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建新闻来源列表框架
        list_frame = ttk.Frame(source_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建新闻来源列表
        columns = ('来源',)
        self.source_tree = ttk.Treeview(
            list_frame, columns=columns, show='headings')

        # 设置列标题
        self.source_tree.heading('来源', text='来源')
        self.source_tree.column('来源', width=200)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.source_tree.yview)
        self.source_tree.configure(yscroll=scrollbar.set)

        # 放置列表和滚动条
        self.source_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建按钮框架
        button_frame = ttk.Frame(source_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 添加按钮
        add_button = ttk.Button(
            button_frame,
            text="添加",
            command=self.add_source
        )
        add_button.pack(side=tk.LEFT, padx=(0, 5))

        remove_button = ttk.Button(
            button_frame,
            text="删除",
            command=self.remove_source
        )
        remove_button.pack(side=tk.LEFT)

        # 创建新闻来源输入框架
        input_frame = ttk.Frame(source_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(input_frame, text="新闻来源:").pack(side=tk.LEFT, padx=(0, 5))

        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(
            input_frame, textvariable=self.source_var, width=30)
        source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 初始化新闻来源列表
        self.init_source_list()

    def create_model_tab(self):
        """创建模型设置标签页"""
        # 创建模型设置框架
        model_frame = ttk.Frame(self.notebook)
        self.notebook.add(model_frame, text="模型设置")

        # 创建预测参数设置
        prediction_frame = ttk.LabelFrame(model_frame, text="预测参数", padding=10)
        prediction_frame.pack(fill=tk.X, padx=10, pady=10)

        # 预测天数
        ttk.Label(prediction_frame, text="预测天数:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        days_frame = ttk.Frame(prediction_frame)
        days_frame.grid(row=0, column=1, sticky=tk.W, pady=5)

        self.prediction_days_var = tk.IntVar(value=self.config.get(
            'model_parameters', {}).get('prediction_days', 30))
        days_spinbox = ttk.Spinbox(
            days_frame,
            from_=5,
            to=90,
            textvariable=self.prediction_days_var,
            width=5
        )
        days_spinbox.pack(side=tk.LEFT)

        ttk.Label(days_frame, text="天").pack(side=tk.LEFT, padx=(5, 0))

        # LSTM单元数
        ttk.Label(prediction_frame, text="LSTM单元数:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        lstm_frame = ttk.Frame(prediction_frame)
        lstm_frame.grid(row=1, column=1, sticky=tk.W, pady=5)

        self.lstm_units_var = tk.IntVar(value=self.config.get(
            'model_parameters', {}).get('lstm_units', 50))
        lstm_spinbox = ttk.Spinbox(
            lstm_frame,
            from_=10,
            to=200,
            increment=10,
            textvariable=self.lstm_units_var,
            width=5
        )
        lstm_spinbox.pack(side=tk.LEFT)

        # Dropout率
        ttk.Label(prediction_frame, text="Dropout率:").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        dropout_frame = ttk.Frame(prediction_frame)
        dropout_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        self.dropout_var = tk.DoubleVar(value=self.config.get(
            'model_parameters', {}).get('dropout_rate', 0.2))
        dropout_spinbox = ttk.Spinbox(
            dropout_frame,
            from_=0.1,
            to=0.5,
            increment=0.1,
            textvariable=self.dropout_var,
            width=5
        )
        dropout_spinbox.pack(side=tk.LEFT)

        # 训练轮数
        ttk.Label(prediction_frame, text="训练轮数:").grid(
            row=3, column=0, sticky=tk.W, pady=5)
        epochs_frame = ttk.Frame(prediction_frame)
        epochs_frame.grid(row=3, column=1, sticky=tk.W, pady=5)

        self.epochs_var = tk.IntVar(value=self.config.get(
            'model_parameters', {}).get('epochs', 50))
        epochs_spinbox = ttk.Spinbox(
            epochs_frame,
            from_=10,
            to=200,
            increment=10,
            textvariable=self.epochs_var,
            width=5
        )
        epochs_spinbox.pack(side=tk.LEFT)

        # 批次大小
        ttk.Label(prediction_frame, text="批次大小:").grid(
            row=4, column=0, sticky=tk.W, pady=5)
        batch_frame = ttk.Frame(prediction_frame)
        batch_frame.grid(row=4, column=1, sticky=tk.W, pady=5)

        self.batch_var = tk.IntVar(value=self.config.get(
            'model_parameters', {}).get('batch_size', 32))
        batch_spinbox = ttk.Spinbox(
            batch_frame,
            from_=8,
            to=128,
            increment=8,
            textvariable=self.batch_var,
            width=5
        )
        batch_spinbox.pack(side=tk.LEFT)

        # 训练测试分割比例
        ttk.Label(prediction_frame, text="训练测试分割比例:").grid(
            row=5, column=0, sticky=tk.W, pady=5)
        split_frame = ttk.Frame(prediction_frame)
        split_frame.grid(row=5, column=1, sticky=tk.W, pady=5)

        self.split_var = tk.DoubleVar(value=self.config.get(
            'model_parameters', {}).get('train_test_split', 0.8))
        split_spinbox = ttk.Spinbox(
            split_frame,
            from_=0.5,
            to=0.9,
            increment=0.1,
            textvariable=self.split_var,
            width=5
        )
        split_spinbox.pack(side=tk.LEFT)

        ttk.Label(split_frame, text="训练 /").pack(side=tk.LEFT, padx=(5, 0))

        # 创建高级设置框架
        advanced_frame = ttk.LabelFrame(model_frame, text="高级设置", padding=10)
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)

        # 自动保存模型
        self.auto_save_var = tk.BooleanVar(value=True)
        auto_save_check = ttk.Checkbutton(
            advanced_frame,
            text="自动保存模型",
            variable=self.auto_save_var
        )
        auto_save_check.pack(anchor=tk.W, pady=5)

        # 使用GPU加速
        self.use_gpu_var = tk.BooleanVar(value=False)
        gpu_check = ttk.Checkbutton(
            advanced_frame,
            text="使用GPU加速（如果可用）",
            variable=self.use_gpu_var
        )
        gpu_check.pack(anchor=tk.W, pady=5)

    def create_ui_tab(self):
        """创建UI设置标签页"""
        # 创建UI设置框架
        ui_frame = ttk.Frame(self.notebook)
        self.notebook.add(ui_frame, text="界面设置")

        # 创建主题设置
        theme_frame = ttk.LabelFrame(ui_frame, text="主题设置", padding=10)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(theme_frame, text="主题:").pack(anchor=tk.W, pady=5)

        self.theme_var = tk.StringVar(value=self.config.get(
            'ui_settings', {}).get('theme', 'arc'))
        theme_dropdown = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["arc", "clearlooks", "radiance", "ubuntu", "yaru"],
            state="readonly"
        )
        theme_dropdown.pack(fill=tk.X, pady=5)

        # 创建显示设置
        display_frame = ttk.LabelFrame(ui_frame, text="显示设置", padding=10)
        display_frame.pack(fill=tk.X, padx=10, pady=10)

        # 图表设置
        ttk.Label(display_frame, text="图表大小:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        size_frame = ttk.Frame(display_frame)
        size_frame.grid(row=0, column=1, sticky=tk.W, pady=5)

        self.fig_width_var = tk.IntVar(value=self.config.get(
            'visualization', {}).get('figure_size', [12, 8])[0])
        width_spinbox = ttk.Spinbox(
            size_frame,
            from_=8,
            to=20,
            textvariable=self.fig_width_var,
            width=5
        )
        width_spinbox.pack(side=tk.LEFT)

        ttk.Label(size_frame, text="x").pack(side=tk.LEFT, padx=(5, 0))

        self.fig_height_var = tk.IntVar(value=self.config.get(
            'visualization', {}).get('figure_size', [12, 8])[1])
        height_spinbox = ttk.Spinbox(
            size_frame,
            from_=6,
            to=15,
            textvariable=self.fig_height_var,
            width=5
        )
        height_spinbox.pack(side=tk.LEFT)

        ttk.Label(size_frame, text="英寸").pack(side=tk.LEFT, padx=(5, 0))

        # 颜色主题
        ttk.Label(display_frame, text="颜色主题:").grid(
            row=1, column=0, sticky=tk.W, pady=5)

        self.color_var = tk.StringVar(value=self.config.get(
            'visualization', {}).get('color_palette', 'viridis'))
        color_dropdown = ttk.Combobox(
            display_frame,
            textvariable=self.color_var,
            values=["viridis", "plasma", "inferno", "magma", "cividis"],
            state="readonly"
        )
        color_dropdown.grid(row=1, column=1, sticky=tk.W, pady=5)

        # 保存图表
        self.save_plots_var = tk.BooleanVar(value=self.config.get(
            'visualization', {}).get('save_plots', True))
        save_plots_check = ttk.Checkbutton(
            display_frame,
            text="保存图表到文件",
            variable=self.save_plots_var
        )
        save_plots_check.grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        # 创建刷新设置
        refresh_frame = ttk.LabelFrame(ui_frame, text="刷新设置", padding=10)
        refresh_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(refresh_frame, text="自动刷新间隔:").pack(anchor=tk.W, pady=5)

        interval_frame = ttk.Frame(refresh_frame)
        interval_frame.pack(fill=tk.X, pady=5)

        self.refresh_var = tk.IntVar(
            value=self.config.get('refresh_interval', 300))
        interval_spinbox = ttk.Spinbox(
            interval_frame,
            from_=60,
            to=1800,
            increment=60,
            textvariable=self.refresh_var,
            width=5
        )
        interval_spinbox.pack(side=tk.LEFT)

        ttk.Label(interval_frame, text="秒").pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(interval_frame,
                  text="(60-1800秒)").pack(side=tk.LEFT, padx=(10, 0))

    def create_about_tab(self):
        """创建关于标签页"""
        # 创建关于框架
        about_frame = ttk.Frame(self.notebook)
        self.notebook.add(about_frame, text="关于")

        # 创建应用信息框架
        info_frame = ttk.LabelFrame(about_frame, text="应用信息", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        # 应用名称和版本
        ttk.Label(info_frame, text="AI投资顾问", font=(
            'Arial', 14, 'bold')).pack(anchor=tk.W, pady=5)
        ttk.Label(info_frame, text="版本: 1.0.0").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="发布日期: 2023-01-01").pack(anchor=tk.W, pady=2)

        # 创建描述框架
        desc_frame = ttk.LabelFrame(about_frame, text="应用描述", padding=10)
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        desc_text = tk.Text(desc_frame, wrap=tk.WORD, height=10, width=50)
        desc_text.pack(fill=tk.BOTH, expand=True)

        # 添加描述内容
        description = """AI投资顾问是一个基于人工智能的股票分析和投资建议平台。该应用使用深度学习模型预测股票价格，并结合新闻情感分析提供投资建议。

主要功能：
- 股票数据获取和分析
- 技术指标计算
- 新闻情感分析
- 股价预测
- 投资建议生成

该应用旨在帮助投资者做出更明智的投资决策，但请注意，所有预测和建议仅供参考，投资有风险，决策需谨慎。"""

        desc_text.insert(tk.END, description)
        desc_text.config(state=tk.DISABLED)

        # 创建作者信息框架
        author_frame = ttk.LabelFrame(about_frame, text="作者信息", padding=10)
        author_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(author_frame, text="作者: AI投资顾问团队").pack(anchor=tk.W, pady=2)
        ttk.Label(
            author_frame, text="邮箱: contact@aiinvestment-advisor.com").pack(anchor=tk.W, pady=2)
        ttk.Label(
            author_frame, text="网站: www.aiinvestment-advisor.com").pack(anchor=tk.W, pady=2)

        # 创建许可信息框架
        license_frame = ttk.LabelFrame(about_frame, text="许可信息", padding=10)
        license_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(license_frame, text="本软件采用MIT许可证发布。").pack(
            anchor=tk.W, pady=2)
        ttk.Label(license_frame, text="详见LICENSE文件。").pack(anchor=tk.W, pady=2)

    def init_stock_list(self):
        """初始化股票列表"""
        # 清空列表
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)

        # 获取股票列表
        stock_symbols = self.config.get('stock_symbols', [])

        # 股票名称映射
        stock_names = {
            'AAPL': '苹果',
            'MSFT': '微软',
            'GOOGL': '谷歌',
            'AMZN': '亚马逊',
            'META': 'Meta',
            'TSLA': '特斯拉',
            'NVDA': '英伟达',
            'PYPL': 'PayPal',
            'INTC': '英特尔',
            'CSCO': '思科'
        }

        # 添加股票到列表
        for symbol in stock_symbols:
            name = stock_names.get(symbol, symbol)
            self.stock_tree.insert('', 'end', values=(symbol, name))

    def add_stock(self):
        """添加股票"""
        code = self.stock_code_var.get().upper()
        name = self.stock_name_var.get()

        if not code:
            messagebox.showwarning("警告", "请输入股票代码")
            return

        # 检查是否已存在
        for item in self.stock_tree.get_children():
            if self.stock_tree.item(item)['values'][0] == code:
                messagebox.showwarning("警告", f"股票 {code} 已存在")
                return

        # 添加到列表
        self.stock_tree.insert('', 'end', values=(
            code, name if name else code))

        # 清空输入框
        self.stock_code_var.set("")
        self.stock_name_var.set("")

    def remove_stock(self):
        """删除股票"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的股票")
            return

        # 删除选中的股票
        for item in selection:
            self.stock_tree.delete(item)

    def init_source_list(self):
        """初始化新闻来源列表"""
        # 清空列表
        for item in self.source_tree.get_children():
            self.source_tree.delete(item)

        # 获取新闻来源列表
        news_sources = self.config.get('news_sources', [])

        # 添加新闻来源到列表
        for source in news_sources:
            self.source_tree.insert('', 'end', values=(source,))

    def add_source(self):
        """添加新闻来源"""
        source = self.source_var.get().strip()

        if not source:
            messagebox.showwarning("警告", "请输入新闻来源")
            return

        # 检查是否已存在
        for item in self.source_tree.get_children():
            if self.source_tree.item(item)['values'][0] == source:
                messagebox.showwarning("警告", f"新闻来源 {source} 已存在")
                return

        # 添加到列表
        self.source_tree.insert('', 'end', values=(source,))

        # 清空输入框
        self.source_var.set("")

    def remove_source(self):
        """删除新闻来源"""
        selection = self.source_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的新闻来源")
            return

        # 删除选中的新闻来源
        for item in selection:
            self.source_tree.delete(item)

    def save_settings(self):
        """保存设置"""
        try:
            # 获取股票列表
            stock_symbols = []
            for item in self.stock_tree.get_children():
                stock_symbols.append(self.stock_tree.item(item)['values'][0])

            # 获取新闻来源列表
            news_sources = []
            for item in self.source_tree.get_children():
                news_sources.append(self.source_tree.item(item)['values'][0])

            # 更新配置
            config_updates = {
                'api_keys': {
                    'news_api': self.news_api_var.get(),
                    'alpha_vantage': self.alpha_vantage_var.get(),
                    'quandl': self.quandl_var.get()
                },
                'stock_symbols': stock_symbols,
                'news_sources': news_sources,
                'news_query': self.news_query_var.get(),
                'data_settings': {
                    'use_mock_data': self.use_mock_data_var.get(),
                    'historical_data_years': self.historical_years_var.get(),
                    'max_news_articles': self.max_news_var.get()
                },
                'model_parameters': {
                    'prediction_days': self.prediction_days_var.get(),
                    'lstm_units': self.lstm_units_var.get(),
                    'dropout_rate': self.dropout_var.get(),
                    'epochs': self.epochs_var.get(),
                    'batch_size': self.batch_var.get(),
                    'train_test_split': self.split_var.get()
                },
                'visualization': {
                    'figure_size': [self.fig_width_var.get(), self.fig_height_var.get()],
                    'color_palette': self.color_var.get(),
                    'save_plots': self.save_plots_var.get()
                },
                'ui_settings': {
                    'theme': self.theme_var.get()
                },
                'refresh_interval': self.refresh_var.get()
            }

            # 保存配置
            self.app.config_manager.update(config_updates)

            # 更新应用配置
            self.app.config = self.app.config_manager.config

            # 应用主题设置
            self.app.style.set_theme(self.theme_var.get())

            # 显示成功消息
            messagebox.showinfo("成功", "设置已保存")

        except Exception as e:
            messagebox.showerror("错误", f"保存设置时出错: {str(e)}")

    def reset_settings(self):
        """重置设置为默认值"""
        if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
            try:
                # 重置配置
                self.app.config_manager.reset_to_default()

                # 更新应用配置
                self.app.config = self.app.config_manager.config

                # 重新初始化UI
                self.init_ui_from_config()

                # 显示成功消息
                messagebox.showinfo("成功", "设置已重置为默认值")

            except Exception as e:
                messagebox.showerror("错误", f"重置设置时出错: {str(e)}")

    def init_ui_from_config(self):
        """从配置初始化UI"""
        # API设置
        self.news_api_var.set(self.config.get(
            'api_keys', {}).get('news_api', ''))
        self.alpha_vantage_var.set(self.config.get(
            'api_keys', {}).get('alpha_vantage', ''))
        self.quandl_var.set(self.config.get('api_keys', {}).get('quandl', ''))

        # 数据源设置
        self.use_mock_data_var.set(self.config.get(
            'data_settings', {}).get('use_mock_data', True))
        self.historical_years_var.set(self.config.get(
            'data_settings', {}).get('historical_data_years', 5))
        self.max_news_var.set(self.config.get(
            'data_settings', {}).get('max_news_articles', 100))

        # 股票列表
        self.init_stock_list()

        # 新闻设置
        self.news_query_var.set(self.config.get(
            'news_query', 'artificial intelligence'))
        self.init_source_list()

        # 模型设置
        self.prediction_days_var.set(self.config.get(
            'model_parameters', {}).get('prediction_days', 30))
        self.lstm_units_var.set(self.config.get(
            'model_parameters', {}).get('lstm_units', 50))
        self.dropout_var.set(self.config.get(
            'model_parameters', {}).get('dropout_rate', 0.2))
        self.epochs_var.set(self.config.get(
            'model_parameters', {}).get('epochs', 50))
        self.batch_var.set(self.config.get(
            'model_parameters', {}).get('batch_size', 32))
        self.split_var.set(self.config.get(
            'model_parameters', {}).get('train_test_split', 0.8))

        # UI设置
        self.theme_var.set(self.config.get(
            'ui_settings', {}).get('theme', 'arc'))
        self.fig_width_var.set(self.config.get(
            'visualization', {}).get('figure_size', [12, 8])[0])
        self.fig_height_var.set(self.config.get(
            'visualization', {}).get('figure_size', [12, 8])[1])
        self.color_var.set(self.config.get(
            'visualization', {}).get('color_palette', 'viridis'))
        self.save_plots_var.set(self.config.get(
            'visualization', {}).get('save_plots', True))
        self.refresh_var.set(self.config.get('refresh_interval', 300))

    def export_config(self):
        """导出配置"""
        try:
            # 选择保存路径
            file_path = filedialog.asksaveasfilename(
                title="导出配置",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )

            if not file_path:
                return

            # 保存配置
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            # 显示成功消息
            messagebox.showinfo("成功", f"配置已导出到 {file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"导出配置时出错: {str(e)}")

    def import_config(self):
        """导入配置"""
        try:
            # 选择文件路径
            file_path = filedialog.askopenfilename(
                title="导入配置",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )

            if not file_path:
                return

            # 读取配置
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # 更新配置
            self.app.config_manager.update(imported_config)

            # 更新应用配置
            self.app.config = self.app.config_manager.config

            # 重新初始化UI
            self.init_ui_from_config()

            # 应用主题设置
            self.app.style.set_theme(self.theme_var.get())

            # 显示成功消息
            messagebox.showinfo("成功", "配置已导入")

        except Exception as e:
            messagebox.showerror("错误", f"导入配置时出错: {str(e)}")
