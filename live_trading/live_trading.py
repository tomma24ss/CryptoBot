# live_trading.py
import time
import pandas as pd
from utils.logger import logger
from strategies.generic_strategy import GenericStrategy

class LiveTrading:
    def __init__(self, api_client, strategy_config, pair='BTCUSD'):
        """
        Initialize Live Trading Module
        Args:
            api_client: Exchange API client for live data and orders.
            strategy_config: Configuration dictionary for strategy parameters.
            pair: Trading pair.
        """
        self.api_client = api_client
        self.pair = pair
        self.strategy = GenericStrategy(
            data=pd.DataFrame(),  # Will dynamically update with live data
            **strategy_config
        )
        logger.info("✅ Live Trading Initialized")

    def fetch_live_data(self):
        """Fetch live market data from the exchange."""
        ticker = self.api_client.fetch_ticker(self.pair)
        return {
            'timestamp': pd.Timestamp.now(),
            'close': float(ticker['last']),
            'open': float(ticker['open']),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'volume': float(ticker['volume']),
        }

    def start_trading(self):
        """Start the live trading loop."""
        logger.info("🚀 Starting Live Trading Loop...")
        try:
            while True:
                new_data = self.fetch_live_data()
                self.strategy.data = self.strategy.data.append(new_data, ignore_index=True)
                self.strategy.run()
                time.sleep(60)  # Adjust for your preferred frequency (e.g., 1 minute)
        except KeyboardInterrupt:
            logger.info("🛑 Live Trading Stopped Manually")
