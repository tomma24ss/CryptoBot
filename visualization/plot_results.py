# visualization/plot_results.py
import matplotlib.pyplot as plt
from utils.logger import logger


def plot_results(df, output_file='trading_results.png'):
    """
    Plot the trading results, including Buy, Sell, and Stop-Loss actions, for any strategy.

    Args:
        df (pd.DataFrame): DataFrame containing trading data.
        output_file (str): Path to save the plot.
    """
    logger.info("📊 Generating trading results plot...")

    plt.figure(figsize=(16, 8))
    
    # Plot Close Price
    plt.plot(df.index, df['close'], label='Close Price', linewidth=1, color='gray')

    # Dynamic Plotting for Indicators
    indicators = {
        'SMA50': {'label': 'SMA50 (Short-term)', 'style': '--', 'color': 'blue'},
        'SMA200': {'label': 'SMA200 (Long-term)', 'style': '--', 'color': 'orange'},
        'WMA50': {'label': 'WMA50 (Weighted Moving Average)', 'style': '-.', 'color': 'green'},
        'EMA200': {'label': 'EMA200 (Exponential Moving Average)', 'style': '-.', 'color': 'purple'},
        # 'RSI': {'label': 'RSI (Relative Strength Index)', 'style': ':', 'color': 'brown'}
    }
    
    for col, params in indicators.items():
        if col in df.columns:
            plt.plot(
                df.index, 
                df[col], 
                label=params['label'], 
                linestyle=params['style'], 
                linewidth=1, 
                color=params['color']
            )
    
    # Plot Buy Actions
    if 'Action' in df.columns:
        plt.plot(
            df.index[df['Action'] == 'BUY'],
            df['close'][df['Action'] == 'BUY'],
            '^', color='green', markersize=6, label='Buy Action'
        )
    
    # Plot Sell Actions
    if 'Action' in df.columns:
        plt.plot(
            df.index[df['Action'] == 'SELL'],
            df['close'][df['Action'] == 'SELL'],
            'v', color='red', markersize=6, label='Sell Action'
        )
    
    # Plot Stop-Loss Actions
    if 'Action' in df.columns:
        plt.plot(
            df.index[df['Action'] == 'STOP-LOSS'],
            df['close'][df['Action'] == 'STOP-LOSS'],
            'x', color='purple', markersize=8, label='Stop-Loss Action'
        )
    
    # Add Titles, Labels, and Grid
    plt.title('Trading Strategy Performance')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend(loc='upper left', fontsize='small', title='Legend', title_fontsize='medium')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    # Save Plot
    plt.savefig(output_file)
    logger.info(f"✅ Plot saved as {output_file}")
    
    # Close Plot to Avoid Memory Issues
    plt.close()
