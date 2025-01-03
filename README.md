# 🚀 **Crypto Trading Bot**

## 📊 **Overview**

Welcome to the **Crypto Trading Bot** – an advanced Python-based cryptocurrency trading framework. This bot automates trading strategies, incorporates robust risk management techniques, and visualizes trading performance.

---

## 🛠️ **Features**

- **Multiple Trading Strategies:**  
   - 📈 **Moving Average Strategy:** Ride trends with SMA and EMA.  
   - 📉 **Trend Reversal Strategy:** Detect reversals for strategic entries and exits.  
- **Stop-Loss Mechanism:** Protect your capital with dynamic stop-loss logic.  
- **Custom Configurations:** Fine-tune strategies in `config.py` with options for stop-loss, profit targets, and more.  
- **Detailed Performance Metrics:** Compare your strategy with benchmark performance.  
- **Visualization Tools:** Clear graphs showing buy/sell points and stop-loss triggers.  
- **Logging:** Comprehensive logs for every trade action.

---

## 📂 **Project Structure**

```plaintext
CryptoTradingBot/
├── backtest/
│   ├── data_loader.py       # Load and preprocess market data
│   ├── performance.py       # Calculate trading performance metrics
│
├── strategies/
│   ├── base_strategy.py     # Base trading strategy class
│   ├── generic_strategy.py  # Configurable trading strategy
│
├── visualization/
│   ├── plot_results.py      # Plot trading outcomes
│
├── utils/
│   ├── logger.py            # Logging setup
│
├── data/
│   ├── BTCUSD.csv           # Historical BTC/USD data
│
├── config.py                # Configurations for the bot
├── main.py                  # Entry point for execution
├── requirements.txt         # Required Python libraries
└── README.md                # Project documentation
```

---

## ⚙️ **Configuration**

Edit `config.py` to adjust trading parameters:

```python
# General Settings
INITIAL_CAPITAL = 1000
TRADE_FEE = 0.001  # 0.1% per trade
PROFIT_TARGET = 0.01  # 1% profit target
STOP_LOSS = 0.02  # 2% stop-loss

# Strategy Settings
STRATEGY = 'GenericStrategy'  # Options: 'GenericStrategy'
INDICATOR_TYPE = 'EMA'  # Options: SMA, EMA, WMA, RSI, MACD

# Trading Windows
SHORT_WINDOW = 500
LONG_WINDOW = 2000

# Data Source
DATA_PATH = './data/BTCUSD.csv'
START_DATE = '2022-01-10T00:00:00+00:00'
END_DATE = '2022-08-01T11:59:00+00:00'
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
- Logs: `./logs/trading_bot.log`
- Visualization: `./trading_results.png`

---

## 📊 **Trading Strategies**

### **1. Generic Strategy**
- **Dynamic Indicators:** Choose from SMA, EMA, WMA, RSI, or MACD.  
- **Configurable Logic:** Control profit targets, stop-loss, and trend behaviors.  
- **Long/Short Positions:** Enable or disable long and short trading.  

### **2. Stop-Loss Logic**
- **Automatic Trigger:** Exit trades when stop-loss conditions are met.  
- **Adjustable Parameters:** Tune stop-loss and profit targets in `config.py`.

---

## 📈 **Performance Metrics**

At the end of each run, key performance metrics are displayed:
- 🏁 **Final Portfolio Value:** Realized profit/loss.  
- 💼 **Unrealized Value:** Open position value.  
- 📊 **Benchmark Comparison:** Against a simple buy-and-hold approach.  
- 💸 **Total Fees Paid:** Cumulative trading fees.

---

## 📊 **Visualization**

The trading outcomes are visualized with:
- 📈 **Close Price Line:** Tracks market price.  
- 🟢 **Buy Signals:** Marked with green triangles.  
- 🔴 **Sell Signals:** Marked with red triangles.  
- 🛑 **Stop-Loss Triggers:** Indicated with purple crosses.  

Results are saved as `trading_results.png`.

---

## 📚 **Dependencies**

Ensure you have the required Python packages:
- `pandas`
- `numpy`
- `matplotlib`
- `tqdm`
- `numba`

Install them with:
```bash
pip install -r requirements.txt
```

---

## 🤝 **Contributing**

We welcome your contributions!  
1. Fork the project.  
2. Create a feature branch: `git checkout -b feature-new-strategy`.  
3. Commit changes: `git commit -m "Add new strategy"`.  
4. Push to the branch: `git push origin feature-new-strategy`.  
5. Open a Pull Request.  

---

## 🐞 **Troubleshooting**

- **Missing Data:** Ensure `BTCUSD.csv` exists in `./data`.  
- **Visualization Errors:** Verify your matplotlib backend.  
- **Logs Missing:** Check the configuration in `logger.py`.

---

## 🌐 **Resources**

- [Backtrader Documentation](https://www.backtrader.com/docu/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Numba Documentation](https://numba.pydata.org/)

---

## 🛡️ **License**

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

## 📬 **Contact**

- **Author:** Tomma Vlaemynck  
- **Email:** your.email@example.com  
- **LinkedIn:** [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)

---

## ⭐ **Support the Project**

If you found this project helpful, don’t forget to ⭐ star it on GitHub!

Happy Trading! 🚀📊💼

---