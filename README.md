# 🚀 Crypto Trading Bot

## 📊 **Overview**

Welcome to the **Crypto Trading Bot** – an automated cryptocurrency trading framework built with Python. This bot leverages advanced trading strategies, risk management, and data visualization tools to help traders automate their strategies and analyze performance effectively.

---

## 🛠️ **Features**

- **Multiple Trading Strategies**  
   - 📈 **Moving Average Strategy:** Buy on uptrend, sell on profit target.  
   - 📉 **Trend Reversal Strategy:** Sell on downtrend if profit target is reached.  
- **Stop-Loss Protection:** Protect your balance with trade-level and account-level stop-losses.  
- **Dynamic Configurations:** Customize parameters like stop-loss percentage, profit targets, and strategy selection via `config.py`.  
- **Comprehensive Logging:** Track every trade with detailed logs stored in log files.  
- **Performance Metrics:** Get insights into your strategy's performance with key metrics.  
- **Visualization:** Generate graphs showing buy, sell, and stop-loss points.

---

## 📂 **Project Structure**

```plaintext
CryptoTradingBot/
├── backtest/
│   ├── data_loader.py       # Load and preprocess trading data
│   ├── performance.py       # Calculate performance metrics
│
├── strategies/
│   ├── base_strategy.py     # Base class for all strategies
│   ├── ma_strategy.py       # Moving Average Strategy
│   ├── trend_reversal_strategy.py # Trend Reversal Strategy
│
├── visualization/
│   ├── plot_results.py      # Plot results with buy, sell, and stop-loss points
│
├── utils/
│   ├── logger.py            # Logging configuration
│
├── data/
│   ├── BTCUSD.csv           # Historical price data for BTC/USD
│
├── config.py                # Configuration file for parameters
├── main.py                  # Entry point for running the trading bot
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## ⚙️ **Configuration**

Edit `config.py` to customize your trading bot settings:

```python
# General Settings
INITIAL_CAPITAL = 100
TRADE_FEE = 0.001  # 0.1% per trade
PROFIT_TARGET = 0.005  # 0.5% profit target
STOP_LOSS = 0.01  # 1% stop-loss
ENABLE_STOP_LOSS = True  # Toggle stop-loss functionality

# Strategy Selection
STRATEGY = 'MovingAverageStrategy'  # Options: 'MovingAverageStrategy', 'TrendReversalStrategy'
```

---

## ▶️ **How to Run**

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/CryptoTradingBot.git
cd CryptoTradingBot
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Run the Bot**
```bash
python main.py
```

### **4. View Logs and Results**
- Logs: `logs/trading.log`
- Visualization: `output/trading_results.png`

---

## 📊 **Trading Strategies**

### **1. Moving Average Strategy**
- **Buy:** When short-term SMA crosses above long-term SMA.  
- **Sell:** When profit target is reached.  
- **Stop-Loss:** Optional, configurable in `config.py`.

### **2. Trend Reversal Strategy**
- **Buy:** Same as Moving Average Strategy.  
- **Sell:** When profit target is reached AND a downtrend is detected (SMA50 crosses below SMA200).  
- **Stop-Loss:** Optional, configurable in `config.py`.

---

## 📈 **Performance Metrics**

At the end of each run, key metrics are displayed:
- 📊 **Final Portfolio Value:** Total capital after backtest.  
- 📉 **Unrealized Crypto Balance:** Value of remaining crypto.  
- 💼 **Benchmark Comparison:** Compare against buy-and-hold strategy.

---

## 🛡️ **Risk Management**

- **Trade-Level Stop-Loss:** Automatically exit losing trades.  
- **Account-Level Stop-Loss:** Stop trading if the balance falls below a certain threshold.

---

## 📊 **Visualization**

- 📈 Price Chart with SMA50 and SMA200.
- 🟢 **Buy Signals:** Green upward markers (`^`).  
- 🔴 **Sell Signals:** Red downward markers (`v`).  
- 🛑 **Stop-Loss Triggers:** Red cross markers (`x`).  
- 📊 Exported as `trading_results.png`.

---

## 📚 **Dependencies**

Make sure you have the following Python packages installed:
- `pandas`
- `matplotlib`
- `numpy`
- `backtrader`

Install them using:
```bash
pip install -r requirements.txt
```

---

## 🤝 **Contributing**

We welcome contributions! To contribute:
1. Fork the project.
2. Create a feature branch: `git checkout -b feature-new-strategy`.
3. Commit your changes: `git commit -m "Add new strategy"`.
4. Push to the branch: `git push origin feature-new-strategy`.
5. Open a Pull Request.

---

## 🐞 **Troubleshooting**

- **Missing Data:** Ensure the `BTCUSD.csv` file exists in the `/data` directory.
- **Visualization Issues:** Ensure matplotlib backend supports your environment (use `Agg` for headless servers).
- **Logs Not Appearing:** Verify the logging setup in `logger.py`.

---

## 🌐 **Resources**

- [Backtrader Documentation](https://www.backtrader.com/docu/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Trading Strategy Examples](https://www.investopedia.com/)

---

## 🛡️ **License**

This project is licensed under the **MIT License**. See `LICENSE` for more information.

---

## 📬 **Contact**

- **Author:** Luca Vlaemynck  
- **Email:** your.email@example.com  
- **LinkedIn:** [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)

---

## ⭐ **Support the Project**

If you found this project useful, consider giving it a ⭐ on GitHub!

Happy Trading! 🚀📊💼
```

---

## ✅ **What This README Covers:**

1. Clear **overview** of the project.  
2. **Project structure** explanation.  
3. How to **run the bot** and **customize settings**.  
4. Explanation of **strategies** and **performance metrics**.  
5. Guidance for **troubleshooting** and **contributing**.

Let me know if you'd like to add/remove anything! 🚀📊😊