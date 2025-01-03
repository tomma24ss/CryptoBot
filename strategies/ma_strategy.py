# strategies/ma_strategy.py
import pandas as pd
from strategies.base_strategy import BaseStrategy
from utils.logger import logger


class MovingAverageStrategy(BaseStrategy):
    def __init__(self, data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss, short_window, long_window):
        super().__init__(data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss)
        self.short_window = short_window
        self.long_window = long_window
        
        # Add indicators
        self.data['SMA50'] = self.data['close'].rolling(window=self.short_window, min_periods=1).mean()
        self.data['SMA200'] = self.data['close'].rolling(window=self.long_window, min_periods=1).mean()
        
        logger.info("📊 Moving Average Strategy initialized.")
    
    def run(self):
        logger.info("🚀 Moving Average Strategy run started.")
        
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
            
            # 🟢 1. BUY Condition 
            if self.current_position == 0 and not self.uptrend_triggered and sma50 > sma200:
                self.execute_buy(current_price, timestamp)
                self.uptrend_triggered = True
                continue  # Prevent SELL or STOP-LOSS on the same timestamp
            
            # 🛑 STOP-LOSS Condition: Price hits stop-loss
            if self.current_position == 1 and self.enable_stop_loss and current_price <= self.stop_loss_price:
                self.execute_stop_loss(current_price, timestamp)
                continue  # Ensure no further logic executes after a stop-loss
            
            # 🔴 SELL Condition: Profit target reached
            if self.current_position == 1:
                target_sell_price = self.calculate_sell_price(self.entry_price)
                if current_price >= target_sell_price:
                    self.execute_sell(current_price, timestamp)
            
            # 🔄 Reset Uptrend Trigger if Trend Reverses
            if sma50 <= sma200:
                self.uptrend_triggered = False
        
        logger.info("🏁 Moving Average Strategy run completed.")
