import json
import os
import logging


class ConfigManager:
    def __init__(self, config_file=None):
        """初始化配置管理器"""
        if config_file is None:
            # 默认配置文件路径
            current_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(current_dir, 'data', 'config.json')

        self.config_file = config_file
        self.config = self.load_config()

        # 设置日志
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """加载配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            # 如果配置文件不存在，创建默认配置
            if not os.path.exists(self.config_file):
                default_config = self.get_default_config()
                self.save_config(default_config)
                return default_config

            # 读取配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            return config
        except Exception as e:
            logging.error(f"加载配置文件时出错: {str(e)}")
            return self.get_default_config()

    def save_config(self, config=None):
        """保存配置文件"""
        if config is None:
            config = self.config

        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            # 写入配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            self.config = config
            return True
        except Exception as e:
            logging.error(f"保存配置文件时出错: {str(e)}")
            return False

    def get_default_config(self):
        """获取默认配置"""
        return {
            "api_keys": {
                "news_api": "",
                "alpha_vantage": "",
                "quandl": ""
            },
            "stock_symbols": [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "META",
                "TSLA",
                "NVDA",
                "PYPL",
                "INTC",
                "CSCO"
            ],
            "news_sources": [
                "TechCrunch",
                "Reuters",
                "Bloomberg",
                "WSJ",
                "CNBC",
                "Forbes",
                "The Verge",
                "Wired",
                "TechRadar",
                "CNET"
            ],
            "news_query": "artificial intelligence",
            "data_settings": {
                "use_mock_data": True,
                "historical_data_years": 5,
                "max_news_articles": 100
            },
            "model_parameters": {
                "prediction_days": 30,
                "lstm_units": 50,
                "dropout_rate": 0.2,
                "epochs": 50,
                "batch_size": 32,
                "train_test_split": 0.8
            },
            "visualization": {
                "figure_size": [12, 8],
                "color_palette": "viridis",
                "save_plots": True,
                "plot_format": "png",
                "plot_dpi": 300
            },
            "ui_settings": {
                "theme": "arc",
                "host": "127.0.0.1",
                "port": 8050,
                "debug": False
            },
            "logging": {
                "level": "INFO",
                "file": "logs/ai_investment_advisor.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "refresh_interval": 300  # 5分钟
        }

    def get(self, key, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key, value):
        """设置配置项"""
        keys = key.split('.')
        config = self.config

        # 遍历到倒数第二层
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置最后一层的值
        config[keys[-1]] = value

        # 保存配置
        return self.save_config()

    def update(self, updates):
        """批量更新配置"""
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = update_dict(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        self.config = update_dict(self.config, updates)
        return self.save_config()

    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.get_default_config()
        return self.save_config()
