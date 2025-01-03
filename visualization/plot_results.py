# visualization/plot_results.py
import matplotlib.pyplot as plt
from utils.logger import logger


def plot_results(df, output_file='trading_results.png'):
    """
    Plot the trading results, including all Long and Short transactions, for any strategy.

    Args:
        df (pd.DataFrame): DataFrame containing trading data.
        output_file (str): Path to save the plot.
    """
    logger.info("📊 Generating trading results plot...")

    plt.figure(figsize=(16, 8))
    
    # Plot Close Price
    plt.plot(df.index, df['close'], label='Close Price', linewidth=1, color='gray')

    # Plot Indicators (if available)
    indicators = {
        'FAST_IND': {'label': 'Fast Indicator', 'style': '--', 'color': 'blue'},
        'SLOW_IND': {'label': 'Slow Indicator', 'style': '--', 'color': 'orange'}
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
    
    # Plot Long and Short Transactions
    if 'Action' in df.columns:
        actions = [
            ('GO_LONG', '^', 'green', 'Go Long'),
            ('CLOSE_LONG', 'v', 'lime', 'Close Long'),
            ('GO_SHORT', '>', 'red', 'Go Short'),
            ('CLOSE_SHORT', '<', 'orange', 'Close Short'),
            ('STOP-LOSS', 'x', 'purple', 'Stop-Loss')
        ]
        
        for action, marker, color, label in actions:
            plt.plot(
                df.index[df['Action'] == action],
                df['close'][df['Action'] == action],
                marker,
                color=color,
                markersize=8,
                label=label
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
