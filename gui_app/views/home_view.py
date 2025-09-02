import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import seaborn as sns
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta


class Visualizer:
    def __init__(self, config):
        if not isinstance(config, dict):
            logging.getLogger(__name__).warning(
                "Visualizer 收到的 config 不是 dict，将使用默认配置"
            )
            config = {}
        self.config = config
        """初始化可视化工具"""
        self.config = config
        self.figure_size = config.get(
            'visualization', {}).get('figure_size', [12, 8])
        self.color_palette = config.get(
            'visualization', {}).get('color_palette', 'viridis')
        self.save_plots = config.get(
            'visualization', {}).get('save_plots', True)
        self.plot_format = config.get(
            'visualization', {}).get('plot_format', 'png')
        self.plot_dpi = config.get('visualization', {}).get('plot_dpi', 300)

        # 设置中文字体（在 macOS 上优先使用系统可用字体）
        cn_font_candidates = [
            'PingFang SC',        # macOS 系统中文字体
            'Hiragino Sans GB',   # macOS/日文环境常见
            'Heiti SC', 'STHeiti',
            'Noto Sans CJK SC',   # Google 思源黑体
            'Source Han Sans SC',
            'WenQuanYi Zen Hei'   # Linux 常见
        ]
        available = set(f.name for f in font_manager.fontManager.ttflist)
        chosen = None
        for name in cn_font_candidates:
            if name in available:
                chosen = name
                break
        # 如果没有中文字体可用，chosen 仍为 None，matplotlib 会回退到默认字体
        if chosen:
            plt.rcParams['font.sans-serif'] = [chosen]
            sns.set(style='whitegrid', font=chosen,
                    rc={'axes.unicode_minus': False})
        else:
            sns.set(style='whitegrid', rc={'axes.unicode_minus': False})
        plt.rcParams['axes.unicode_minus'] = False

        # 日志器与输出目录
        self.logger = logging.getLogger(__name__)
        # 确保图像目录存在（.../static/images）
        images_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'static', 'images'
        )
        os.makedirs(images_dir, exist_ok=True)
    def _setup_date_axis(self, ax):
        """让日期轴更智能：使用自动 locator 和简洁 formatter。"""
        locator = mdates.AutoDateLocator(minticks=5, maxticks=8)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

    def plot_stock_data(self, data, symbol, save_path=None, show_volume=True, show_indicators=True):
        """绘制股票数据图表"""
        if data.empty:
            self.logger.warning("股票数据为空，无法绘制图表")
            return None

        try:
            # 创建图表
            fig, axes = plt.subplots(4, 1, figsize=self.figure_size, sharex=True,
                                     gridspec_kw={'height_ratios': [3, 1, 1, 1]})

            # 绘制K线图
            self._plot_candlestick(axes[0], data)
            self._setup_date_axis(axes[0])

            # 添加移动平均线
            if show_indicators and 'MA20' in data.columns:
                axes[0].plot(data.index, data['MA20'],
                             label='MA20', color='blue', alpha=0.75)

            if show_indicators and 'MA50' in data.columns:
                axes[0].plot(data.index, data['MA50'],
                             label='MA50', color='red', alpha=0.75)

            # 添加布林带
            if show_indicators and all(col in data.columns for col in ['BB_upper', 'BB_middle', 'BB_lower']):
                axes[0].plot(data.index, data['BB_upper'], label='布林带上轨',
                             color='gray', alpha=0.5, linestyle='--')
                axes[0].plot(data.index, data['BB_middle'],
                             label='布林带中轨', color='gray', alpha=0.5)
                axes[0].plot(data.index, data['BB_lower'], label='布林带下轨',
                             color='gray', alpha=0.5, linestyle='--')
                axes[0].fill_between(
                    data.index, data['BB_upper'], data['BB_lower'], color='gray', alpha=0.1)

            # 设置标题和图例
            axes[0].set_title(f'{symbol} 股价走势')
            axes[0].legend(loc='upper left')

            # 绘制成交量
            if show_volume:
                self._plot_volume(axes[1], data)
                self._setup_date_axis(axes[1])

            # 绘制RSI
            if show_indicators and 'RSI' in data.columns:
                self._plot_rsi(axes[2], data)
                self._setup_date_axis(axes[2])

            # 绘制MACD
            if show_indicators and all(col in data.columns for col in ['MACD', 'MACD_signal', 'MACD_hist']):
                self._plot_macd(axes[3], data)
                self._setup_date_axis(axes[3])

            # 只保留最底部子图的 x 轴刻度标签
            for ax in axes[:-1]:
                ax.label_outer()

            # 调整布局
            plt.tight_layout()

            # 保存图表
            if self.save_plots:
                if save_path is None:
                    save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                             'static', 'images', f'{symbol}_stock_data.{self.plot_format}')
                plt.savefig(save_path, format=self.plot_format,
                            dpi=self.plot_dpi)
                self.logger.info(f"股票数据图表已保存到 {save_path}")

            return fig
        except Exception as e:
            self.logger.error(f"绘制股票数据图表时出错: {str(e)}")
            return None

    def _plot_candlestick(self, ax, data):
        """绘制K线图"""
        # 定义上涨和下跌的颜色
        up_color = 'red'
        down_color = 'green'

        # 计算上涨和下跌
        up = data[data['Close'] >= data['Open']]
        down = data[data['Close'] < data['Open']]

        # 绘制上涨K线
        ax.bar(up.index, up['Close'] - up['Open'],
               bottom=up['Open'], width=0.6, color=up_color)
        ax.bar(up.index, up['High'] - up['Close'],
               bottom=up['Close'], width=0.1, color=up_color)
        ax.bar(up.index, up['Low'] - up['Open'],
               bottom=up['Open'], width=0.1, color=up_color)

        # 绘制下跌K线
        ax.bar(down.index, down['Close'] - down['Open'],
               bottom=down['Open'], width=0.6, color=down_color)
        ax.bar(down.index, down['High'] - down['Open'],
               bottom=down['Open'], width=0.1, color=down_color)
        ax.bar(down.index, down['Low'] - down['Close'],
               bottom=down['Close'], width=0.1, color=down_color)

        # 设置y轴标签
        ax.set_ylabel('价格')

    def _plot_volume(self, ax, data):
        """绘制成交量"""
        # 定义上涨和下跌的颜色
        up_color = 'red'
        down_color = 'green'

        # 计算上涨和下跌
        up = data[data['Close'] >= data['Open']]
        down = data[data['Close'] < data['Open']]

        # 绘制成交量
        ax.bar(up.index, up['Volume'], color=up_color, alpha=0.5)
        ax.bar(down.index, down['Volume'], color=down_color, alpha=0.5)

        # 设置y轴标签
        ax.set_ylabel('成交量')

    def _plot_rsi(self, ax, data):
        """绘制RSI指标"""
        # 绘制RSI线
        ax.plot(data.index, data['RSI'], label='RSI', color='purple')

        # 添加超买超卖线
        ax.axhline(70, color='red', linestyle='--', alpha=0.5)
        ax.axhline(30, color='green', linestyle='--', alpha=0.5)

        # 设置y轴标签和范围
        ax.set_ylabel('RSI')
        ax.set_ylim(0, 100)

    def _plot_macd(self, ax, data):
        """绘制MACD指标"""
        # 绘制MACD线
        ax.plot(data.index, data['MACD'], label='MACD', color='blue')
        ax.plot(data.index, data['MACD_signal'], label='MACD信号', color='red')

        # 绘制MACD柱状图
        colors = ['green' if val >= 0 else 'red' for val in data['MACD_hist']]
        ax.bar(data.index, data['MACD_hist'],
               color=colors, alpha=0.5, width=0.8)

        # 添加零线
        ax.axhline(0, color='black', linestyle='-', alpha=0.3)

        # 设置y轴标签
        ax.set_ylabel('MACD')
        ax.legend(loc='upper left')

    def plot_prediction_results(self, actual, predicted, symbol, save_path=None):
        """绘制预测结果图表"""
        if actual is None or predicted is None or len(actual) == 0 or len(predicted) == 0:
            self.logger.warning("预测结果数据为空，无法绘制图表")
            return None

        try:
            # 创建图表
            fig, ax = plt.subplots(figsize=self.figure_size)

            # 绘制实际值
            ax.plot(actual, label='实际价格', color='blue', linewidth=2)

            # 绘制预测值
            ax.plot(predicted, label='预测价格', color='red',
                    linewidth=2, linestyle='--')

            # 设置标题和图例
            ax.set_title(f'{symbol} 股价预测结果')
            ax.legend(loc='upper left')

            # 设置坐标轴标签
            ax.set_xlabel('时间')
            ax.set_ylabel('价格')

            # 调整布局
            plt.tight_layout()

            # 保存图表
            if self.save_plots:
                if save_path is None:
                    save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                             'static', 'images', f'{symbol}_prediction_results.{self.plot_format}')
                plt.savefig(save_path, format=self.plot_format,
                            dpi=self.plot_dpi)
                self.logger.info(f"预测结果图表已保存到 {save_path}")

            return fig
        except Exception as e:
            self.logger.error(f"绘制预测结果图表时出错: {str(e)}")
            return None

    def plot_future_predictions(self, historical_data, future_predictions, symbol, save_path=None):
        """绘制未来预测图表"""
        if historical_data is None or future_predictions is None or len(historical_data) == 0 or len(future_predictions) == 0:
            self.logger.warning("未来预测数据为空，无法绘制图表")
            return None

        try:
            # 创建图表
            fig, ax = plt.subplots(figsize=self.figure_size)

            # 绘制历史数据
            ax.plot(historical_data, label='历史价格', color='blue', linewidth=2)

            # 绘制未来预测
            future_x = range(len(historical_data), len(
                historical_data) + len(future_predictions))
            ax.plot(future_x, future_predictions, label='未来预测',
                    color='red', linewidth=2, linestyle='--')

            # 添加预测区域
            ax.axvspan(len(historical_data), len(historical_data) + len(future_predictions),
                       alpha=0.1, color='red')

            # 设置标题和图例
            ax.set_title(f'{symbol} 未来股价预测')
            ax.legend(loc='upper left')

            # 设置坐标轴标签
            ax.set_xlabel('时间')
            ax.set_ylabel('价格')

            # 调整布局
            plt.tight_layout()

            # 保存图表
            if self.save_plots:
                if save_path is None:
                    save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                             'static', 'images', f'{symbol}_future_predictions.{self.plot_format}')
                plt.savefig(save_path, format=self.plot_format,
                            dpi=self.plot_dpi)
                self.logger.info(f"未来预测图表已保存到 {save_path}")

            return fig
        except Exception as e:
            self.logger.error(f"绘制未来预测图表时出错: {str(e)}")
            return None

    def plot_news_sentiment(self, news_data, save_path=None):
        """绘制新闻情感分析图表"""
        if not news_data:
            self.logger.warning("新闻数据为空，无法绘制情感分析图表")
            return None

        try:
            # 创建DataFrame
            news_df = pd.DataFrame(news_data)

            # 确保有日期列
            if 'publishedAt' in news_df.columns:
                news_df['date'] = pd.to_datetime(
                    news_df['publishedAt']).dt.date
            else:
                self.logger.warning("新闻数据中没有发布日期，无法按时间分析情感")
                return None

            # 按日期分组，计算每日情感得分
            daily_sentiment = news_df.groupby('date').agg({
                'vader_compound': 'mean',
                'vader_positive': 'mean',
                'vader_negative': 'mean',
                'vader_neutral': 'mean',
                'textblob_polarity': 'mean'
            }).reset_index()

            # 创建子图
            fig, axes = plt.subplots(2, 1, figsize=self.figure_size)

            # 绘制情感得分时间序列
            axes[0].plot(daily_sentiment['date'], daily_sentiment['vader_compound'],
                         label='VADER综合得分', color='blue')
            axes[0].plot(daily_sentiment['date'], daily_sentiment['textblob_polarity'],
                         label='TextBlob极性得分', color='green')

            # 添加零线
            axes[0].axhline(0, color='gray', linestyle='--', alpha=0.5)

            # 设置标题和图例
            axes[0].set_title('新闻情感得分时间序列')
            axes[0].legend(loc='upper left')

            # 设置日期轴格式
            self._setup_date_axis(axes[0])

            # 设置y轴标签
            axes[0].set_ylabel('情感得分')

            # 计算情感分布
            sentiment_counts = news_df['sentiment'].value_counts()

            # 绘制情感分布饼图
            axes[1].pie(sentiment_counts.values,
                        labels=sentiment_counts.index, autopct='%1.1f%%')
            axes[1].set_title('新闻情感分布')

            # 调整布局
            plt.tight_layout()

            # 保存图表
            if self.save_plots:
                if save_path is None:
                    save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                             'static', 'images', f'news_sentiment.{self.plot_format}')
                plt.savefig(save_path, format=self.plot_format,
                            dpi=self.plot_dpi)
                self.logger.info(f"新闻情感分析图表已保存到 {save_path}")

            return fig
        except Exception as e:
            self.logger.error(f"绘制新闻情感分析图表时出错: {str(e)}")
            return None

    def plot_stock_news_correlation(self, stock_data, news_data, symbol, save_path=None):
        """绘制股票与新闻情感相关性图表"""
        if stock_data.empty or not news_data:
            self.logger.warning("股票数据或新闻数据为空，无法绘制相关性图表")
            return None

        try:
            # 确保股票数据有日期索引
            if not isinstance(stock_data.index, pd.DatetimeIndex):
                stock_data.index = pd.to_datetime(stock_data.index)

            # 创建新闻DataFrame
            news_df = pd.DataFrame(news_data)

            # 确保新闻数据有日期列
            if 'publishedAt' in news_df.columns:
                news_df['date'] = pd.to_datetime(
                    news_df['publishedAt']).dt.date
            else:
                self.logger.warning("新闻数据中没有发布日期，无法分析与股票的相关性")
                return None

            # 按日期分组新闻，计算每日情感得分
            daily_sentiment = news_df.groupby('date').agg({
                'vader_compound': 'mean',
                'vader_positive': 'mean',
                'vader_negative': 'mean',
                'vader_neutral': 'mean',
                'textblob_polarity': 'mean'
            }).reset_index()

            # 转换日期格式以匹配股票数据
            daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])

            # 计算股票日收益率
            stock_data_copy = stock_data.copy()
            stock_data_copy['Daily_Return'] = stock_data_copy['Close'].pct_change(
            ) * 100

            # 为股票数据添加日期列（用于合并）
            stock_data_copy['date'] = stock_data_copy.index.date

            # 合并数据
            merged_data = pd.merge(
                stock_data_copy,
                daily_sentiment,
                on='date',
                how='left'
            )

            # 填充NaN值
            sentiment_cols = ['vader_compound', 'vader_positive', 'vader_negative',
                              'vader_neutral', 'textblob_polarity']
            merged_data[sentiment_cols] = merged_data[sentiment_cols].fillna(
                method='ffill').fillna(0)

            # 创建子图
            fig, axes = plt.subplots(3, 1, figsize=self.figure_size)

            # 绘制股价和收益率
            ax1 = axes[0]
            ax2 = ax1.twinx()

            # 绘制股价
            ax1.plot(merged_data.index,
                     merged_data['Close'], label='收盘价', color='blue')
            ax1.set_ylabel('价格', color='blue')
            ax1.tick_params(axis='y', labelcolor='blue')

            # 绘制收益率
            ax2.plot(merged_data.index,
                     merged_data['Daily_Return'], label='日收益率 (%)', color='green')
            ax2.set_ylabel('收益率 (%)', color='green')
            ax2.tick_params(axis='y', labelcolor='green')

            # 设置标题
            ax1.set_title(f'{symbol} 股价与收益率')

            # 绘制情感得分
            axes[1].plot(merged_data.index, merged_data['vader_compound'],
                         label='VADER综合得分', color='red')
            axes[1].plot(merged_data.index, merged_data['textblob_polarity'],
                         label='TextBlob极性得分', color='purple')

            # 添加零线
            axes[1].axhline(0, color='gray', linestyle='--', alpha=0.5)

            # 设置标题和图例
            axes[1].set_title('新闻情感得分')
            axes[1].legend(loc='upper left')

            # 设置y轴标签
            axes[1].set_ylabel('情感得分')

            # 计算并添加相关性
            window = 10  # 10天滚动窗口
            correlation_vader = merged_data['Daily_Return'].rolling(
                window=window).corr(merged_data['vader_compound'])
            correlation_textblob = merged_data['Daily_Return'].rolling(
                window=window).corr(merged_data['textblob_polarity'])

            axes[2].plot(merged_data.index, correlation_vader,
                         label=f'收益率与VADER得分相关性 ({window}天滚动)', color='red')
            axes[2].plot(merged_data.index, correlation_textblob,
                         label=f'收益率与TextBlob得分相关性 ({window}天滚动)', color='purple')

            # 添加零线
            axes[2].axhline(0, color='gray', linestyle='--', alpha=0.5)

            # 设置标题和图例
            axes[2].set_title('股价与新闻情感相关性')
            axes[2].legend(loc='upper left')

            # 设置y轴标签
            axes[2].set_ylabel('相关性系数')
            axes[2].set_xlabel('日期')

            # 设置x轴格式
            for ax in axes:
                self._setup_date_axis(ax)
            for ax in axes[:-1]:
                ax.label_outer()

            # 调整布局
            plt.tight_layout()

            # 保存图表
            if self.save_plots:
                if save_path is None:
                    save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                             'static', 'images', f'{symbol}_news_correlation.{self.plot_format}')
                plt.savefig(save_path, format=self.plot_format,
                            dpi=self.plot_dpi)
                self.logger.info(f"股票与新闻情感相关性图表已保存到 {save_path}")

            return fig
        except Exception as e:
            self.logger.error(f"绘制股票与新闻情感相关性图表时出错: {str(e)}")
            return None

    def plot_technical_signals(self, data, signals, symbol, save_path=None):
        """绘制技术信号图表"""
        if data.empty or not signals:
            self.logger.warning("股票数据或技术信号为空，无法绘制图表")
            return None

        try:
            # 创建图表
            fig, ax = plt.subplots(figsize=self.figure_size)

            # 绘制K线图
            self._plot_candlestick(ax, data)

            # 添加移动平均线
            if 'MA20' in data.columns:
                ax.plot(data.index, data['MA20'],
                        label='MA20', color='blue', alpha=0.75)

            if 'MA50' in data.columns:
                ax.plot(data.index, data['MA50'],
                        label='MA50', color='red', alpha=0.75)

            # 添加布林带
            if all(col in data.columns for col in ['BB_upper', 'BB_middle', 'BB_lower']):
                ax.plot(data.index, data['BB_upper'], label='布林带上轨',
                        color='gray', alpha=0.5, linestyle='--')
                ax.plot(data.index, data['BB_middle'],
                        label='布林带中轨', color='gray', alpha=0.5)
                ax.plot(data.index, data['BB_lower'], label='布林带下轨',
                        color='gray', alpha=0.5, linestyle='--')
                ax.fill_between(
                    data.index, data['BB_upper'], data['BB_lower'], color='gray', alpha=0.1)

            # 添加技术信号标记
            last_date = data.index[-1]
            last_close = data['Close'].iloc[-1]

            # 添加信号文本
            signal_text = "技术信号:\n"
            for indicator, signal in signals.items():
                signal_text += f"{indicator}: {signal}\n"

            # 在图表上添加信号文本
            ax.text(0.02, 0.98, signal_text, transform=ax.transAxes,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            # 设置标题
            ax.set_title(f'{symbol} 技术分析信号')

            # 调整布局
            plt.tight_layout()

            # 保存图表
            if self.save_plots:
                if save_path is None:
                    save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                             'static', 'images', f'{symbol}_technical_signals.{self.plot_format}')
                plt.savefig(save_path, format=self.plot_format,
                            dpi=self.plot_dpi)
                self.logger.info(f"技术信号图表已保存到 {save_path}")

            return fig
        except Exception as e:
            self.logger.error(f"绘制技术信号图表时出错: {str(e)}")
            return None
