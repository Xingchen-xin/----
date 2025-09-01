import os
import json
import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import logging
from tqdm import tqdm


class DataFetcher:
    def __init__(self, config):
        """初始化数据获取器"""
        self.config = config
        self.api_keys = config.get('api_keys', {})
        self.stock_symbols = config.get('stock_symbols', [])
        self.news_sources = config.get('news_sources', [])
        self.use_mock_data = config.get(
            'data_settings', {}).get('use_mock_data', True)
        self.historical_data_years = config.get(
            'data_settings', {}).get('historical_data_years', 5)

        # 设置日志
        self.logger = logging.getLogger(__name__)

    def fetch_stock_data(self, symbol, period=None):
        """获取股票数据"""
        if period is None:
            end_date = datetime.datetime.now()
            start_date = end_date - \
                datetime.timedelta(days=self.historical_data_years * 365)
            period = f"{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}"

        try:
            if self.use_mock_data:
                # 使用模拟数据
                self.logger.info(f"使用模拟数据获取股票 {symbol} 的数据")
                return self._generate_mock_stock_data(symbol, period)
            else:
                # 使用真实API
                self.logger.info(f"从Yahoo Finance获取股票 {symbol} 的数据")
                stock = yf.Ticker(symbol)
                data = stock.history(period=period)
                return data
        except Exception as e:
            self.logger.error(f"获取股票 {symbol} 数据时出错: {str(e)}")
            return self._generate_mock_stock_data(symbol, period)

    def _generate_mock_stock_data(self, symbol, period):
        """生成模拟股票数据"""
        self.logger.info(f"为股票 {symbol} 生成模拟数据")

        # 解析period参数
        if '_' in period:
            start_date, end_date = period.split('_')
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        else:
            # 处理预定义的period值
            end_date = datetime.datetime.now()
            if period == '1mo':
                start_date = end_date - datetime.timedelta(days=30)
            elif period == '3mo':
                start_date = end_date - datetime.timedelta(days=90)
            elif period == '6mo':
                start_date = end_date - datetime.timedelta(days=180)
            elif period == '1y':
                start_date = end_date - datetime.timedelta(days=365)
            elif period == '2y':
                start_date = end_date - datetime.timedelta(days=730)
            elif period == '5y':
                start_date = end_date - datetime.timedelta(days=1825)
            elif period == '10y':
                start_date = end_date - datetime.timedelta(days=3650)
            elif period == 'ytd':
                start_date = datetime.datetime(end_date.year, 1, 1)
            elif period == 'max':
                start_date = datetime.datetime(2015, 1, 1)
            else:
                start_date = end_date - datetime.timedelta(days=365)

        # 生成日期范围
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 工作日

        # 生成基础价格序列（随机游走）
        np.random.seed(hash(symbol) % 10000)  # 使用符号作为种子，确保同一符号的数据一致
        base_price = 100 + np.random.randn() * 50
        returns = np.random.normal(0.001, 0.02, size=len(dates))
        price_series = base_price * np.exp(np.cumsum(returns))

        # 生成OHLCV数据
        data = pd.DataFrame(index=dates)
        data['Close'] = price_series

        # 生成开盘价（通常接近前一天的收盘价）
        data['Open'] = data['Close'].shift(
            1) * (1 + np.random.normal(0, 0.005, size=len(dates)))
        data['Open'].iloc[0] = data['Close'].iloc[0] * \
            (1 + np.random.normal(0, 0.005))

        # 生成最高价和最低价
        high_factor = 1 + np.abs(np.random.normal(0, 0.01, size=len(dates)))
        low_factor = 1 - np.abs(np.random.normal(0, 0.01, size=len(dates)))
        data['High'] = data[['Open', 'Close']].max(axis=1) * high_factor
        data['Low'] = data[['Open', 'Close']].min(axis=1) * low_factor

        # 确保最高价不低于开盘价和收盘价，最低价不高于开盘价和收盘价
        data['High'] = data[['High', 'Open', 'Close']].max(axis=1)
        data['Low'] = data[['Low', 'Open', 'Close']].min(axis=1)

        # 生成成交量
        data['Volume'] = np.random.lognormal(
            15, 1, size=len(dates)).astype(int)

        # 添加股息和股票分割（通常为0）
        data['Dividends'] = 0
        data['Stock Splits'] = 0

        return data

    def fetch_news_data(self, query='artificial intelligence', max_articles=None):
        """获取新闻数据"""
        if max_articles is None:
            max_articles = self.config.get(
                'data_settings', {}).get('max_news_articles', 100)

        try:
            if self.use_mock_data:
                # 使用模拟数据
                self.logger.info(f"使用模拟数据获取关于 '{query}' 的新闻")
                return self._generate_mock_news_data(query, max_articles)
            else:
                # 使用真实API
                self.logger.info(f"从NewsAPI获取关于 '{query}' 的新闻")
                news_api_key = self.api_keys.get('news_api')
                if not news_api_key:
                    self.logger.warning("未找到News API密钥，使用模拟数据")
                    return self._generate_mock_news_data(query, max_articles)

                url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={news_api_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    news_data = response.json()
                    articles = news_data.get('articles', [])[:max_articles]
                    return articles
                else:
                    self.logger.error(f"获取新闻数据失败，状态码: {response.status_code}")
                    return self._generate_mock_news_data(query, max_articles)
        except Exception as e:
            self.logger.error(f"获取新闻数据时出错: {str(e)}")
            return self._generate_mock_news_data(query, max_articles)

    def _generate_mock_news_data(self, query, max_articles):
        """生成模拟新闻数据"""
        self.logger.info(f"为查询 '{query}' 生成模拟新闻数据")

        # 模拟新闻标题模板
        positive_templates = [
            f"{query}技术取得重大突破",
            f"专家看好{query}未来发展",
            f"{query}行业获得大量投资",
            f"{query}应用范围不断扩大",
            f"{query}技术助力经济增长",
            f"{query}企业发布创新产品",
            f"{query}研究取得新进展",
            f"{query}市场前景广阔"
        ]

        negative_templates = [
            f"{query}技术面临挑战",
            f"专家担忧{query}发展风险",
            f"{query}行业投资降温",
            f"{query}应用引发争议",
            f"{query}技术可能带来失业问题",
            f"{query}企业遭遇困境",
            f"{query}研究遇到瓶颈",
            f"{query}市场前景不明朗"
        ]

        neutral_templates = [
            f"{query}技术发展现状分析",
            f"专家讨论{query}未来趋势",
            f"{query}行业投资情况报告",
            f"{query}应用场景探讨",
            f"{query}技术对社会的影响",
            f"{query}企业最新动态",
            f"{query}研究进展综述",
            f"{query}市场分析报告"
        ]

        # 模拟新闻来源
        sources = self.news_sources if self.news_sources else [
            "TechCrunch", "Reuters", "Bloomberg", "WSJ", "CNBC",
            "Forbes", "The Verge", "Wired", "TechRadar", "CNET"
        ]

        # 生成模拟新闻文章
        articles = []
        for i in range(max_articles):
            # 随机选择情感倾向
            sentiment = np.random.choice(
                ['positive', 'negative', 'neutral'], p=[0.4, 0.2, 0.4])

            # 根据情感倾向选择标题模板
            if sentiment == 'positive':
                title_template = np.random.choice(positive_templates)
            elif sentiment == 'negative':
                title_template = np.random.choice(negative_templates)
            else:
                title_template = np.random.choice(neutral_templates)

            # 生成标题
            title = title_template

            # 生成描述
            description = f"这是一篇关于{query}的新闻文章。文章讨论了{query}的最新发展和未来前景。"

            # 生成发布日期（最近30天内随机）
            publish_date = datetime.datetime.now(
            ) - datetime.timedelta(days=np.random.randint(0, 30))

            # 随机选择来源
            source = np.random.choice(sources)

            # 生成URL
            url = f"https://example.com/{source.lower().replace(' ', '')}/{query.replace(' ', '-')}-{i}"

            # 生成文章
            article = {
                'title': title,
                'description': description,
                'publishedAt': publish_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'source': {'name': source},
                'url': url,
                'sentiment': sentiment
            }

            articles.append(article)

        # 按发布日期排序
        articles.sort(key=lambda x: x['publishedAt'], reverse=True)

        return articles

    def fetch_multiple_stocks(self, symbols=None, period=None):
        """获取多只股票的数据"""
        if symbols is None:
            symbols = self.stock_symbols

        stock_data = {}

        for symbol in tqdm(symbols, desc="获取股票数据"):
            data = self.fetch_stock_data(symbol, period)
            if not data.empty:
                stock_data[symbol] = data

        return stock_data

    def fetch_stock_fundamentals(self, symbol):
        """获取股票基本面数据"""
        try:
            if self.use_mock_data:
                # 使用模拟数据
                self.logger.info(f"使用模拟数据获取股票 {symbol} 的基本面数据")
                return self._generate_mock_fundamentals(symbol)
            else:
                # 使用真实API
                self.logger.info(f"从Yahoo Finance获取股票 {symbol} 的基本面数据")
                stock = yf.Ticker(symbol)
                info = stock.info
                return info
        except Exception as e:
            self.logger.error(f"获取股票 {symbol} 基本面数据时出错: {str(e)}")
            return self._generate_mock_fundamentals(symbol)

    def _generate_mock_fundamentals(self, symbol):
        """生成模拟基本面数据"""
        self.logger.info(f"为股票 {symbol} 生成模拟基本面数据")

        # 基本面数据模板
        fundamentals = {
            'symbol': symbol,
            'shortName': f"{symbol} Corporation",
            'longName': f"{symbol} Inc.",
            'sector': "Technology",
            'industry': "Computer Hardware",
            # 10亿到2万亿美元
            'marketCap': np.random.randint(1000000000, 2000000000000),
            'enterpriseValue': np.random.randint(1000000000, 2000000000000),
            'trailingPE': np.random.uniform(10, 50),
            'forwardPE': np.random.uniform(10, 50),
            'pegRatio': np.random.uniform(0.5, 3),
            'priceToSalesTrailing12Months': np.random.uniform(1, 10),
            'priceToBook': np.random.uniform(1, 10),
            'enterpriseToRevenue': np.random.uniform(1, 10),
            'enterpriseToEbitda': np.random.uniform(5, 20),
            'forwardEps': np.random.uniform(1, 20),
            'trailingEps': np.random.uniform(1, 20),
            'dividendRate': np.random.uniform(0, 5),
            'dividendYield': np.random.uniform(0, 0.05),
            'payoutRatio': np.random.uniform(0, 0.5),
            'beta': np.random.uniform(0.5, 2),
            'priceToSalesTrailing12Months': np.random.uniform(1, 10),
            'priceToBook': np.random.uniform(1, 10),
            'enterpriseToRevenue': np.random.uniform(1, 10),
            'enterpriseToEbitda': np.random.uniform(5, 20),
            '52WeekChange': np.random.uniform(-0.5, 0.5),
            'SandP52WeekChange': np.random.uniform(-0.2, 0.2),
            'lastDividendValue': np.random.uniform(0, 1),
            'lastDividendDate': (datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 90))).strftime('%Y-%m-%d'),
            'exDividendDate': (datetime.datetime.now() + datetime.timedelta(days=np.random.randint(0, 90))).strftime('%Y-%m-%d'),
            'payoutRatio': np.random.uniform(0, 0.5),
            'fiveYearAvgDividendYield': np.random.uniform(0, 0.05),
            'beta': np.random.uniform(0.5, 2),
            'trailingAnnualDividendRate': np.random.uniform(0, 5),
            'trailingAnnualDividendYield': np.random.uniform(0, 0.05),
            'lastSplitDate': None,
            'lastSplitFactor': None,
            'lastFiscalYearEnd': (datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d'),
            'nextFiscalYearEnd': (datetime.datetime.now() + datetime.timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d'),
            'mostRecentQuarter': (datetime.datetime.now() - datetime.timedelta(days=np.random.randint(0, 90))).strftime('%Y-%m-%d'),
            'earningsQuarterlyGrowth': np.random.uniform(-0.5, 0.5),
            'revenueQuarterlyGrowth': np.random.uniform(-0.5, 0.5),
            'grossMargins': np.random.uniform(0.2, 0.8),
            'operatingMargins': np.random.uniform(0.1, 0.4),
            'profitMargins': np.random.uniform(0.05, 0.3),
            'financialCurrency': "USD",
            'trailingPegRatio': np.random.uniform(0.5, 3)
        }

        return fundamentals
