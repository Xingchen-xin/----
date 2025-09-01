import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
import json


class PredictionModel:
    def __init__(self, config):
        """初始化预测模型"""
        self.config = config
        self.model = None
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), 'data', 'prediction_model.h5')
        self.scaler = None
        self.prediction_days = config.get(
            'model_parameters', {}).get('prediction_days', 30)
        self.lstm_units = config.get(
            'model_parameters', {}).get('lstm_units', 50)
        self.dropout_rate = config.get(
            'model_parameters', {}).get('dropout_rate', 0.2)
        self.epochs = config.get('model_parameters', {}).get('epochs', 50)
        self.batch_size = config.get(
            'model_parameters', {}).get('batch_size', 32)

        # 设置日志
        self.logger = logging.getLogger(__name__)

        # 确保模型目录存在
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

    def build_model(self, input_shape):
        """构建LSTM模型"""
        try:
            model = Sequential()

            # 第一层LSTM
            model.add(LSTM(
                units=self.lstm_units,
                return_sequences=True,
                input_shape=input_shape
            ))
            model.add(Dropout(self.dropout_rate))

            # 第二层LSTM
            model.add(LSTM(
                units=self.lstm_units,
                return_sequences=True
            ))
            model.add(Dropout(self.dropout_rate))

            # 第三层LSTM
            model.add(LSTM(
                units=self.lstm_units,
                return_sequences=False
            ))
            model.add(Dropout(self.dropout_rate))

            # 输出层
            model.add(Dense(units=1))

            # 编译模型
            model.compile(
                optimizer='adam',
                loss='mean_squared_error',
                metrics=['mae']
            )

            self.model = model
            self.logger.info("成功构建LSTM模型")
            return model
        except Exception as e:
            self.logger.error(f"构建模型时出错: {str(e)}")
            return None

    def train(self, X_train, y_train, X_test=None, y_test=None):
        """训练模型"""
        if self.model is None:
            input_shape = (X_train.shape[1], X_train.shape[2])
            self.build_model(input_shape)

        try:
            # 设置回调函数
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                ModelCheckpoint(
                    filepath=self.model_path,
                    monitor='val_loss',
                    save_best_only=True
                )
            ]

            # 训练模型
            validation_data = None
            if X_test is not None and y_test is not None:
                validation_data = (X_test, y_test)

            history = self.model.fit(
                X_train,
                y_train,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_data=validation_data,
                callbacks=callbacks,
                verbose=1
            )

            self.logger.info("模型训练完成")
            return history
        except Exception as e:
            self.logger.error(f"训练模型时出错: {str(e)}")
            return None

    def load_model(self):
        """加载已保存的模型"""
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                self.logger.info("成功加载已保存的模型")
                return True
            else:
                self.logger.warning("未找到已保存的模型")
                return False
        except Exception as e:
            self.logger.error(f"加载模型时出错: {str(e)}")
            return False

    def predict(self, X):
        """使用模型进行预测"""
        if self.model is None:
            if not self.load_model():
                self.logger.error("模型未加载，无法进行预测")
                return None

        try:
            predictions = self.model.predict(X)
            return predictions
        except Exception as e:
            self.logger.error(f"预测时出错: {str(e)}")
            return None

    def evaluate(self, X_test, y_test, scaler=None):
        """评估模型性能"""
        if self.model is None:
            if not self.load_model():
                self.logger.error("模型未加载，无法评估")
                return None

        try:
            # 进行预测
            y_pred = self.model.predict(X_test)

            # 如果提供了scaler，则反标准化预测值和实际值
            if scaler is not None:
                # 创建一个与原始特征相同形状的零矩阵
                y_test_reshaped = np.zeros(
                    (len(y_test), scaler.n_features_in_))
                y_pred_reshaped = np.zeros(
                    (len(y_pred), scaler.n_features_in_))

                # 将收盘价（第3列）放在正确的位置
                y_test_reshaped[:, 3] = y_test.flatten()
                y_pred_reshaped[:, 3] = y_pred.flatten()

                # 反标准化
                y_test_inv = scaler.inverse_transform(y_test_reshaped)[:, 3]
                y_pred_inv = scaler.inverse_transform(y_pred_reshaped)[:, 3]
            else:
                y_test_inv = y_test.flatten()
                y_pred_inv = y_pred.flatten()

            # 计算评估指标
            mse = mean_squared_error(y_test_inv, y_pred_inv)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test_inv, y_pred_inv)
            r2 = r2_score(y_test_inv, y_pred_inv)

            # 计算平均绝对百分比误差 (MAPE)
            mape = np.mean(
                np.abs((y_test_inv - y_pred_inv) / y_test_inv)) * 100

            evaluation_metrics = {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'mape': mape
            }

            self.logger.info(
                f"模型评估结果: MSE={mse:.4f}, RMSE={rmse:.4f}, MAE={mae:.4f}, R2={r2:.4f}, MAPE={mape:.4f}%")

            return evaluation_metrics, y_test_inv, y_pred_inv
        except Exception as e:
            self.logger.error(f"评估模型时出错: {str(e)}")
            return None

    def predict_future(self, last_sequence, days=30, scaler=None):
        """预测未来几天的股价"""
        if self.model is None:
            if not self.load_model():
                self.logger.error("模型未加载，无法进行预测")
                return None

        try:
            # 确保输入数据的形状正确
            if len(last_sequence.shape) == 2:
                last_sequence = np.reshape(
                    last_sequence, (last_sequence.shape[0], last_sequence.shape[1], 1))

            # 创建一个数组来存储预测结果
            predictions = []

            # 使用最后已知的序列作为起点
            current_sequence = last_sequence.copy()

            # 逐日预测
            for _ in range(days):
                # 预测下一天的收盘价
                next_day_pred = self.model.predict(current_sequence)[0, 0]
                predictions.append(next_day_pred)

                # 更新序列，将预测值添加到序列中，并移除最早的值
                new_sequence = np.copy(current_sequence)
                new_sequence[0, :-1, 0] = current_sequence[0, 1:, 0]
                new_sequence[0, -1, 0] = next_day_pred
                current_sequence = new_sequence

            # 如果提供了scaler，则反标准化预测值
            if scaler is not None:
                # 创建一个与原始特征相同形状的零矩阵
                predictions_reshaped = np.zeros(
                    (len(predictions), scaler.n_features_in_))

                # 将预测的收盘价（第3列）放在正确的位置
                predictions_reshaped[:, 3] = predictions

                # 反标准化
                predictions_inv = scaler.inverse_transform(
                    predictions_reshaped)[:, 3]
            else:
                predictions_inv = np.array(predictions)

            return predictions_inv
        except Exception as e:
            self.logger.error(f"预测未来股价时出错: {str(e)}")
            return None

    def save_model(self, path=None):
        """保存模型"""
        if self.model is None:
            self.logger.error("没有模型可保存")
            return False

        try:
            save_path = path if path else self.model_path
            self.model.save(save_path)
            self.logger.info(f"模型已保存到 {save_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存模型时出错: {str(e)}")
            return False

    def get_model_summary(self):
        """获取模型摘要"""
        if self.model is None:
            if not self.load_model():
                self.logger.error("模型未加载")
                return None

        try:
            # 获取模型摘要
            summary = []
            self.model.summary(print_fn=lambda x: summary.append(x))

            # 获取模型配置
            config = self.model.get_config()

            # 获取模型权重信息
            weights_info = []
            for i, layer in enumerate(self.model.layers):
                weights = layer.get_weights()
                weights_info.append({
                    'layer': i,
                    'name': layer.name,
                    'weights_count': len(weights),
                    'weights_shape': [w.shape for w in weights]
                })

            return {
                'summary': '\n'.join(summary),
                'config': config,
                'weights_info': weights_info
            }
        except Exception as e:
            self.logger.error(f"获取模型摘要时出错: {str(e)}")
            return None
