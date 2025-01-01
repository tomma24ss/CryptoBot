import ccxt  # Binance API library
import time

# --- Configuration ---
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
SYMBOL = 'BTC/USDT'
SHORT_SMA_PERIOD = 7
LONG_SMA_PERIOD = 25
PROFIT_TARGET = 0.005  # 0.5% profit

# Initialize Binance Exchange
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True
})

# --- Utility Functions ---
def fetch_prices(symbol, limit=50):
    """Fetch historical OHLCV data."""
    candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=limit)
    return [candle[4] for candle in candles]  # Closing prices

def calculate_sma(prices, period):
    """Calculate Simple Moving Average."""
    return sum(prices[-period:]) / period

def get_balance():
    """Get current USDT balance."""
    balance = exchange.fetch_balance()
    return balance['USDT']['free']

def buy(symbol, amount):
    """Place a market buy order."""
    return exchange.create_market_buy_order(symbol, amount)

def sell(symbol, amount):
    """Place a market sell order."""
    return exchange.create_market_sell_order(symbol, amount)

# --- Main Strategy Loop ---
try:
    position = False
    entry_price = 0
    
    while True:
        prices = fetch_prices(SYMBOL, limit=LONG_SMA_PERIOD)
        short_sma = calculate_sma(prices, SHORT_SMA_PERIOD)
        long_sma = calculate_sma(prices, LONG_SMA_PERIOD)
        current_price = prices[-1]
        
        print(f"Short SMA: {short_sma}, Long SMA: {long_sma}, Price: {current_price}")
        
        if not position and short_sma > long_sma:
            # Uptrend detected, Buy!
            balance = get_balance()
            if balance > 10:  # Minimum balance to trade
                amount = balance / current_price
                buy(SYMBOL, amount)
                entry_price = current_price
                position = True
                print(f"Bought {amount} {SYMBOL} at {entry_price}")
        
        if position:
            profit = (current_price - entry_price) / entry_price
            print(f"Current Profit: {profit * 100:.2f}%")
            
            if profit >= PROFIT_TARGET:
                # Take Profit
                crypto_balance = exchange.fetch_balance()[SYMBOL.split('/')[0]]['free']
                sell(SYMBOL, crypto_balance)
                print(f"Sold at {current_price}, Profit: {profit * 100:.2f}%")
                position = False
                entry_price = 0
        
        time.sleep(60)  # Run every minute

except KeyboardInterrupt:
    print("Bot stopped by user.")
except Exception as e:
    print(f"Error: {e}")