class HomeView(tk.Frame):
    """首页视图：继承自 tk.Frame，支持 pack/grid/place，并委托可视化给 Visualizer"""
    def __init__(self, parent, app_or_config=None):
        # 兼容两种传参：HomeView(parent, app) 或 HomeView(parent, config_dict)
        super().__init__(parent)
        if isinstance(app_or_config, dict) or app_or_config is None:
            config = app_or_config or {}
            self.app = None
        else:
            self.app = app_or_config
            config = getattr(self.app, 'config', {})

        # 内部可视化器
        self._viz = Visualizer(config)

        # 基本 UI 占位（避免空白导致布局问题）
        self._header = ttk.Label(self, text="首页", font=("Arial", 14, "bold"))
        self._header.pack(anchor="w", padx=10, pady=10)

        # 使用说明
        help_text = (
            "使用提示：\n"
            "1) 左侧选择 ‘股票分析’ 进入主功能界面。\n"
            "2) 顶部输入股票代码或从下拉框选择，然后点 ‘搜索/刷新’。\n"
            "3) 如弹出 ‘Date’ 相关错误，请确保数据中有日期索引：\n"
            "   例如在数据抓取后执行 data.index = pd.to_datetime(data.index); data.index.name = 'Date'。\n"
            "4) 首次运行会自动下载并处理配置里的股票列表，稍等几秒即可。"
        )
        self._help = ttk.Label(self, text=help_text, justify="left")
        self._help.pack(anchor="w", padx=10, pady=(0,10))

        # 数据占位
        self._stock_data = {}
        self._news_data = []

    # 供 app.py 调用，用于注入数据
    def update_data(self, stock_data, news_data):
        self._stock_data = stock_data or {}
        self._news_data = news_data or []
        # 这里可以根据需要刷新界面；先简单更新标题中的数量信息
        try:
            stocks_cnt = len(self._stock_data) if isinstance(self._stock_data, dict) else 0
            news_cnt = len(self._news_data) if isinstance(self._news_data, (list, tuple)) else 0
            self._header.config(text=f"首页（股票: {stocks_cnt}，新闻: {news_cnt}）")
        except Exception:
            pass

    # 以下方法保持向后兼容：对外暴露与旧版一致的绘图 API
    def plot_stock_data(self, *args, **kwargs):
        return self._viz.plot_stock_data(*args, **kwargs)

    def plot_prediction_results(self, *args, **kwargs):
        return self._viz.plot_prediction_results(*args, **kwargs)

    def plot_future_predictions(self, *args, **kwargs):
        return self._viz.plot_future_predictions(*args, **kwargs)

    def plot_news_sentiment(self, *args, **kwargs):
        return self._viz.plot_news_sentiment(*args, **kwargs)

    def plot_stock_news_correlation(self, *args, **kwargs):
        return self._viz.plot_stock_news_correlation(*args, **kwargs)

    def plot_technical_signals(self, *args, **kwargs):
        return self._viz.plot_technical_signals(*args, **kwargs)