# strategies/base_strategy.py
import pandas as pd
from utils.logger import logger


class BaseStrategy:
    def __init__(self, data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss):
        self.data = data
        self.balance = initial_capital
        self.initial_capital = initial_capital
        self.trade_fee = trade_fee
        self.profit_target = profit_target
        self.stop_loss = stop_loss
        self.enable_stop_loss = enable_stop_loss
        
        self.current_position = 0  # 0: No Position, 1: Holding Position
        self.entry_price = None
        self.stop_loss_price = None
        self.assets = 0
        self.uptrend_triggered = False
        self.total_fees = 0  # Track total fees paid during all trades
        
        self.data['Action'] = None
        logger.info("📊 Base Strategy Initialized")
    
    def calculate_sell_price(self, entry_price):
        """Calculate the target sell price, considering profit target and fees."""
        return entry_price * (1 + self.profit_target + 2 * self.trade_fee)
    
    def calculate_stop_loss_price(self, entry_price):
        """Calculate the stop-loss price."""
        return entry_price * (1 - self.stop_loss)
    
    def execute_buy(self, current_price, timestamp):
        """Handles the buy logic."""
        self.assets = self.balance / current_price
        self.entry_price = current_price
        self.stop_loss_price = self.calculate_stop_loss_price(current_price) if self.enable_stop_loss else None
        
        # Calculate and track buy fee
        fee = current_price * self.assets * self.trade_fee
        self.total_fees += fee
        
        logger.info(
            f"🟢 BUY Triggered | Price: {current_price:.2f}, Assets: {self.assets:.6f}, "
            f"Stop-Loss: {self.stop_loss_price}, Fee: ${fee:.2f}, Timestamp: {timestamp}"
        )
        
        self.data.at[timestamp, 'Action'] = 'BUY'
        self.balance = 0
        self.current_position = 1
    
    def execute_sell(self, current_price, timestamp):
        """Handles the sell logic."""
        profit = (current_price - self.entry_price) * self.assets * (1 - 2 * self.trade_fee)
        percentage_gain = (profit / (self.entry_price * self.assets)) * 100
        fee = current_price * self.assets * self.trade_fee
        self.total_fees += fee
        self.balance = (self.entry_price * self.assets) + profit
        
        logger.info(
            f"🔴 SELL Triggered | Price: {current_price:.2f}, Profit: ${profit:.2f} ({percentage_gain:.2f}%), "
            f"Fee: ${fee:.2f}, New Balance: ${self.balance:.2f}, Timestamp: {timestamp}"
        )
        
        self.data.at[timestamp, 'Action'] = 'SELL'
        self.current_position = 0
        self.assets = 0
        # self.uptrend_triggered = False  # Only reset uptrend when SELL happens intentionally
    
    def execute_stop_loss(self, current_price, timestamp):
        """Handles the stop-loss logic."""
        loss = (self.entry_price - current_price) * self.assets * (1 - 2 * self.trade_fee)
        percentage_loss = (loss / (self.entry_price * self.assets)) * 100
        fee = current_price * self.assets * self.trade_fee
        self.total_fees += fee
        self.balance = (self.entry_price * self.assets) - abs(loss)
        
        logger.warning(
            f"🛑 STOP-LOSS Triggered | Price: {current_price:.2f}, Loss: ${loss:.2f} ({percentage_loss:.2f}%), "
            f"Fee: ${fee:.2f}, New Balance: ${self.balance:.2f}, Timestamp: {timestamp}"
        )
        
        self.data.at[timestamp, 'Action'] = 'STOP-LOSS'
        self.current_position = 0
        self.assets = 0
        # Stop-loss does NOT reset uptrend
    
    def finalize_performance(self):
        """Log final performance details."""
        logger.info(f"🏁 Final Balance: ${self.balance:.2f}")
        logger.info(f"💸 Total Fees Paid: ${self.total_fees:.2f}")
    
    def run(self):
        """Ensure each strategy implements its own run logic."""
        raise NotImplementedError("Each strategy must implement its own 'run' method.")
