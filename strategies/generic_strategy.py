# strategies/generic_strategy.py
import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
from utils.logger import logger

from numba import njit
from tqdm import tqdm  # For visual progress bars


class GenericStrategy(BaseStrategy):
    def __init__(self, data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss,
                 short_window, long_window, indicator_type, enable_close_long_on_downtrend,
                 enable_close_short_on_uptrend, enable_profit_target,
                 enable_longing=True, enable_shorting=False):
        """
        Initialize the Generic Strategy with configuration parameters.

        Args:
            data (pd.DataFrame): Market data.
            initial_capital (float): Initial capital.
            trade_fee (float): Trading fee percentage.
            profit_target (float): Profit target percentage.
            stop_loss (float): Stop-loss percentage.
            enable_stop_loss (bool): Toggle stop-loss functionality.
            short_window (int): Window for short-term indicator.
            long_window (int): Window for long-term indicator.
            indicator_type (str): Type of indicator (SMA, EMA, WMA, RSI, MACD).
            enable_close_long_on_downtrend (bool): Enable closing long positions on downtrend.
            enable_close_short_on_uptrend (bool): Enable closing short positions on uptrend.
            enable_profit_target (bool): Enable profit target.
            enable_longing (bool): Enable long trading.
            enable_shorting (bool): Enable short trading.
        """
        super().__init__(
            data, initial_capital, trade_fee, profit_target, stop_loss,
            enable_stop_loss, enable_longing, enable_shorting
        )
        self.short_window = short_window
        self.long_window = long_window
        self.indicator_type = indicator_type
        self.enable_close_long_on_downtrend = enable_close_long_on_downtrend
        self.enable_close_short_on_uptrend = enable_close_short_on_uptrend
        self.enable_profit_target = enable_profit_target

        self.uptrend_triggered = False
        self.downtrend_triggered = False

        # Apply indicators based on config
        self._apply_indicator()
        logger.info("📊 Generic Strategy initialized with configuration.")

    def _apply_indicator(self):
        """
        Apply the selected indicator type to the data with optimized calculations and progress logging.
        Supports: SMA, EMA, WMA, RSI, MACD
        """
        logger.info(f"📊 Calculating indicators: {self.indicator_type}")
        total_steps = len(self.data)
        progress_bar = tqdm(total=total_steps, desc=f"Calculating {self.indicator_type}", unit="row")

        if self.indicator_type == 'SMA':
            self.data['FAST_IND'] = self.data['close'].rolling(window=self.short_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)
            self.data['SLOW_IND'] = self.data['close'].rolling(window=self.long_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)

        elif self.indicator_type == 'EMA':
            self.data['FAST_IND'] = self.data['close'].ewm(span=self.short_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)
            self.data['SLOW_IND'] = self.data['close'].ewm(span=self.long_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)

        elif self.indicator_type == 'WMA':
            self.data['FAST_IND'] = self._calculate_weighted_moving_average(self.data['close'], self.short_window, progress_bar)
            self.data['SLOW_IND'] = self._calculate_weighted_moving_average(self.data['close'], self.long_window, progress_bar)

        elif self.indicator_type == 'RSI':
            delta = self.data['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=self.short_window, min_periods=1).mean()
            avg_loss = loss.rolling(window=self.short_window, min_periods=1).mean()
            rs = avg_gain / avg_loss
            self.data['FAST_IND'] = 100 - (100 / (1 + rs))
            progress_bar.update(total_steps // 2)
            self.data['SLOW_IND'] = self.data['FAST_IND'].rolling(window=self.long_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)

        elif self.indicator_type == 'MACD':
            fast_ema = self.data['close'].ewm(span=self.short_window, min_periods=1).mean()
            slow_ema = self.data['close'].ewm(span=self.long_window, min_periods=1).mean()
            self.data['FAST_IND'] = fast_ema - slow_ema
            progress_bar.update(total_steps // 2)
            self.data['SLOW_IND'] = self.data['FAST_IND'].ewm(span=9, min_periods=1).mean()
            progress_bar.update(total_steps // 2)

        else:
            raise ValueError(f"Indicator '{self.indicator_type}' is not supported.")
        
        progress_bar.close()
        logger.info(f"✅ Indicator {self.indicator_type} calculation completed.")

    def run(self):
        logger.info("🚀 Generic Strategy run started.")
        
        for i in range(1, len(self.data)):
            current_price = self.data['close'].iloc[i]
            fast_ind = self.data['FAST_IND'].iloc[i]
            slow_ind = self.data['SLOW_IND'].iloc[i]
            timestamp = self.data.index[i]

            if pd.isna(fast_ind) or pd.isna(slow_ind):
                continue

            # === LONG POSITION LOGIC ===
            if self.enable_longing:
                if self.current_position == 0 and not self.uptrend_triggered and fast_ind > slow_ind:
                    self.execute_go_long(current_price, timestamp)
                    self.uptrend_triggered = True
                    continue

                if self.current_position == 1 and self.enable_stop_loss and current_price <= self.stop_loss_price:
                    self.execute_stop_loss(current_price, timestamp)
                    continue

                # === LONG POSITION LOGIC ===
                if self.current_position == 1:
                    if self.enable_profit_target and self.enable_close_long_on_downtrend:
                        # ✅ Both enabled: Check both conditions
                        if current_price >= self.calculate_close_long_price(self.entry_price) and fast_ind < slow_ind:
                            self.execute_close_long(current_price, timestamp)
                    elif self.enable_profit_target:
                        # ✅ Only Profit Target enabled
                        if current_price >= self.calculate_close_long_price(self.entry_price):
                            self.execute_close_long(current_price, timestamp)
                    elif self.enable_close_long_on_downtrend:
                        # ✅ Only Close on Downtrend enabled
                        if fast_ind < slow_ind:
                            self.execute_close_long(current_price, timestamp)
                    else:
                        # ❌ Invalid Configuration
                        logger.error("⚠️ Invalid configuration: Both enable_profit_target and enable_close_long_on_downtrend are False.")
                        raise ValueError("Both enable_profit_target and enable_close_long_on_downtrend cannot be False.")

                if fast_ind <= slow_ind:
                    self.uptrend_triggered = False

            # === SHORT POSITION LOGIC ===
            if self.enable_shorting:
                # 🟢 Enter Short Position
                if self.current_position == 0 and not self.downtrend_triggered and fast_ind < slow_ind:
                    self.execute_go_short(current_price, timestamp)
                    self.downtrend_triggered = True
                    continue

                # 🛑 Stop-Loss for Short Position
                if self.current_position == -1 and self.enable_stop_loss and current_price >= self.stop_loss_price:
                    self.execute_stop_loss(current_price, timestamp)
                    continue

                # 🔻 Close Short Position
                if self.current_position == -1:
                    if self.enable_profit_target and self.enable_close_short_on_uptrend:
                        # Both enabled: Check both conditions
                        if current_price <= self.calculate_close_short_price(self.entry_price) and fast_ind > slow_ind:
                            self.execute_close_short(current_price, timestamp)
                    elif self.enable_profit_target:
                        # Only Profit Target enabled
                        if current_price <= self.calculate_close_short_price(self.entry_price):
                            self.execute_close_short(current_price, timestamp)
                    elif self.enable_close_short_on_uptrend:
                        # Only Sell on Downtrend enabled
                        if fast_ind > slow_ind:
                            self.execute_close_short(current_price, timestamp)
                    else:
                        # ❌ Invalid Configuration: No valid conditions to close the position
                        logger.error("⚠️ Invalid configuration: Both enable_profit_target and enable_close_short_on_uptrend are False.")
                        raise ValueError("Both enable_profit_target and enable_close_short_on_uptrend cannot be False.")

                # 🔄 Reset Downtrend Trigger
                if fast_ind >= slow_ind:
                    self.downtrend_triggered = False

        logger.info("🏁 Generic Strategy run completed.")
