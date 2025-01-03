# main.py
from config import *
from backtest.data_loader import DataLoader
from strategies.generic_strategy import GenericStrategy
from backtest.performance import PerformanceMetrics
from visualization.plot_results import plot_results
from visualization.interactive_plot import interactive_plot_results
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
    enable_close_long_on_downtrend=ENABLE_CLOSE_LONG_ON_DOWNTREND,
    enable_close_short_on_uptrend=ENABLE_CLOSE_SHORT_ON_UPTREND,
    enable_profit_target=ENABLE_PROFIT_TARGET,
    enable_longing=ENABLE_LONGING,
    enable_shorting=ENABLE_SHORTING
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
    total_fees=strategy.total_fees,
    long_profit=strategy.long_profit,
    long_loss=strategy.long_loss,
    short_profit=strategy.short_profit,
    short_loss=strategy.short_loss
)

# 📊 Plot Results
plot_results(df)
interactive_plot_results(df)
logger.info("✅ Trading bot execution completed.")
