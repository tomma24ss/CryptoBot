# ma_strategy.py

import backtrader as bt

class MovingAverageStrategy(bt.Strategy):
    """
    A simple Moving Average Crossover strategy.
    Buys when SMA(10) crosses above SMA(50) and sells when it crosses below.
    """
    def __init__(self):
        self.sma10 = bt.indicators.SimpleMovingAverage(self.data.close, period=10)
        self.sma50 = bt.indicators.SimpleMovingAverage(self.data.close, period=50)
    
    def next(self):
        if self.sma10[0] > self.sma50[0] and self.sma10[-1] <= self.sma50[-1]:
            self.buy()
        if self.sma10[0] < self.sma50[0] and self.sma10[-1] >= self.sma50[-1]:
            self.sell()
