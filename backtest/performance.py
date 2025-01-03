# backtest/performance.py
from utils.logger import logger


class PerformanceMetrics:
    @staticmethod
    def calculate_performance(
        df, 
        initial_capital, 
        balance, 
        current_position, 
        entry_price, 
        assets, 
        total_fees, 
        long_profit, 
        long_loss, 
        short_profit, 
        short_loss
    ):
        """
        Calculate and display the strategy's performance metrics.
        
        Args:
            df (pd.DataFrame): DataFrame with trading data.
            initial_capital (float): Starting capital.
            balance (float): Final cash balance after backtest.
            current_position (int): Indicates if an open position exists (0: No, 1: Long, -1: Short).
            entry_price (float): Entry price of the current position, if any.
            assets (float): Amount of assets held if there's an open position.
            total_fees (float): Total trading fees accumulated during the strategy.
            long_profit (float): Total profit from long positions.
            long_loss (float): Total loss from long positions.
            short_profit (float): Total profit from short positions.
            short_loss (float): Total loss from short positions.
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
        
        # Initialize virtual_balance to balance
        virtual_balance = balance
        unrealized_value = 0
        
        # 🧮 Unrealized Value Calculation
        if current_position == 1 and assets > 0:  # Open Long Position
            unrealized_value = assets * final_price * (1 - 2 * 0.001)  # Adjust for trading fees
            unrealized_percentage = ((final_price - entry_price) / entry_price) * 100
            virtual_balance = balance + unrealized_value
            logger.info(
                f"🟢 Open Long Position Detected | Entry Price: ${entry_price:.2f}, "
                f"Current Price: ${final_price:.2f}, Unrealized P&L: ${unrealized_value:.2f} "
                f"({unrealized_percentage:.2f}%), Virtual Balance: ${virtual_balance:.2f}"
            )

        elif current_position == -1 and assets > 0:  # Open Short Position
            unrealized_value = (entry_price - final_price) * assets * (1 - 2 * 0.001)  # Adjust for trading fees
            margin_value = entry_price * assets  # Margin used for the short position
            virtual_balance = margin_value + unrealized_value
            logger.info(
                f"🔻 Open Short Position Detected | Entry Price: ${entry_price:.2f}, "
                f"Current Price: ${final_price:.2f}, Unrealized P&L: ${unrealized_value:.2f}, "
                f"Margin Value: ${margin_value:.2f}, Virtual Balance: ${virtual_balance:.2f}"
            )
        
        else:
            virtual_balance = balance  # Default to balance if no open position
            logger.info("⚪ No Open Position Detected | Virtual Balance equals realized balance.")

        # 📝 Comparison with Benchmark
        comparison = "outperformed" if virtual_balance > benchmark_final else "underperformed"
        
        # 📝 Log Results
        logger.info(f"🏁 Final Portfolio Value (Realized Balance): ${balance:.2f}")
        logger.info(f"💼 Unrealized P&L: ${unrealized_value:.2f}")
        logger.info(f"📊 Final Virtual Portfolio Value: ${virtual_balance:.2f}")
        logger.info(f"📈 Benchmark Portfolio Value: ${benchmark_final:.2f}")
        logger.info(f"🏆 The strategy has {comparison} the benchmark by ${virtual_balance - benchmark_final:.2f}")
        
        # 💸 Log Fees
        logger.info(f"💸 Total Fees Paid: ${total_fees:.2f}")
        
        # 📊 Long Position Stats
        net_long_result = long_profit - long_loss
        logger.info(f"🟢 Total Long Profit: ${long_profit:.2f}")
        logger.info(f"🔴 Total Long Loss: ${long_loss:.2f}")
        logger.info(f"📊 Net Long Result: ${net_long_result:.2f}")
        
        # 📊 Short Position Stats
        net_short_result = short_profit - short_loss
        logger.info(f"🔻 Total Short Profit: ${short_profit:.2f}")
        logger.info(f"🔼 Total Short Loss: ${short_loss:.2f}")
        logger.info(f"📊 Net Short Result: ${net_short_result:.2f}")
        
        # 🏆 Overall Performance
        total_net_result = net_long_result + net_short_result
        logger.info(f"📈 Total Net Result (Long + Short): ${total_net_result:.2f}")
        logger.info("✅ Performance metrics calculation completed successfully.")
