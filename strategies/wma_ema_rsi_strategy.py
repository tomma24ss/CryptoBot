# strategies/wma_ema_rsi_strategy.py
import pandas as pd
from strategies.base_strategy import BaseStrategy
from utils.logger import logger


class WMA_EMA_RSI_Strategy(BaseStrategy):
    def __init__(self, data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss, short_window, long_window):
        super().__init__(data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss)
        self.short_window = short_window
        self.long_window = long_window
        
        # Add indicators
        self.data['WMA50'] = self.data['close'].rolling(window=self.short_window).mean().fillna(method='backfill')
        self.data['EMA200'] = self.data['close'].ewm(span=self.long_window, adjust=False).mean().fillna(method='backfill')
        self.data['RSI'] = self.calculate_rsi(self.data['close'])
        
        # Initialize Action Column for Plotting
        self.data['Action'] = None
        
        logger.info("📊 WMA + EMA + RSI Strategy initialized.")
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index (RSI)."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs)).fillna(50)
    
    def run(self):
        logger.info("🚀 WMA + EMA + RSI Strategy run started.")
        
        for i in range(1, len(self.data)):
            current_price = self.data['close'].iloc[i]
            wma50 = self.data['WMA50'].iloc[i]
            ema200 = self.data['EMA200'].iloc[i]
            rsi = self.data['RSI'].iloc[i]
            timestamp = self.data.index[i]
            
            if pd.isna(wma50) or pd.isna(ema200) or pd.isna(rsi):
                continue
            
            logger.debug(
                f"{timestamp} - Price: {current_price:.2f}, WMA50: {wma50:.2f}, EMA200: {ema200:.2f}, "
                f"RSI: {rsi:.2f}, Position: {self.current_position}, Uptrend: {self.uptrend_triggered}"
            )
            
            # 🟢 BUY Condition
            self.execute_trade(
                condition=wma50 > ema200 and not self.uptrend_triggered and self.current_position == 0 and rsi < 30,
                action='BUY',
                current_price=current_price,
                timestamp=timestamp
            )
            
            # 🛑 STOP-LOSS Condition
            self.execute_trade(
                condition=self.current_position == 1 and self.enable_stop_loss and current_price <= self.stop_loss_price,
                action='STOP-LOSS',
                current_price=current_price,
                timestamp=timestamp
            )
            
            # 🔴 SELL Condition
            self.execute_trade(
                condition=self.current_position == 1 and (wma50 < ema200 or rsi > 70),
                action='SELL',
                current_price=current_price,
                timestamp=timestamp
            )
        
        logger.info("🏁 WMA + EMA + RSI Strategy run completed.")
