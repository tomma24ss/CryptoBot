# config.py
MODE = 'BACKTEST'  # Mode: BACKTEST or LIVE
INITIAL_CAPITAL = 10

# Enable Long and Short Trading
ENABLE_LONGING = True
ENABLE_SHORTING = True

# Exit Conditions
ENABLE_PROFIT_TARGET = True
ENABLE_CLOSE_LONG_ON_DOWNTREND = False   # For Long positions
ENABLE_CLOSE_SHORT_ON_UPTREND = False    # For Short positions
ENABLE_STOP_LOSS = True

# Windows
SHORT_WINDOW = 1000
LONG_WINDOW = 4000

# === Strategy Selector ===
INDICATOR_TYPE = 'EMA'  # Options: SMA, EMA, WMA, RSI, MACD


# Trading Parameters
TRADE_FEE = 0.001
PROFIT_TARGET = 0.05
STOP_LOSS = 0.02

# Data Path
DATA_PATH = './data/BTCUSD.csv'
START_DATE = '2022-01-10T00:00:00+00:00'
END_DATE = '2022-08-01T11:59:00+00:00'  

# Logging Configuration
LOG_FOLDER = './logs'
LOG_FILE = f"{LOG_FOLDER}/trading_bot.log"
LOG_LEVEL = 'DEBUG'

# API Configuration for Live Trading
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
