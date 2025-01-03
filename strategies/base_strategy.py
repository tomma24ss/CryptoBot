# strategies/base_strategy.py
import pandas as pd
from utils.logger import logger


class BaseStrategy:
    def __init__(self, data, initial_capital, trade_fee, profit_target, stop_loss, enable_stop_loss,
                 enable_longing=True, enable_shorting=False):
        """
        Initialize the Base Strategy with trading parameters.

        Args:
            data (pd.DataFrame): Trading data.
            initial_capital (float): Initial cash balance.
            trade_fee (float): Fee percentage per trade.
            profit_target (float): Profit target percentage.
            stop_loss (float): Stop-loss percentage.
            enable_stop_loss (bool): Toggle stop-loss functionality.
            enable_longing (bool): Toggle long position functionality.
            enable_shorting (bool): Toggle short position functionality.
        """
        self.data = data
        self.balance = initial_capital
        self.initial_capital = initial_capital
        self.trade_fee = trade_fee
        self.profit_target = profit_target
        self.stop_loss = stop_loss
        self.enable_stop_loss = enable_stop_loss
        self.enable_longing = enable_longing
        self.enable_shorting = enable_shorting

        self.current_position = 0  # 0: No Position, 1: Long Position, -1: Short Position
        self.entry_price = None
        self.stop_loss_price = None
        self.assets = 0
        self.uptrend_triggered = False
        self.downtrend_triggered = False
        self.total_fees = 0  # Track total fees paid during all trades

        # New Metrics
        self.long_profit = 0
        self.long_loss = 0
        self.short_profit = 0
        self.short_loss = 0

        self.data['Action'] = None
        logger.info("📊 Base Strategy Initialized")

    def calculate_close_long_price(self, entry_price):
        return entry_price * (1 + self.profit_target + 2 * self.trade_fee)

    def calculate_close_short_price(self, entry_price):
        return entry_price * (1 - self.profit_target - 2 * self.trade_fee)

    def calculate_stop_loss_price(self, entry_price, is_short=False):
        return entry_price * (1 + self.stop_loss) if is_short else entry_price * (1 - self.stop_loss)

    # === STOP-LOSS LOGIC ===
    def execute_stop_loss(self, current_price, timestamp):
        if self.current_position == 1:  # Long Position Stop-Loss
            loss = (self.entry_price - current_price) * self.assets * (1 - 2 * self.trade_fee)
            percentage_loss = (loss / (self.entry_price * self.assets)) * 100
            self.long_loss += abs(loss)
        elif self.current_position == -1:  # Short Position Stop-Loss
            loss = (current_price - self.entry_price) * self.assets * (1 - 2 * self.trade_fee)
            percentage_loss = (loss / (self.entry_price * self.assets)) * 100
            self.short_loss += abs(loss)
        else:
            logger.warning("⚠️ STOP-LOSS Triggered but no active position found. Skipping...")
            return

        fee = current_price * self.assets * self.trade_fee
        self.total_fees += fee
        self.balance = (self.entry_price * self.assets) - abs(loss)
        self.current_position = 0
        self.assets = 0

        logger.warning(
            f"🛑 STOP-LOSS Triggered | Position: {self.current_position}, Price: {current_price:.2f}, "
            f"Loss: ${loss:.2f} ({percentage_loss:.2f}%), Fee: ${fee:.2f}, New Balance: ${self.balance:.2f}, Timestamp: {timestamp}"
        )

        self.data.at[timestamp, 'Action'] = 'STOP-LOSS'

    # === LONG POSITION LOGIC ===
    def execute_go_long(self, current_price, timestamp):
        if not self.enable_longing:
            logger.warning("🛑 GO_LONG is disabled via ENABLE_LONGING.")
            return

        self.assets = self.balance / current_price
        self.entry_price = current_price
        self.stop_loss_price = self.calculate_stop_loss_price(current_price) if self.enable_stop_loss else None

        fee = current_price * self.assets * self.trade_fee
        self.total_fees += fee

        logger.info(
            f"🟢 GO_LONG Triggered | Price: {current_price:.2f}, Assets: {self.assets:.6f}, "
            f"Stop-Loss: {self.stop_loss_price}, Fee: ${fee:.2f}, Timestamp: {timestamp}"
        )

        self.data.at[timestamp, 'Action'] = 'GO_LONG'
        self.balance = 0
        self.current_position = 1

    def execute_close_long(self, current_price, timestamp):
        profit = (current_price - self.entry_price) * self.assets * (1 - 2 * self.trade_fee)
        percentage_gain = (profit / (self.entry_price * self.assets)) * 100

        if profit > 0:
            self.long_profit += profit
        else:
            self.long_loss += abs(profit)

        fee = current_price * self.assets * self.trade_fee
        self.total_fees += fee
        self.balance = (self.entry_price * self.assets) + profit

        logger.info(
            f"🔴 CLOSE_LONG Triggered | Price: {current_price:.2f}, Profit: ${profit:.2f} "
            f"({percentage_gain:.2f}%), Fee: ${fee:.2f}, New Balance: ${self.balance:.2f}, Timestamp: {timestamp}"
        )

        self.data.at[timestamp, 'Action'] = 'CLOSE_LONG'
        self.current_position = 0
        self.assets = 0

    # === SHORT POSITION LOGIC ===
    def execute_go_short(self, current_price, timestamp):
        if not self.enable_shorting:
            logger.warning("🛑 GO_SHORT is disabled via ENABLE_SHORTING.")
            return

        self.assets = self.balance / current_price
        self.entry_price = current_price
        self.stop_loss_price = self.calculate_stop_loss_price(current_price, is_short=True) if self.enable_stop_loss else None

        fee = current_price * self.assets * self.trade_fee
        self.total_fees += fee

        logger.info(
            f"🔻 GO_SHORT Triggered | Price: {current_price:.2f}, Assets: {self.assets:.6f}, "
            f"Stop-Loss: {self.stop_loss_price}, Fee: ${fee:.2f}, Timestamp: {timestamp}"
        )

        self.data.at[timestamp, 'Action'] = 'GO_SHORT'
        self.balance = 0
        self.current_position = -1

    def execute_close_short(self, current_price, timestamp):
        profit = (self.entry_price - current_price) * self.assets * (1 - 2 * self.trade_fee)
        percentage_gain = (profit / (self.entry_price * self.assets)) * 100

        if profit > 0:
            self.short_profit += profit
        else:
            self.short_loss += abs(profit)

        fee = current_price * self.assets * self.trade_fee
        self.total_fees += fee
        self.balance = (self.entry_price * self.assets) + profit

        logger.info(
            f"🔼 CLOSE_SHORT Triggered | Price: {current_price:.2f}, Profit: ${profit:.2f} "
            f"({percentage_gain:.2f}%), Fee: ${fee:.2f}, New Balance: ${self.balance:.2f}, Timestamp: {timestamp}"
        )

        self.data.at[timestamp, 'Action'] = 'CLOSE_SHORT'
        self.current_position = 0
        self.assets = 0

    def finalize_performance(self):
        logger.info(f"🏁 Final Balance: ${self.balance:.2f}")
        logger.info(f"💸 Total Fees Paid: ${self.total_fees:.2f}")
        logger.info(f"📈 Long Profit: ${self.long_profit:.2f}, Long Loss: ${self.long_loss:.2f}")
        logger.info(f"📉 Short Profit: ${self.short_profit:.2f}, Short Loss: ${self.short_loss:.2f}")
