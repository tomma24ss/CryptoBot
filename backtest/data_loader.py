# backtest/data_loader.py
import pandas as pd
from utils.logger import logger

class DataLoader:
    def __init__(self, file_path, start_date, end_date):
        self.file_path = file_path
        self.start_date = start_date
        self.end_date = end_date
    
    def load_data(self):
        logger.info("Loading data from CSV file...")
        df = pd.read_csv(self.file_path, parse_dates=['timestamp'], index_col='timestamp')
        df = df.loc[self.start_date:self.end_date].copy()
        df.rename(columns={'price': 'close'}, inplace=True)
        logger.info(f"Data loaded successfully with {len(df)} rows.")
        
        required_columns = {'close', 'open', 'high', 'low', 'volume'}
        if not required_columns.issubset(df.columns):
            logger.error(f"Missing required columns: {required_columns - set(df.columns)}")
            raise ValueError("Missing required columns.")
        
        return df
