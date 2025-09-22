import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.utils import dropna
import yaml

class FeatureEngineer:
    def __init__(self):
        with open("config/config.yaml", 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.lags = self.config['features']['lags']
        self.windows = self.config['features']['windows']
    
    
    def create_features(self, df):
        """Create lag features for the close price"""
        if df.empty:
            return df
        
        df = df.copy()
        
        #ensure sorted by time
        df = df.sort_values(['symbol','open_time']).reset_index(drop = True)
        #calculate returns
        df['returns']= df.groupby('symbol')["close"].pct_change()
        
        #add all technical indicators
        
        df = add_all_ta_features(
            df, open="open", high="high", low="low", 
            close="close", volume="volume", fillna=True
        )
        
        #create lag features
        
        for lag in self.lags:
            df[f'close_lag_{lag}'] = df.groupby('symbol')['close'].shift(lag)
            df[f'returns_lag_{lag}'] = df.groupby('symbol')['returns'].shift(lag)
            
        #rolling statistics
        
        for window in self.windows:
            df[f'roll_mean_{window}'] = df.groupby('symbol')['close'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df[f'roll_std_{window}'] = df.groupby('symbol')['close'].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            )
            df[f'roll_vol_{window}'] = df.groupby('symbol')['volume'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            
            
        df['price_change_7d'] =df.groupby('symbol')['close'].pct_change(7)
        df['price_change_30d'] = df.groupby('symbol')['close'].pct_change(30)
        
        #volatility features 
        df['volatility_7d'] = df.groupby('symbol')['returns'].transform(
            lambda x: x.rolling(window=7, min_periods=1).std()
        )
        df['volatility_30d'] = df.groupby('symbol')['returns'].transform(
            lambda x: x.rolling(window=30, min_periods=1).std()
        )
        
         # Target variable (next day's close price)
        df['target'] = df.groupby('symbol')['close'].shift(-1)
        
        # Drop rows with NaN values
        df = dropna(df)
        
        return df
    
    def process_symbol(self, symbol, df):
        """Process data for a specific symbol"""
        symbol_data = df[df['symbol'] == symbol].copy()
        processed_data = self.create_features(symbol_data)
        return processed_data

    def save_processed_data(self, df, symbol):
        """Save processed data for a symbol"""
        os.makedirs(self.config['data']['processed_dir'], exist_ok=True)
        df.to_csv(f"{self.config['data']['processed_dir']}/processed_{symbol}.csv", index=False)
        print(f"Processed data saved for {symbol}")
        
def main():
    # Load raw data
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    raw_data_path = config['data']['raw_path']
    
    try:
        df = pd.read_csv(raw_data_path)
        print(f"Loaded data with {len(df)} records")
    except FileNotFoundError:
        print("Raw data file not found. Run data collector first.")
        return
    
    # Initialize feature engineer
    engineer = FeatureEngineer()
    
    # Process each symbol
    symbols = df['symbol'].unique()
    for symbol in symbols:
        print(f"Processing {symbol}...")
        symbol_df = df[df['symbol'] == symbol]
        processed_df = engineer.create_features(symbol_df)
        engineer.save_processed_data(processed_df, symbol)
    
    print("Feature engineering completed!")

if __name__ == "__main__":
    main()

        

