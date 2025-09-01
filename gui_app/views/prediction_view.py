import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class PredictionView(ttk.Frame):
    def __init__(self, parent, app):
        """初始化预测结果视图"""
        super().__init__(parent)
        self.app = app
        self.current_symbol = None
        self.prediction_results = {}
        self.future_predictions = {}
        self.model_evaluation = {}

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        """创建UI组件"""
        # 创建顶部框架 - 股票选择和预测控制
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 创建股票选择框架
        stock_frame = ttk.Frame(top_frame)
        stock_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(stock_frame, text="股票代码:").pack(side=tk.LEFT, padx=(0, 5))

        self.stock_var = tk.StringVar()
        self.stock_dropdown = ttk.Combobox(
            stock_frame,
            textvariable=self.stock_var,
            width=10,
            state="readonly"
        )
        self.stock_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        self.stock_dropdown.bind(
            "<<ComboboxSelected>>", self.on_stock_selected)

        # 创建预测天数选择
        ttk.Label(stock_frame, text="预测天数:").pack(side=tk.LEFT, padx=(10, 5))

        self.days_var = tk.IntVar(value=30)
        days_spinbox = ttk.Spinbox(
            stock_frame,
            from_=5,
            to=90,
            textvariable=self.days_var,
            width=5
        )
        days_spinbox.pack(side=tk.LEFT, padx=(0, 10))

        # 创建按钮
        train_button = ttk.Button(
            stock_frame,
            text="训练模型",
            command=self.train_model
        )
        train_button.pack(side=tk.LEFT, padx=(0, 5))

        predict_button = ttk.Button(
            stock_frame,
            text="预测未来",
            command=self.predict_future
        )
        predict_button.pack(side=tk.LEFT, padx=(0, 5))

        refresh_button = ttk.Button(
            stock_frame,
            text="刷新",
            command=self.refresh_data
        )
        refresh_button.pack(side=tk.LEFT)

        # 创建中间框架 - 分为左右两部分
        middle_frame = ttk.Frame(self)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建左侧框架 - 预测图表
        left_frame = ttk.Frame(middle_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建预测结果图表框架
        prediction_chart_frame = ttk.LabelFrame(
            left_frame, text="预测结果", padding=5)
        prediction_chart_frame.pack(fill=tk.BOTH, expand=True)

        # 创建预测结果图表
        self.create_prediction_chart(prediction_chart_frame)

        # 创建未来预测图表框架
        future_chart_frame = ttk.LabelFrame(left_frame, text="未来预测", padding=5)
        future_chart_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 创建未来预测图表
        self.create_future_chart(future_chart_frame)

        # 创建右侧框架 - 预测数据和模型评估
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 创建预测数据框架
        prediction_data_frame = ttk.LabelFrame(
            right_frame, text="预测数据", padding=5)
        prediction_data_frame.pack(fill=tk.BOTH, expand=True)

        # 创建预测数据表格
        self.create_prediction_data_table(prediction_data_frame)

        # 创建模型评估框架
        evaluation_frame = ttk.LabelFrame(right_frame, text="模型评估", padding=5)
        evaluation_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 创建模型评估表格
        self.create_evaluation_table(evaluation_frame)

        # 创建底部框架 - 预测历史
        bottom_frame = ttk.LabelFrame(self, text="预测历史", padding=5)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # 创建预测历史表格
        self.create_history_table(bottom_frame)

    def create_prediction_chart(self, parent):
        """创建预测结果图表"""
        # 创建图表框架
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        # 创建图表
        self.prediction_fig, self.prediction_ax = plt.subplots(
            figsize=(6, 4), dpi=100)
        self.prediction_canvas = FigureCanvasTkAgg(
            self.prediction_fig, master=chart_frame)
        self.prediction_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 初始化图表
        self.update_prediction_chart()

    def create_future_chart(self, parent):
        """创建未来预测图表"""
        # 创建图表框架
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        # 创建图表
        self.future_fig, self.future_ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.future_canvas = FigureCanvasTkAgg(
            self.future_fig, master=chart_frame)
        self.future_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 初始化图表
        self.update_future_chart()

    def create_prediction_data_table(self, parent):
        """创建预测数据表格"""
        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ('日期', '实际价格', '预测价格', '误差', '误差率')
        self.prediction_table = ttk.Treeview(
            table_frame, columns=columns, show='headings', height=10)

        # 设置列标题
        for col in columns:
            self.prediction_table.heading(col, text=col)
            self.prediction_table.column(col, width=80)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.prediction_table.yview)
        self.prediction_table.configure(yscroll=scrollbar.set)

        # 放置表格和滚动条
        self.prediction_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_evaluation_table(self, parent):
        """创建模型评估表格"""
        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ('指标', '值')
        self.evaluation_table = ttk.Treeview(
            table_frame, columns=columns, show='headings', height=6)

        # 设置列标题
        self.evaluation_table.heading('指标', text='指标')
        self.evaluation_table.heading('值', text='值')
        self.evaluation_table.column('指标', width=120)
        self.evaluation_table.column('值', width=120)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.evaluation_table.yview)
        self.evaluation_table.configure(yscroll=scrollbar.set)

        # 放置表格和滚动条
        self.evaluation_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_history_table(self, parent):
        """创建预测历史表格"""
        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ('日期', '股票代码', '预测天数', '准确率', '平均误差')
        self.history_table = ttk.Treeview(
            table_frame, columns=columns, show='headings')

        # 设置列标题
        for col in columns:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, width=120)

        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.history_table.yview)
        h_scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.HORIZONTAL, command=self.history_table.xview)
        self.history_table.configure(
            yscroll=v_scrollbar.set, xscroll=h_scrollbar.set)

        # 放置表格和滚动条
        self.history_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_stock_list(self, stock_symbols):
        """更新股票列表"""
        self.stock_dropdown['values'] = stock_symbols
        if stock_symbols and not self.stock_var.get():
            self.stock_var.set(stock_symbols[0])
            self.current_symbol = stock_symbols[0]

    def on_stock_selected(self, event):
        """股票选择事件处理"""
        symbol = self.stock_var.get()
        if symbol:
            self.current_symbol = symbol
            self.update_prediction_data()

    def train_model(self):
        """训练模型"""
        if not self.current_symbol:
            self.app.show_warning("警告", "请先选择股票")
            return

        try:
            self.app.update_status(f"正在为 {self.current_symbol} 训练模型...")
            self.app.update_progress(10)

            # 获取处理后的数据
            if self.current_symbol not in self.app.processed_data:
                self.app.show_warning("警告", f"请先获取 {self.current_symbol} 的数据")
                return

            processed_data = self.app.processed_data[self.current_symbol]

            self.app.update_progress(30)

            # 准备训练数据
            X_train, X_test, y_train, y_test, scaler = self.app.data_processor.prepare_data_for_prediction(
                processed_data)

            if X_train is None:
                self.app.show_error("错误", "准备训练数据失败")
                return

            self.app.update_progress(50)

            # 训练模型
            history = self.app.prediction_model.train(
                X_train, y_train, X_test, y_test)

            self.app.update_progress(80)

            # 评估模型
            evaluation_metrics, y_test_inv, y_pred_inv = self.app.prediction_model.evaluate(
                X_test, y_test, scaler)

            if evaluation_metrics is None:
                self.app.show_error("错误", "评估模型失败")
                return

            self.app.update_progress(90)

            # 保存结果
            self.prediction_results[self.current_symbol] = {
                'y_test': y_test_inv.tolist(),
                'y_pred': y_pred_inv.tolist(),
                'evaluation_metrics': evaluation_metrics
            }

            self.model_evaluation[self.current_symbol] = evaluation_metrics

            # 更新UI
            self.update_prediction_chart()
            self.update_evaluation_table()
            self.update_prediction_data_table()

            # 添加到历史记录
            self.add_to_history(self.current_symbol, 0, evaluation_metrics)

            self.app.update_progress(100)
            self.app.update_status(f"{self.current_symbol} 模型训练完成")

        except Exception as e:
            self.app.update_progress(0)
            self.app.update_status("模型训练失败")
            self.app.show_error("训练错误", f"训练模型时出错: {str(e)}")

    def predict_future(self):
        """预测未来"""
        if not self.current_symbol:
            self.app.show_warning("警告", "请先选择股票")
            return

        try:
            self.app.update_status(f"正在预测 {self.current_symbol} 的未来价格...")
            self.app.update_progress(10)

            # 获取处理后的数据
            if self.current_symbol not in self.app.processed_data:
                self.app.show_warning("警告", f"请先获取 {self.current_symbol} 的数据")
                return

            processed_data = self.app.processed_data[self.current_symbol]

            self.app.update_progress(30)

            # 准备数据
            X_train, X_test, y_train, y_test, scaler = self.app.data_processor.prepare_data_for_prediction(
                processed_data)

            if X_train is None:
                self.app.show_error("错误", "准备预测数据失败")
                return

            self.app.update_progress(50)

            # 获取最后一段序列用于预测
            last_sequence = X_test[-1:]

            # 预测未来
            prediction_days = self.days_var.get()
            future_predictions = self.app.prediction_model.predict_future(
                last_sequence, prediction_days, scaler)

            if future_predictions is None:
                self.app.show_error("错误", "预测未来价格失败")
                return

            self.app.update_progress(80)

            # 获取历史收盘价
            historical_prices = processed_data['Close'].values.tolist()

            # 保存结果
            self.future_predictions[self.current_symbol] = {
                'historical_prices': historical_prices,
                'future_predictions': future_predictions.tolist(),
                'prediction_days': prediction_days
            }

            self.app.update_progress(90)

            # 更新UI
            self.update_future_chart()
            self.update_prediction_data_table()

            # 添加到历史记录
            if self.current_symbol in self.model_evaluation:
                self.add_to_history(
                    self.current_symbol, prediction_days, self.model_evaluation[self.current_symbol])

            self.app.update_progress(100)
            self.app.update_status(f"{self.current_symbol} 未来预测完成")

        except Exception as e:
            self.app.update_progress(0)
            self.app.update_status("未来预测失败")
            self.app.show_error("预测错误", f"预测未来价格时出错: {str(e)}")

    def refresh_data(self):
        """刷新数据"""
        if self.current_symbol:
            self.update_prediction_data()

    def update_prediction_data(self):
        """更新预测数据"""
        if self.current_symbol not in self.app.processed_data:
            return

        try:
            self.app.update_status(f"正在更新 {self.current_symbol} 的预测数据...")
            self.app.update_progress(10)

            # 获取处理后的数据
            processed_data = self.app.processed_data[self.current_symbol]

            self.app.update_progress(30)

            # 准备数据
            X_train, X_test, y_train, y_test, scaler = self.app.data_processor.prepare_data_for_prediction(
                processed_data)

            if X_train is None:
                self.app.show_error("错误", "准备预测数据失败")
                return

            self.app.update_progress(50)

            # 如果有训练好的模型，进行预测
            if self.app.prediction_model.model is not None:
                # 评估模型
                evaluation_metrics, y_test_inv, y_pred_inv = self.app.prediction_model.evaluate(
                    X_test, y_test, scaler)

                if evaluation_metrics is not None:
                    # 保存结果
                    self.prediction_results[self.current_symbol] = {
                        'y_test': y_test_inv.tolist(),
                        'y_pred': y_pred_inv.tolist(),
                        'evaluation_metrics': evaluation_metrics
                    }

                    self.model_evaluation[self.current_symbol] = evaluation_metrics

                    # 更新UI
                    self.update_prediction_chart()
                    self.update_evaluation_table()

                # 获取最后一段序列用于预测
                last_sequence = X_test[-1:]

                # 预测未来
                prediction_days = self.days_var.get()
                future_predictions = self.app.prediction_model.predict_future(
                    last_sequence, prediction_days, scaler)

                if future_predictions is not None:
                    # 获取历史收盘价
                    historical_prices = processed_data['Close'].values.tolist()

                    # 保存结果
                    self.future_predictions[self.current_symbol] = {
                        'historical_prices': historical_prices,
                        'future_predictions': future_predictions.tolist(),
                        'prediction_days': prediction_days
                    }

                    # 更新UI
                    self.update_future_chart()

            self.app.update_progress(90)

            # 更新预测数据表格
            self.update_prediction_data_table()

            self.app.update_progress(100)
            self.app.update_status(f"{self.current_symbol} 预测数据已更新")

        except Exception as e:
            self.app.update_progress(0)
            self.app.update_status("预测数据更新失败")
            self.app.show_error("更新错误", f"更新预测数据时出错: {str(e)}")

    def update_prediction_chart(self):
        """更新预测结果图表"""
        if self.current_symbol not in self.prediction_results:
            return

        try:
            # 获取预测结果
            results = self.prediction_results[self.current_symbol]
            y_test = results['y_test']
            y_pred = results['y_pred']

            # 清空图表
            self.prediction_ax.clear()

            # 绘制实际值和预测值
            self.prediction_ax.plot(
                y_test, label='实际价格', color='blue', linewidth=2)
            self.prediction_ax.plot(
                y_pred, label='预测价格', color='red', linewidth=2, linestyle='--')

            # 设置标题和图例
            self.prediction_ax.set_title(f'{self.current_symbol} 股价预测结果')
            self.prediction_ax.legend(loc='upper left')

            # 设置坐标轴标签
            self.prediction_ax.set_xlabel('时间')
            self.prediction_ax.set_ylabel('价格')

            # 更新画布
            self.prediction_fig.tight_layout()
            self.prediction_canvas.draw()

        except Exception as e:
            self.app.show_error("图表错误", f"更新预测结果图表时出错: {str(e)}")

    def update_future_chart(self):
        """更新未来预测图表"""
        if self.current_symbol not in self.future_predictions:
            return

        try:
            # 获取未来预测结果
            predictions = self.future_predictions[self.current_symbol]
            historical_prices = predictions['historical_prices']
            future_predictions = predictions['future_predictions']

            # 清空图表
            self.future_ax.clear()

            # 绘制历史数据
            self.future_ax.plot(historical_prices,
                                label='历史价格', color='blue', linewidth=2)

            # 绘制未来预测
            future_x = range(len(historical_prices), len(
                historical_prices) + len(future_predictions))
            self.future_ax.plot(future_x, future_predictions,
                                label='未来预测', color='red', linewidth=2, linestyle='--')

            # 添加预测区域
            self.future_ax.axvspan(len(historical_prices), len(historical_prices) + len(future_predictions),
                                   alpha=0.1, color='red')

            # 设置标题和图例
            self.future_ax.set_title(f'{self.current_symbol} 未来股价预测')
            self.future_ax.legend(loc='upper left')

            # 设置坐标轴标签
            self.future_ax.set_xlabel('时间')
            self.future_ax.set_ylabel('价格')

            # 更新画布
            self.future_fig.tight_layout()
            self.future_canvas.draw()

        except Exception as e:
            self.app.show_error("图表错误", f"更新未来预测图表时出错: {str(e)}")

    def update_evaluation_table(self):
        """更新模型评估表格"""
        if self.current_symbol not in self.model_evaluation:
            return

        # 清空表格
        for item in self.evaluation_table.get_children():
            self.evaluation_table.delete(item)

        # 获取评估指标
        metrics = self.model_evaluation[self.current_symbol]

        # 添加数据到表格
        metric_items = [
            ('均方误差 (MSE)', f"{metrics.get('mse', 0):.4f}"),
            ('均方根误差 (RMSE)', f"{metrics.get('rmse', 0):.4f}"),
            ('平均绝对误差 (MAE)', f"{metrics.get('mae', 0):.4f}"),
            ('决定系数 (R²)', f"{metrics.get('r2', 0):.4f}"),
            ('平均绝对百分比误差 (MAPE)', f"{metrics.get('mape', 0):.2f}%")
        ]

        for item in metric_items:
            self.evaluation_table.insert('', 'end', values=item)

    def update_prediction_data_table(self):
        """更新预测数据表格"""
        # 清空表格
        for item in self.prediction_table.get_children():
            self.prediction_table.delete(item)

        # 如果有预测结果，添加到表格
        if self.current_symbol in self.prediction_results:
            results = self.prediction_results[self.current_symbol]
            y_test = results['y_test']
            y_pred = results['y_pred']

            # 添加最近10条数据
            for i in range(min(10, len(y_test))):
                actual = y_test[-(i+1)]
                predicted = y_pred[-(i+1)]
                error = actual - predicted
                error_rate = error / actual * 100 if actual != 0 else 0

                # 生成日期（模拟）
                date = (datetime.now() - timedelta(days=i)
                        ).strftime('%Y-%m-%d')

                self.prediction_table.insert('', 'end', values=(
                    date,
                    f"{actual:.2f}",
                    f"{predicted:.2f}",
                    f"{error:.2f}",
                    f"{error_rate:.2f}%"
                ))

        # 如果有未来预测，添加到表格
        if self.current_symbol in self.future_predictions:
            predictions = self.future_predictions[self.current_symbol]
            future_predictions = predictions['future_predictions']
            historical_prices = predictions['historical_prices']

            # 添加未来预测数据
            last_price = historical_prices[-1] if historical_prices else 0
            for i, price in enumerate(future_predictions[:10]):
                # 生成日期（模拟）
                date = (datetime.now() + timedelta(days=i+1)
                        ).strftime('%Y-%m-%d')

                # 计算变化
                change = price - last_price
                change_rate = change / last_price * 100 if last_price != 0 else 0

                self.prediction_table.insert('', 'end', values=(
                    date,
                    "-",
                    f"{price:.2f}",
                    f"{change:.2f}",
                    f"{change_rate:.2f}%"
                ))

    def add_to_history(self, symbol, prediction_days, evaluation_metrics):
        """添加到历史记录"""
        # 计算准确率（基于R²）
        accuracy = evaluation_metrics.get('r2', 0) * 100

        # 计算平均误差（基于MAPE）
        avg_error = evaluation_metrics.get('mape', 0)

        # 添加到表格
        self.history_table.insert('', 'end', values=(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            symbol,
            prediction_days if prediction_days > 0 else "-",
            f"{accuracy:.2f}%",
            f"{avg_error:.2f}%"
        ))

        # 保留最近20条记录
        children = self.history_table.get_children()
        if len(children) > 20:
            self.history_table.delete(children[0])
