# config.py

INITIAL_CAPITAL = 1000

# Windows
SHORT_WINDOW = 500
LONG_WINDOW = 2000

# === Strategy Selector ===
INDICATOR_TYPE = 'EMA'  # Options: SMA, EMA, WMA, RSI, MACD

# Strategy Behavior Flags
ENABLE_SELL_ON_DOWNTREND = False
ENABLE_PROFIT_TARGET = True
ENABLE_STOP_LOSS = True

# Trading Parameters
TRADE_FEE = 0.001
PROFIT_TARGET = 0.01
STOP_LOSS = 0.02

# Data Path
DATA_PATH = './data/BTCUSD.csv'
START_DATE = '2022-01-10T00:00:00+00:00'
END_DATE = '2022-08-01T11:59:00+00:00'

# Logging Configuration
LOG_FOLDER = './logs'
LOG_FILE = f"{LOG_FOLDER}/trading_bot.log"
LOG_LEVEL = 'DEBUG'
