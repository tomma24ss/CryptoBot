# strategies/trend_reversal_strategy.py
import pandas as pd
from strategies.base_strategy import BaseStrategy
from utils.logger import logger


class TrendReversalStrategy(BaseStrategy):
    def __init__(self, data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss, short_window, long_window):
        super().__init__(data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss)
        self.short_window = short_window
        self.long_window = long_window
        
        # Add indicators
        self.data['SMA50'] = self.data['close'].rolling(window=self.short_window, min_periods=1).mean()
        self.data['SMA200'] = self.data['close'].rolling(window=self.long_window, min_periods=1).mean()
        
        logger.info("📊 Trend Reversal Strategy initialized.")
    
    def run(self):
        logger.info("🚀 Trend Reversal Strategy run started.")
        
        for i in range(1, len(self.data)):
            current_price = self.data['close'].iloc[i]
            sma50 = self.data['SMA50'].iloc[i]
            sma200 = self.data['SMA200'].iloc[i]
            timestamp = self.data.index[i]
            
            if pd.isna(sma50) or pd.isna(sma200):
                continue
            
            logger.debug(
                f"{timestamp} - Price: {current_price:.2f}, SMA50: {sma50:.2f}, SMA200: {sma200:.2f}, "
                f"Position: {self.current_position}, Uptrend: {self.uptrend_triggered}"
            )
            
            # 🟢 BUY Condition: Uptrend Detected, No Active Position
            if sma50 > sma200 and self.current_position == 0 and not self.uptrend_triggered:
                self.execute_buy(current_price, timestamp)
                self.uptrend_triggered = True
                continue
            
            # 🛑 STOP-LOSS Condition: Price Falls Below Stop-Loss Price
            if self.current_position == 1 and self.enable_stop_loss and current_price <= self.stop_loss_price:
                self.execute_stop_loss(current_price, timestamp)
                continue  # Prevent further logic execution after a stop-loss
            
            # 🔴 SELL Condition: Profit Target Reached & Downtrend Detected
            if self.current_position == 1 and current_price >= self.calculate_sell_price(self.entry_price) and sma50 < sma200:
                self.execute_sell(current_price, timestamp)
            
            # 🔄 Reset Uptrend Trigger if Trend Reverses
            if sma50 <= sma200:
                self.uptrend_triggered = False

        logger.info("🏁 Trend Reversal Strategy run completed.")
