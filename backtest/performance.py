# backtest/performance.py
from utils.logger import logger


class PerformanceMetrics:
    @staticmethod
    def calculate_performance(df, initial_capital, balance, current_position, entry_price, assets, total_fees):
        """
        Calculate and display the strategy's performance metrics.
        
        Args:
            df (pd.DataFrame): DataFrame with trading data.
            initial_capital (float): Starting capital.
            balance (float): Final cash balance after backtest.
            current_position (int): Indicates if an open position exists (0: No, 1: Yes).
            entry_price (float): Entry price of the current position, if any.
            assets (float): Amount of assets held if there's an open position.
            total_fees (float): Total trading fees accumulated during the strategy.
        """
        if df.empty or 'close' not in df.columns:
            logger.warning("⚠️ DataFrame is empty or missing 'close' column. Skipping performance calculation.")
            return
        
        try:
            initial_price = df['close'].iloc[0]
            final_price = df['close'].iloc[-1]
        except IndexError:
            logger.warning("⚠️ Not enough data for performance calculation.")
            return

        # 🧮 Benchmark Calculation
        buy_and_hold_return = final_price / initial_price
        benchmark_final = initial_capital * buy_and_hold_return
        
        # 🧮 Unrealized Value Calculation (if position is still open)
        unrealized_value = 0
        if current_position == 1 and assets > 0:
            unrealized_value = assets * final_price * (1 - 2 * 0.001)  # Adjust for trading fees
        
        # 🧮 Final Portfolio Value
        if current_position == 1:
            # Position is still open
            strategy_final = unrealized_value
        else:
            # Position is closed, use final balance
            strategy_final = balance
        
        # 🧮 Virtual Portfolio Value
        virtual_balance = balance + unrealized_value
        
        # 📝 Comparison with Benchmark
        comparison = "outperformed" if virtual_balance > benchmark_final else "underperformed"
        
        # 📝 Log Results
        logger.info(f"🏁 Final Portfolio Value (Realized Balance): ${balance:.2f}")
        logger.info(f"💼 Final Crypto Balance (Unrealized Value): ${unrealized_value:.2f}")
        logger.info(f"📊 Final Virtual Portfolio Value: ${virtual_balance:.2f}")
        logger.info(f"📈 Benchmark Portfolio Value: ${benchmark_final:.2f}")
        logger.info(f"🏆 The strategy has {comparison} the benchmark by ${virtual_balance - benchmark_final:.2f}")
        
        # 💸 Log Fees
        logger.info(f"💸 Total Fees Paid: ${total_fees:.2f}")
