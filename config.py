# config.py

INITIAL_CAPITAL = 1000

# Windows
SHORT_WINDOW = 1000
LONG_WINDOW = 3000

# === Strategy Selector ===
# Strategy Selection
STRATEGY = 'MovingAverageStrategy'  # Options: 'MovingAverageStrategy', 'TrendReversalStrategy', 'WMA_EMA_RSI_Strategy'

# Trading Parameters
TRADE_FEE = 0.001
PROFIT_TARGET = 0.05 #0.005
STOP_LOSS = 0.02  # 1% stop-loss
ENABLE_STOP_LOSS = True  # Toggle stop-loss functionality

# Data Path
DATA_PATH = './data/BTCUSD.csv'
START_DATE = '2022-01-10T00:00:00+00:00'
END_DATE = '2022-06-25T14:39:00+00:00'
# START_DATE = '2025-01-01T18:12:00+00:00' 
# END_DATE = '2025-01-02T15:52:00+00:00'
# Logging Configuration
LOG_FOLDER = './logs'
LOG_FILE = f"{LOG_FOLDER}/trading_bot.log"
LOG_LEVEL = 'DEBUG'
