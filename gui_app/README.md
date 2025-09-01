---
AIGC:
  Label: '1'
  ContentProducer: '001191110108MA01KP2T5U00000'
  ProduceID: '321380f5-4589-48ac-935d-cb223a541fd0'
  ReservedCode1: '7f6e2242-dff5-45b8-9408-d0dac2fe5616'
  ContentPropagator: '001191110108MA01KP2T5U00000'
  PropagateID: '80327208-cd14-4011-87f6-9535bbd7be76'
  ReservedCode2: '874f0508-a195-4f46-9b75-c283c0bf943c'
---

# AI投资顾问 - GUI版本

## 项目简介

AI投资顾问是一个基于人工智能的股票分析和投资建议平台，使用Tkinter构建的现代化GUI界面。该应用使用深度学习模型预测股票价格，并结合新闻情感分析提供投资建议。

## 功能特点

- **现代化GUI界面**：使用Tkinter和ttkthemes构建美观的用户界面
- **股票分析**：提供K线图、技术指标和基本面数据分析
- **新闻资讯**：AI相关新闻列表和情感分析
- **预测结果**：基于LSTM模型的股价预测和可视化
- **设置管理**：灵活的配置管理和API密钥设置

## 系统要求

- Python 3.7+
- 操作系统：Windows、macOS或Linux
- 内存：至少4GB RAM
- 硬盘空间：至少1GB可用空间

## 安装说明

1. 克隆或下载项目代码
2. 进入项目目录
3. 安装依赖包：

bash
pip install -r requirements.txt


## 使用说明

### 启动应用

在项目根目录下运行：

bash
python app.py


### 主要功能

#### 1. 首页
- 市场状态概览
- AI公司股票概览
- 简要新闻摘要
- 系统运行状态

#### 2. 股票分析
- 股票搜索和选择
- K线图显示
- 技术指标分析
- 基本面数据查看

#### 3. 新闻资讯
- AI相关新闻列表
- 新闻详情查看
- 情感分析显示
- 新闻分类和筛选

#### 4. 预测结果
- 股价预测图表
- 预测数据表格
- 置信度显示
- 预测准确性历史

#### 5. 设置
- API密钥管理
- 股票列表配置
- 新闻来源设置
- 模型参数调整
- 界面主题设置

## 文件结构


gui_app/
├── app.py                 # 主程序
├── requirements.txt      # 依赖包列表
├── README.md            # 使用说明
├── views/               # 视图模块
│   ├── home_view.py     # 首页视图
│   ├── stock_view.py    # 股票分析视图
│   ├── news_view.py     # 新闻资讯视图
│   ├── prediction_view.py # 预测结果视图
│   └── settings_view.py # 设置视图
├── utils/               # 工具模块
│   ├── config_manager.py # 配置管理器
│   ├── data_fetcher.py  # 数据获取器
│   ├── data_processor.py # 数据处理器
│   ├── prediction_model.py # 预测模型
│   └── visualizer.py    # 可视化工具
└── data/                # 数据目录
    ├── config.json      # 配置文件
    ├── logs/           # 日志目录
    └── models/         # 模型文件目录


## 配置说明

应用首次运行时，会在`data`目录下创建默认配置文件`config.json`。您可以通过设置界面修改配置，或直接编辑配置文件。

主要配置项包括：
- API密钥设置
- 股票列表
- 新闻来源
- 模型参数
- 界面设置

## 常见问题

### 1. 无法获取股票数据
请检查网络连接，并确保在设置中正确配置了API密钥。

### 2. 预测结果不准确
预测结果仅供参考，实际投资请结合多种因素综合判断。您可以在设置中调整模型参数以提高预测准确性。

### 3. 界面显示异常
请确保安装了所有依赖包，并尝试更换界面主题。

## 技术支持

如有问题或建议，请通过以下方式联系：
- 邮箱：contact@aiinvestment-advisor.com
- 网站：www.aiinvestment-advisor.com

## 许可证

本项目采用MIT许可证发布。详见LICENSE文件。

## 免责声明

本应用提供的所有预测和建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。