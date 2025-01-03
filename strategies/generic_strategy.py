# strategies/generic_strategy.py
import pandas as pd
from strategies.base_strategy import BaseStrategy
from utils.logger import logger

from numba import njit
from tqdm import tqdm  # For visual progress bars


class GenericStrategy(BaseStrategy):
    def __init__(self, data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss,
                 short_window, long_window, indicator_type, enable_sell_on_downtrend, enable_profit_target):
        super().__init__(data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss)
        self.short_window = short_window
        self.long_window = long_window
        self.indicator_type = indicator_type
        self.enable_sell_on_downtrend = enable_sell_on_downtrend
        self.enable_profit_target = enable_profit_target

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
            logger.info("🟢 Calculating SMA (Simple Moving Average)...")
            self.data['SHORT_IND'] = self.data['close'].rolling(window=self.short_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)
            self.data['LONG_IND'] = self.data['close'].rolling(window=self.long_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)

        elif self.indicator_type == 'EMA':
            logger.info("🟡 Calculating EMA (Exponential Moving Average)...")
            self.data['SHORT_IND'] = self.data['close'].ewm(span=self.short_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)
            self.data['LONG_IND'] = self.data['close'].ewm(span=self.long_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)

        elif self.indicator_type == 'WMA':
            logger.info("🔵 Calculating WMA (Weighted Moving Average)...")
            self.data['SHORT_IND'] = self._calculate_weighted_moving_average(self.data['close'], self.short_window, progress_bar)
            self.data['LONG_IND'] = self._calculate_weighted_moving_average(self.data['close'], self.long_window, progress_bar)

        elif self.indicator_type == 'RSI':
            logger.info("🟤 Calculating RSI (Relative Strength Index)...")
            delta = self.data['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=self.short_window, min_periods=1).mean()
            avg_loss = loss.rolling(window=self.short_window, min_periods=1).mean()
            rs = avg_gain / avg_loss
            self.data['SHORT_IND'] = 100 - (100 / (1 + rs))
            progress_bar.update(total_steps // 2)
            self.data['LONG_IND'] = self.data['SHORT_IND'].rolling(window=self.long_window, min_periods=1).mean()
            progress_bar.update(total_steps // 2)

        elif self.indicator_type == 'MACD':
            logger.info("🟠 Calculating MACD (Moving Average Convergence Divergence)...")
            short_ema = self.data['close'].ewm(span=self.short_window, min_periods=1).mean()
            long_ema = self.data['close'].ewm(span=self.long_window, min_periods=1).mean()
            self.data['SHORT_IND'] = short_ema - long_ema
            progress_bar.update(total_steps // 2)
            self.data['LONG_IND'] = self.data['SHORT_IND'].ewm(span=9, min_periods=1).mean()
            progress_bar.update(total_steps // 2)

        else:
            raise ValueError(f"Indicator '{self.indicator_type}' is not supported.")
        
        progress_bar.close()
        logger.info(f"✅ Indicator {self.indicator_type} calculation completed.")


    @staticmethod
    @njit
    def _calculate_weighted_moving_average(values, window, progress_bar):
        """
        Calculate the Weighted Moving Average (WMA) with Numba for performance optimization.
        """
        result = np.full(len(values), np.nan)
        weights = np.arange(1, window + 1)

        for i in range(window - 1, len(values)):
            window_values = values[i - window + 1:i + 1]
            if not np.isnan(window_values).any():
                result[i] = np.sum(window_values * weights) / np.sum(weights)
            if i % (len(values) // 10) == 0:  # Update progress every 10%
                progress_bar.update(len(values) // 10)

        progress_bar.update(len(values) % (len(values) // 10))
        return result

    def run(self):
        logger.info("🚀 Generic Strategy run started.")
        
        for i in range(1, len(self.data)):
            current_price = self.data['close'].iloc[i]
            short_ind = self.data['SHORT_IND'].iloc[i]
            long_ind = self.data['LONG_IND'].iloc[i]
            timestamp = self.data.index[i]
            
            if pd.isna(short_ind) or pd.isna(long_ind):
                continue

            logger.debug(
                f"{timestamp} - Price: {current_price:.2f}, SHORT_IND: {short_ind:.2f}, LONG_IND: {long_ind:.2f}, "
                f"Position: {self.current_position}, Uptrend: {self.uptrend_triggered}"
            )

            # 🟢 BUY Condition
            if self.current_position == 0 and not self.uptrend_triggered and short_ind > long_ind:
                self.execute_buy(current_price, timestamp)
                self.uptrend_triggered = True
                continue

            # 🛑 STOP-LOSS Condition
            if self.current_position == 1 and self.enable_stop_loss and current_price <= self.stop_loss_price:
                self.execute_stop_loss(current_price, timestamp)
                continue

            # 🔴 SELL Condition
            if self.current_position == 1:
                if self.enable_profit_target and current_price >= self.calculate_sell_price(self.entry_price):
                    if self.enable_sell_on_downtrend and short_ind < long_ind:
                        self.execute_sell(current_price, timestamp)
                    elif not self.enable_sell_on_downtrend:
                        self.execute_sell(current_price, timestamp)

            # 🔄 Reset Uptrend Trigger
            if short_ind <= long_ind:
                self.uptrend_triggered = False

        logger.info("🏁 Generic Strategy run completed.")
