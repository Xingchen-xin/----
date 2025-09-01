import pandas as pd
import numpy as np
import logging
from textblob import TextBlob
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ta


class DataProcessor:
    def __init__(self, config):
        """初始化数据处理器"""
        self.config = config

        # 设置日志
        self.logger = logging.getLogger(__name__)

        # 初始化NLTK的VADER情感分析器
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
        self.sia = SentimentIntensityAnalyzer()

    def process_stock_data(self, data):
        """处理股票数据，添加技术指标"""
        if data.empty:
            return data

        try:
            # 确保数据按日期排序
            data = data.sort_index()

            # 添加技术指标
            # 移动平均线
            data['MA5'] = ta.trend.sma_indicator(data['Close'], window=5)
            data['MA10'] = ta.trend.sma_indicator(data['Close'], window=10)
            data['MA20'] = ta.trend.sma_indicator(data['Close'], window=20)
            data['MA50'] = ta.trend.sma_indicator(data['Close'], window=50)

            # 指数移动平均线
            data['EMA12'] = ta.trend.ema_indicator(data['Close'], window=12)
            data['EMA26'] = ta.trend.ema_indicator(data['Close'], window=26)

            # MACD
            macd = ta.trend.MACD(data['Close'])
            data['MACD'] = macd.macd()
            data['MACD_signal'] = macd.macd_signal()
            data['MACD_hist'] = macd.macd_diff()

            # RSI
            data['RSI'] = ta.momentum.rsi(data['Close'], window=14)

            # 布林带
            bollinger = ta.volatility.BollingerBands(data['Close'])
            data['BB_upper'] = bollinger.bollinger_hband()
            data['BB_middle'] = bollinger.bollinger_mavg()
            data['BB_lower'] = bollinger.bollinger_lband()

            # 随机指标
            stoch = ta.momentum.StochasticOscillator(
                data['High'], data['Low'], data['Close'])
            data['STOCH_K'] = stoch.stoch()
            data['STOCH_D'] = stoch.stoch_signal()

            # 威廉指标
            data['WILLIAMS_R'] = ta.momentum.williams_r(
                data['High'], data['Low'], data['Close'])

            # 商品通道指数
            data['CCI'] = ta.trend.cci(
                data['High'], data['Low'], data['Close'])

            # 平均方向指数
            adx = ta.trend.ADXIndicator(
                data['High'], data['Low'], data['Close'])
            data['ADX'] = adx.adx()

            # 动量指标
            data['Momentum'] = ta.momentum.roc(data['Close'], window=10)

            # 波动率
            data['Volatility'] = ta.volatility.average_true_range(
                data['High'], data['Low'], data['Close'])

            # 计算日收益率
            data['Daily_Return'] = data['Close'].pct_change()

            # 计算波动率（标准差）
            data['Volatility_Std'] = data['Daily_Return'].rolling(
                window=20).std()

            # 填充NaN值
            data = data.fillna(method='bfill').fillna(method='ffill')

            return data
        except Exception as e:
            self.logger.error(f"处理股票数据时出错: {str(e)}")
            return data

    def process_news_data(self, news_data):
        """处理新闻数据，添加情感分析"""
        if not news_data:
            return []

        try:
            processed_news = []
            for article in news_data:
                # 提取标题和描述
                title = article.get('title', '')
                description = article.get('description', '')
                content = f"{title} {description}"

                # 使用TextBlob进行情感分析
                blob = TextBlob(content)
                polarity = blob.sentiment.polarity  # 极性：-1到1，负值表示负面，正值表示正面
                subjectivity = blob.sentiment.subjectivity  # 主观性：0到1，0表示非常客观，1表示非常主观

                # 使用VADER进行情感分析
                vader_scores = self.sia.polarity_scores(content)
                vader_compound = vader_scores['compound']  # 综合得分：-1到1

                # 确定情感类别
                if vader_compound >= 0.05:
                    sentiment = 'positive'
                elif vader_compound <= -0.05:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'

                # 添加情感分析结果
                processed_article = article.copy()
                processed_article['textblob_polarity'] = polarity
                processed_article['textblob_subjectivity'] = subjectivity
                processed_article['vader_compound'] = vader_compound
                processed_article['vader_positive'] = vader_scores['pos']
                processed_article['vader_negative'] = vader_scores['neg']
                processed_article['vader_neutral'] = vader_scores['neu']
                processed_article['sentiment'] = sentiment

                processed_news.append(processed_article)

            return processed_news
        except Exception as e:
            self.logger.error(f"处理新闻数据时出错: {str(e)}")
            return news_data

    def merge_stock_news_data(self, stock_data, news_data):
        """合并股票和新闻数据"""
        if stock_data.empty or not news_data:
            return stock_data

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
                self.logger.warning("新闻数据中没有发布日期，无法与股票数据合并")
                return stock_data

            # 按日期分组新闻，计算每日情感得分
            daily_sentiment = news_df.groupby('date').agg({
                'vader_compound': 'mean',
                'vader_positive': 'mean',
                'vader_negative': 'mean',
                'vader_neutral': 'mean',
                'textblob_polarity': 'mean',
                'textblob_subjectivity': 'mean'
            }).reset_index()

            # 转换日期格式以匹配股票数据
            daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])

            # 将情感数据添加到股票数据
            merged_data = stock_data.copy()

            # 为股票数据添加日期列（用于合并）
            merged_data['date'] = merged_data.index.date

            # 合并数据
            merged_data = pd.merge(
                merged_data,
                daily_sentiment,
                on='date',
                how='left'
            )

            # 填充NaN值
            sentiment_cols = ['vader_compound', 'vader_positive', 'vader_negative',
                              'vader_neutral', 'textblob_polarity', 'textblob_subjectivity']
            merged_data[sentiment_cols] = merged_data[sentiment_cols].fillna(
                method='ffill').fillna(0)

            # 删除临时日期列
            merged_data = merged_data.drop(columns=['date'])

            return merged_data
        except Exception as e:
            self.logger.error(f"合并股票和新闻数据时出错: {str(e)}")
            return stock_data

    def prepare_data_for_prediction(self, data, prediction_days=None):
        """准备用于预测的数据"""
        if data.empty:
            return None, None, None, None

        if prediction_days is None:
            prediction_days = self.config.get(
                'model_parameters', {}).get('prediction_days', 30)

        try:
            # 选择特征列
            feature_cols = [
                'Open', 'High', 'Low', 'Close', 'Volume',
                'MA5', 'MA10', 'MA20', 'MA50',
                'EMA12', 'EMA26',
                'MACD', 'MACD_signal', 'MACD_hist',
                'RSI',
                'BB_upper', 'BB_middle', 'BB_lower',
                'STOCH_K', 'STOCH_D',
                'WILLIAMS_R', 'CCI', 'ADX', 'Momentum',
                'Volatility', 'Volatility_Std',
                'vader_compound', 'vader_positive', 'vader_negative',
                'vader_neutral', 'textblob_polarity', 'textblob_subjectivity'
            ]

            # 确保所有特征列都存在
            available_cols = [
                col for col in feature_cols if col in data.columns]
            if not available_cols:
                self.logger.error("没有可用的特征列")
                return None, None, None, None

            # 提取特征数据
            features = data[available_cols].values

            # 标准化数据
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_features = scaler.fit_transform(features)

            # 创建时间序列数据
            X, y = [], []
            for i in range(prediction_days, len(scaled_features)):
                X.append(scaled_features[i-prediction_days:i, 0])
                y.append(scaled_features[i, 3])  # 预测收盘价

            X, y = np.array(X), np.array(y)

            # 重塑X以适应LSTM模型 [samples, time steps, features]
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))

            # 分割训练集和测试集
            train_test_split_ratio = self.config.get(
                'model_parameters', {}).get('train_test_split', 0.8)
            split_index = int(len(X) * train_test_split_ratio)

            X_train, X_test = X[:split_index], X[split_index:]
            y_train, y_test = y[:split_index], y[split_index:]

            return X_train, X_test, y_train, y_test, scaler
        except Exception as e:
            self.logger.error(f"准备预测数据时出错: {str(e)}")
            return None, None, None, None

    def process_fundamental_data(self, fundamental_data):
        """处理基本面数据"""
        if not fundamental_data:
            return {}

        try:
            # 创建处理后的基本面数据字典
            processed_data = {
                'symbol': fundamental_data.get('symbol', ''),
                'name': fundamental_data.get('longName', fundamental_data.get('shortName', '')),
                'sector': fundamental_data.get('sector', ''),
                'industry': fundamental_data.get('industry', ''),
                'market_cap': fundamental_data.get('marketCap', 0),
                'enterprise_value': fundamental_data.get('enterpriseValue', 0),
                'trailing_pe': fundamental_data.get('trailingPE', 0),
                'forward_pe': fundamental_data.get('forwardPE', 0),
                'peg_ratio': fundamental_data.get('pegRatio', 0),
                'price_to_sales': fundamental_data.get('priceToSalesTrailing12Months', 0),
                'price_to_book': fundamental_data.get('priceToBook', 0),
                'enterprise_to_revenue': fundamental_data.get('enterpriseToRevenue', 0),
                'enterprise_to_ebitda': fundamental_data.get('enterpriseToEbitda', 0),
                'dividend_rate': fundamental_data.get('dividendRate', 0),
                'dividend_yield': fundamental_data.get('dividendYield', 0),
                'beta': fundamental_data.get('beta', 0),
                'profit_margins': fundamental_data.get('profitMargins', 0),
                'operating_margins': fundamental_data.get('operatingMargins', 0),
                'gross_margins': fundamental_data.get('grossMargins', 0),
                'revenue_growth': fundamental_data.get('revenueQuarterlyGrowth', 0),
                'earnings_growth': fundamental_data.get('earningsQuarterlyGrowth', 0),
                '52_week_change': fundamental_data.get('52WeekChange', 0),
                'last_dividend_date': fundamental_data.get('lastDividendDate', ''),
                'ex_dividend_date': fundamental_data.get('exDividendDate', ''),
                'payout_ratio': fundamental_data.get('payoutRatio', 0)
            }

            return processed_data
        except Exception as e:
            self.logger.error(f"处理基本面数据时出错: {str(e)}")
            return {}

    def calculate_technical_signals(self, data):
        """计算技术信号"""
        if data.empty:
            return {}

        try:
            signals = {}

            # RSI信号
            if 'RSI' in data.columns:
                rsi = data['RSI'].iloc[-1]
                if rsi > 70:
                    signals['RSI'] = '超买'
                elif rsi < 30:
                    signals['RSI'] = '超卖'
                else:
                    signals['RSI'] = '中性'

            # MACD信号
            if all(col in data.columns for col in ['MACD', 'MACD_signal']):
                macd = data['MACD'].iloc[-1]
                macd_signal = data['MACD_signal'].iloc[-1]
                macd_hist = data['MACD_hist'].iloc[-1]

                if macd > macd_signal and macd_hist > 0:
                    signals['MACD'] = '买入信号'
                elif macd < macd_signal and macd_hist < 0:
                    signals['MACD'] = '卖出信号'
                else:
                    signals['MACD'] = '中性'

            # 布林带信号
            if all(col in data.columns for col in ['BB_upper', 'BB_middle', 'BB_lower', 'Close']):
                close = data['Close'].iloc[-1]
                bb_upper = data['BB_upper'].iloc[-1]
                bb_lower = data['BB_lower'].iloc[-1]

                if close > bb_upper:
                    signals['BB'] = '突破上轨'
                elif close < bb_lower:
                    signals['BB'] = '突破下轨'
                else:
                    signals['BB'] = '轨道内'

            # 移动平均线信号
            if all(col in data.columns for col in ['MA5', 'MA10', 'MA20', 'Close']):
                ma5 = data['MA5'].iloc[-1]
                ma10 = data['MA10'].iloc[-1]
                ma20 = data['MA20'].iloc[-1]
                close = data['Close'].iloc[-1]

                if close > ma5 > ma10 > ma20:
                    signals['MA'] = '多头排列'
                elif close < ma5 < ma10 < ma20:
                    signals['MA'] = '空头排列'
                else:
                    signals['MA'] = '交叉中'

            # KDJ信号
            if all(col in data.columns for col in ['STOCH_K', 'STOCH_D']):
                k = data['STOCH_K'].iloc[-1]
                d = data['STOCH_D'].iloc[-1]

                if k > 80 and d > 80:
                    signals['KDJ'] = '超买区'
                elif k < 20 and d < 20:
                    signals['KDJ'] = '超卖区'
                elif k > d:
                    signals['KDJ'] = '金叉'
                else:
                    signals['KDJ'] = '死叉'

            return signals
        except Exception as e:
            self.logger.error(f"计算技术信号时出错: {str(e)}")
            return {}
