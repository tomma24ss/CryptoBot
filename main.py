# main.py
from config import *
from backtest.data_loader import DataLoader
from strategies.generic_strategy import GenericStrategy
from backtest.performance import PerformanceMetrics
from visualization.plot_results import plot_results
from utils.logger import logger

logger.info("🚀 Starting the trading bot...")

# 📊 Load Data
data_loader = DataLoader(DATA_PATH, START_DATE, END_DATE)
df = data_loader.load_data()

# 🛠️ Run Generic Strategy
strategy = GenericStrategy(
    data=df,
    initial_capital=INITIAL_CAPITAL,
    trade_fee=TRADE_FEE,
    profit_target=PROFIT_TARGET,
    stop_loss=STOP_LOSS,
    enable_stop_loss=ENABLE_STOP_LOSS,
    short_window=SHORT_WINDOW,
    long_window=LONG_WINDOW,
    indicator_type=INDICATOR_TYPE,
    enable_sell_on_downtrend=ENABLE_SELL_ON_DOWNTREND,
    enable_profit_target=ENABLE_PROFIT_TARGET
)

strategy.run()
# 📈 Performance Metrics
PerformanceMetrics.calculate_performance(
    df=df,
    initial_capital=INITIAL_CAPITAL,
    balance=strategy.balance,
    current_position=strategy.current_position,
    entry_price=strategy.entry_price,
    assets=strategy.assets,
    total_fees=strategy.total_fees
)

# 📊 Plot Results
plot_results(df)
logger.info("✅ Trading bot execution completed.")
