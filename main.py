from config import *
from backtest.data_loader import DataLoader
from strategies.ma_strategy import MovingAverageStrategy
from strategies.trend_reversal_strategy import TrendReversalStrategy
from strategies.wma_ema_rsi_strategy import WMA_EMA_RSI_Strategy
from backtest.performance import PerformanceMetrics
from visualization.plot_results import plot_results
from utils.logger import logger

logger.info("🚀 Starting the trading bot...")

# 📊 Load Data
data_loader = DataLoader(DATA_PATH, START_DATE, END_DATE)
df = data_loader.load_data()

# 🛠️ Select and Run Strategy
if STRATEGY == 'MovingAverageStrategy':
    strategy = MovingAverageStrategy(
        data=df,
        initial_capital=INITIAL_CAPITAL,
        trade_fee=TRADE_FEE,
        profit_target=PROFIT_TARGET,
        stop_loss=STOP_LOSS,
        enable_stop_loss=ENABLE_STOP_LOSS,
        short_window=SHORT_WINDOW,
        long_window=LONG_WINDOW
    )
elif STRATEGY == 'TrendReversalStrategy':
    strategy = TrendReversalStrategy(
        data=df,
        initial_capital=INITIAL_CAPITAL,
        trade_fee=TRADE_FEE,
        profit_target=PROFIT_TARGET,
        stop_loss=STOP_LOSS,
        enable_stop_loss=ENABLE_STOP_LOSS,
        short_window=SHORT_WINDOW,
        long_window=LONG_WINDOW
    )
elif STRATEGY == 'WMA_EMA_RSI_Strategy':
    strategy = WMA_EMA_RSI_Strategy(
        data=df,
        initial_capital=INITIAL_CAPITAL,
        trade_fee=TRADE_FEE,
        profit_target=PROFIT_TARGET,
        stop_loss=STOP_LOSS,
        enable_stop_loss=ENABLE_STOP_LOSS,
        short_window=SHORT_WINDOW,
        long_window=LONG_WINDOW
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
