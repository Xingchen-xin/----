import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime
import os


class NewsView(ttk.Frame):
    def __init__(self, parent, app):
        """初始化新闻资讯视图"""
        super().__init__(parent)
        self.app = app
        self.news_data = []
        self.filtered_news = []

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        """创建UI组件"""
        # 创建顶部框架 - 搜索和筛选
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 创建搜索框
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search_key_release)

        # 创建搜索按钮
        search_button = ttk.Button(
            search_frame,
            text="搜索",
            command=self.search_news
        )
        search_button.pack(side=tk.LEFT, padx=(0, 10))

        # 创建情感筛选
        ttk.Label(search_frame, text="情感:").pack(side=tk.LEFT, padx=(0, 5))

        self.sentiment_var = tk.StringVar(value="all")
        sentiment_dropdown = ttk.Combobox(
            search_frame,
            textvariable=self.sentiment_var,
            values=["all", "positive", "negative", "neutral"],
            width=10,
            state="readonly"
        )
        sentiment_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        sentiment_dropdown.bind("<<ComboboxSelected>>",
                                self.on_sentiment_selected)

        # 创建刷新按钮
        refresh_button = ttk.Button(
            search_frame,
            text="刷新",
            command=self.refresh_news
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        # 创建中间框架 - 分为左右两部分
        middle_frame = ttk.Frame(self)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建左侧框架 - 新闻列表
        left_frame = ttk.LabelFrame(middle_frame, text="新闻列表", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建新闻列表
        self.create_news_list(left_frame)

        # 创建右侧框架 - 新闻详情和情感分析
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 创建新闻详情框架
        detail_frame = ttk.LabelFrame(right_frame, text="新闻详情", padding=5)
        detail_frame.pack(fill=tk.BOTH, expand=True)

        # 创建新闻详情文本框
        self.create_news_detail(detail_frame)

        # 创建情感分析框架
        sentiment_frame = ttk.LabelFrame(right_frame, text="情感分析", padding=5)
        sentiment_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 创建情感分析图表
        self.create_sentiment_chart(sentiment_frame)

    def create_news_list(self, parent):
        """创建新闻列表"""
        # 创建列表框架
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建列表
        columns = ('日期', '来源', '标题', '情感')
        self.news_tree = ttk.Treeview(
            list_frame, columns=columns, show='headings')

        # 设置列标题
        self.news_tree.heading('日期', text='日期')
        self.news_tree.heading('来源', text='来源')
        self.news_tree.heading('标题', text='标题')
        self.news_tree.heading('情感', text='情感')

        # 设置列宽
        self.news_tree.column('日期', width=80)
        self.news_tree.column('来源', width=80)
        self.news_tree.column('标题', width=300)
        self.news_tree.column('情感', width=60)

        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.news_tree.yview)
        h_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.HORIZONTAL, command=self.news_tree.xview)
        self.news_tree.configure(
            yscroll=v_scrollbar.set, xscroll=h_scrollbar.set)

        # 放置列表和滚动条
        self.news_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定选择事件
        self.news_tree.bind("<<TreeviewSelect>>", self.on_news_select)
        self.news_tree.bind("<Double-1>", self.on_news_double_click)

    def create_news_detail(self, parent):
        """创建新闻详情"""
        # 创建文本框框架
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # 创建文本框
        self.detail_text = tk.Text(
            text_frame, wrap=tk.WORD, font=('Arial', 10))
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        detail_scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscroll=detail_scrollbar.set)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 设置文本框为只读
        self.detail_text.config(state=tk.DISABLED)

    def create_sentiment_chart(self, parent):
        """创建情感分析图表"""
        # 创建图表框架
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 初始化图表
        self.update_sentiment_chart()

    def update_news(self, news_data):
        """更新新闻数据"""
        self.news_data = news_data
        self.filtered_news = news_data.copy()

        # 更新新闻列表
        self.update_news_list()

        # 更新情感分析图表
        self.update_sentiment_chart()

    def update_news_list(self):
        """更新新闻列表"""
        # 清空列表
        for item in self.news_tree.get_children():
            self.news_tree.delete(item)

        # 添加新闻数据
        for article in self.filtered_news:
            # 获取日期
            date_str = article.get('publishedAt', '')[:10]  # 只显示日期部分

            # 获取来源
            source = article.get('source', {}).get('name', '未知来源')

            # 获取标题
            title = article.get('title', '无标题')

            # 获取情感
            sentiment = article.get('sentiment', 'neutral')

            # 设置情感颜色
            sentiment_color = {
                'positive': 'green',
                'negative': 'red',
                'neutral': 'gray'
            }.get(sentiment, 'gray')

            # 添加到列表
            item = self.news_tree.insert('', 'end', values=(
                date_str, source, title, sentiment))

            # 设置情感颜色
            self.news_tree.set(item, '情感', sentiment)
            self.news_tree.tag_configure(sentiment, foreground=sentiment_color)
            self.news_tree.item(item, tags=(sentiment,))

    def update_sentiment_chart(self):
        """更新情感分析图表"""
        # 清空图表
        self.ax.clear()

        # 计算情感分布
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for article in self.filtered_news:
            sentiment = article.get('sentiment', 'neutral')
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

        # 绘制饼图
        labels = ['正面', '负面', '中性']
        sizes = [sentiment_counts['positive'],
                 sentiment_counts['negative'], sentiment_counts['neutral']]
        colors = ['green', 'red', 'gray']
        explode = (0.05, 0.05, 0)  # 突出显示正面和负面

        self.ax.pie(sizes, explode=explode, labels=labels,
                    colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
        self.ax.axis('equal')  # 使饼图呈圆形

        # 设置标题
        self.ax.set_title('新闻情感分布')

        # 更新画布
        self.canvas.draw()

    def on_search_key_release(self, event):
        """搜索框按键释放事件处理"""
        self.filter_news()

    def search_news(self):
        """搜索新闻"""
        self.filter_news()

    def filter_news(self):
        """筛选新闻"""
        # 获取搜索关键词
        keyword = self.search_entry.get().lower()

        # 获取情感筛选
        sentiment = self.sentiment_var.get()

        # 筛选新闻
        self.filtered_news = []
        for article in self.news_data:
            # 检查关键词
            if keyword:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                if keyword not in title and keyword not in description:
                    continue

            # 检查情感
            if sentiment != 'all':
                article_sentiment = article.get('sentiment', 'neutral')
                if article_sentiment != sentiment:
                    continue

            # 添加到筛选结果
            self.filtered_news.append(article)

        # 更新新闻列表
        self.update_news_list()

        # 更新情感分析图表
        self.update_sentiment_chart()

    def on_sentiment_selected(self, event):
        """情感选择事件处理"""
        self.filter_news()

    def on_news_select(self, event):
        """新闻选择事件处理"""
        # 获取选中的新闻
        selection = self.news_tree.selection()
        if selection:
            item = self.news_tree.item(selection[0])
            index = self.news_tree.index(selection[0])

            if index < len(self.filtered_news):
                # 获取新闻详情
                article = self.filtered_news[index]

                # 显示新闻详情
                self.show_news_detail(article)

    def on_news_double_click(self, event):
        """新闻双击事件处理"""
        # 获取选中的新闻
        selection = self.news_tree.selection()
        if selection:
            item = self.news_tree.item(selection[0])
            index = self.news_tree.index(selection[0])

            if index < len(self.filtered_news):
                # 获取新闻详情
                article = self.filtered_news[index]

                # 显示新闻详情对话框
                self.show_news_detail_dialog(article)

    def show_news_detail(self, article):
        """显示新闻详情"""
        # 清空文本框
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)

        # 添加标题
        title = article.get('title', '无标题')
        self.detail_text.insert(tk.END, f"{title}\n\n", 'title')
        self.detail_text.tag_config('title', font=('Arial', 12, 'bold'))

        # 添加来源和日期
        source = article.get('source', {}).get('name', '未知来源')
        date = article.get('publishedAt', '')[:10]  # 只显示日期部分
        self.detail_text.insert(tk.END, f"来源: {source}\n")
        self.detail_text.insert(tk.END, f"日期: {date}\n\n")

        # 添加情感
        sentiment = article.get('sentiment', 'neutral')
        sentiment_text = {
            'positive': '正面',
            'negative': '负面',
            'neutral': '中性'
        }.get(sentiment, '未知')

        sentiment_color = {
            'positive': 'green',
            'negative': 'red',
            'neutral': 'gray'
        }.get(sentiment, 'black')

        self.detail_text.insert(
            tk.END, f"情感: {sentiment_text}\n\n", 'sentiment')
        self.detail_text.tag_config('sentiment', foreground=sentiment_color)

        # 添加情感得分
        vader_compound = article.get('vader_compound', 0)
        textblob_polarity = article.get('textblob_polarity', 0)

        self.detail_text.insert(tk.END, f"VADER综合得分: {vader_compound:.2f}\n")
        self.detail_text.insert(
            tk.END, f"TextBlob极性得分: {textblob_polarity:.2f}\n\n")

        # 添加描述
        description = article.get('description', '无描述')
        self.detail_text.insert(tk.END, description)

        # 设置文本框为只读
        self.detail_text.config(state=tk.DISABLED)

    def show_news_detail_dialog(self, article):
        """显示新闻详情对话框"""
        # 创建对话框
        dialog = tk.Toplevel(self)
        dialog.title("新闻详情")
        dialog.geometry("700x500")

        # 创建标题标签
        title_label = ttk.Label(
            dialog,
            text=article.get('title', '无标题'),
            font=('Arial', 14, 'bold')
        )
        title_label.pack(padx=10, pady=(10, 5), anchor=tk.W)

        # 创建来源和日期标签
        info_frame = ttk.Frame(dialog)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        source_label = ttk.Label(
            info_frame,
            text=f"来源: {article.get('source', {}).get('name', '未知来源')}"
        )
        source_label.pack(side=tk.LEFT)

        date_label = ttk.Label(
            info_frame,
            text=f"日期: {article.get('publishedAt', '')[:10]}"
        )
        date_label.pack(side=tk.RIGHT)

        # 创建情感标签
        sentiment = article.get('sentiment', 'neutral')
        sentiment_text = {
            'positive': '正面',
            'negative': '负面',
            'neutral': '中性'
        }.get(sentiment, '未知')

        sentiment_color = {
            'positive': 'green',
            'negative': 'red',
            'neutral': 'gray'
        }.get(sentiment, 'black')

        sentiment_label = ttk.Label(
            dialog,
            text=f"情感: {sentiment_text}",
            foreground=sentiment_color,
            font=('Arial', 10, 'bold')
        )
        sentiment_label.pack(padx=10, pady=(0, 10), anchor=tk.W)

        # 创建情感得分框架
        scores_frame = ttk.Frame(dialog)
        scores_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        vader_compound = article.get('vader_compound', 0)
        textblob_polarity = article.get('textblob_polarity', 0)

        ttk.Label(scores_frame, text=f"VADER综合得分: {vader_compound:.2f}").pack(
            side=tk.LEFT, padx=(0, 20))
        ttk.Label(scores_frame, text=f"TextBlob极性得分: {textblob_polarity:.2f}").pack(
            side=tk.LEFT)

        # 创建描述文本框
        desc_frame = ttk.Frame(dialog)
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        desc_text = tk.Text(desc_frame, wrap=tk.WORD, font=('Arial', 10))
        desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        desc_scrollbar = ttk.Scrollbar(
            desc_frame, orient=tk.VERTICAL, command=desc_text.yview)
        desc_text.configure(yscroll=desc_scrollbar.set)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 插入描述内容
        desc_text.insert(tk.END, article.get('description', '无描述'))
        desc_text.config(state=tk.DISABLED)

        # 创建按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 创建关闭按钮
        close_button = ttk.Button(
            button_frame,
            text="关闭",
            command=dialog.destroy
        )
        close_button.pack(side=tk.RIGHT)

        # 创建查看原文按钮
        if 'url' in article and article['url']:
            view_button = ttk.Button(
                button_frame,
                text="查看原文",
                command=lambda: self.open_url(article['url'])
            )
            view_button.pack(side=tk.RIGHT, padx=(0, 5))

    def open_url(self, url):
        """打开URL"""
        import webbrowser
        webbrowser.open(url)

    def refresh_news(self):
        """刷新新闻"""
        try:
            self.app.update_status("正在刷新新闻...")
            self.app.update_progress(10)

            # 获取新闻数据
            news_query = self.app.config.get(
                'news_query', 'artificial intelligence')
            news_data = self.app.data_fetcher.fetch_news_data(news_query)

            self.app.update_progress(50)

            # 处理新闻数据
            processed_news = self.app.data_processor.process_news_data(
                news_data)

            self.app.update_progress(90)

            # 更新数据
            self.update_news(processed_news)

            self.app.update_progress(100)
            self.app.update_status("新闻已刷新")

        except Exception as e:
            self.app.update_progress(0)
            self.app.update_status("新闻刷新失败")
            self.app.show_error("刷新错误", f"刷新新闻时出错: {str(e)}")
