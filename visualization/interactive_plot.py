# visualization/interactive_plot.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.logger import logger


def interactive_plot_results(df, output_file='trading_results.html'):
    """
    Create an interactive plot showing trading results, including all Long and Short transactions.

    Args:
        df (pd.DataFrame): DataFrame containing trading data.
        output_file (str): Path to save the plot.
    """
    logger.info("📊 Generating interactive trading results plot...")

    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, subplot_titles=['Trading Strategy Performance'])

    # Plot Close Price
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['close'],
            mode='lines',
            name='Close Price',
            line=dict(color='gray', width=1)
        )
    )

    # Plot Indicators (if available)
    indicators = {
        'FAST_IND': {'name': 'Fast Indicator', 'color': 'blue', 'dash': 'dash'},
        'SLOW_IND': {'name': 'Slow Indicator', 'color': 'orange', 'dash': 'dash'}
    }

    for col, params in indicators.items():
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode='lines',
                    name=params['name'],
                    line=dict(color=params['color'], dash=params['dash'])
                )
            )

    # Plot Long and Short Transactions
    if 'Action' in df.columns:
        actions = [
            ('GO_LONG', 'triangle-up', 'green', 'Go Long'),
            ('CLOSE_LONG', 'triangle-down', 'lime', 'Close Long'),
            ('GO_SHORT', 'triangle-right', 'red', 'Go Short'),
            ('CLOSE_SHORT', 'triangle-left', 'orange', 'Close Short'),
            ('STOP-LOSS', 'x', 'purple', 'Stop-Loss')
        ]

        for action, symbol, color, label in actions:
            action_df = df[df['Action'] == action]
            if not action_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=action_df.index,
                        y=action_df['close'],
                        mode='markers',
                        name=label,
                        marker=dict(symbol=symbol, color=color, size=10)
                    )
                )

    # Update Layout
    fig.update_layout(
        title='Trading Strategy Performance',
        xaxis_title='Time',
        yaxis_title='Price',
        legend_title='Legend',
        hovermode='x unified',
        template='plotly_dark',
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.3)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.3)'),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Save as HTML
    fig.write_html(output_file)
    logger.info(f"✅ Interactive plot saved as {output_file}")
