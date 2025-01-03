# strategies/ma_strategy.py
import pandas as pd
from strategies.base_strategy import BaseStrategy
from utils.logger import logger


class MovingAverageStrategy(BaseStrategy):
    def __init__(self, data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss, short_window, long_window):
        super().__init__(data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss)
        self.short_window = short_window
        self.long_window = long_window
        
        self.data['SMA50'] = self.data['close'].rolling(window=self.short_window, min_periods=1).mean()
        self.data['SMA200'] = self.data['close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # Initialize Action Column for Plotting
        self.data['Action'] = None
        
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
                f"{timestamp} - Price: {current_price:.2f}, SMA50: {sma50:.2f}, SMA200: {sma200:.2f}, Position: {self.current_position}"
            )
            
            # 🟢 BUY Condition
            if sma50 > sma200 and self.current_position == 0 and not self.uptrend_triggered:
                self.assets = self.balance / current_price
                self.entry_price = current_price
                self.stop_loss_price = self.calculate_stop_loss_price(current_price) if self.enable_stop_loss else None
                
                logger.info(
                    f"🟢 BUY Triggered | Price: {current_price:.2f}, Assets: {self.assets:.6f}, "
                    f"Stop-Loss: {self.stop_loss_price}, Timestamp: {timestamp}"
                )
                
                self.data.at[timestamp, 'Action'] = 'BUY'  # Important for plotting
                
                self.balance = 0
                self.current_position = 1
                self.uptrend_triggered = True
            
            # 🔴 SELL or STOP-LOSS Condition
            if self.current_position == 1:
                # Check for Stop-Loss
                if self.enable_stop_loss and current_price <= self.stop_loss_price:
                    loss = (self.entry_price - current_price) * self.assets * (1 - 2 * self.trade_fee)
                    percentage_loss = (loss / (self.entry_price * self.assets)) * 100
                    self.balance = (self.entry_price * self.assets) - abs(loss)
                    
                    logger.warning(
                        f"🛑 STOP-LOSS Triggered | Price: {current_price:.2f}, Loss: ${loss:.2f} ({percentage_loss:.2f}%), "
                        f"New Balance: ${self.balance:.2f}, Timestamp: {timestamp}"
                    )
                    
                    self.data.at[timestamp, 'Action'] = 'STOP-LOSS'  # Important for plotting
                    
                    self.current_position = 0
                    self.assets = 0
                    continue
                
                # Check for Profit Target (SELL)
                target_sell_price = self.calculate_sell_price(self.entry_price)
                if current_price >= target_sell_price:
                    profit = (current_price - self.entry_price) * self.assets * (1 - 2 * self.trade_fee)
                    percentage_gain = (profit / (self.entry_price * self.assets)) * 100
                    self.balance = (self.entry_price * self.assets) + profit
                    
                    logger.info(
                        f"🔴 SELL Triggered | Price: {current_price:.2f}, Profit: ${profit:.2f} ({percentage_gain:.2f}%), "
                        f"New Balance: ${self.balance:.2f}, Timestamp: {timestamp}"
                    )
                    
                    self.data.at[timestamp, 'Action'] = 'SELL'  # Important for plotting
                    
                    self.current_position = 0
                    self.assets = 0
            
            # Reset Uptrend Trigger if Trend Reverses
            if sma50 <= sma200:
                self.uptrend_triggered = False
        
        logger.info("🏁 Moving Average Strategy run completed.")
