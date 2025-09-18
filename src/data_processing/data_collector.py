import pandas as pd
import requests
import time 
import os 
import yaml
from datetime import datetime, timedelta


class CryptoDataCollector:
    def __init__(self):
        with open("config/config.yaml", 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.base_url = self.config['binance']['base_url']
        self.symbols = self.config['models']['supported_symbols']
        
    def fetch_historical_data(self, symbol, interval='1d',limit =1000):
        endpoint = "/klines"
        params = {
            'symbols': symbol,
            'interval': interval,
            'limit': limit    
        }
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
            
            # Convert timestamp to datetime
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            df['symbol'] = symbol
            
            return df
        
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
        
    def fetch_multiple_symbols(self, symbols=None, interval='1d', limit=1000):
        """Fetch data for multiple symbols"""
        if symbols is None:
            symbols = self.symbols
            
        all_data = []
        for symbol in symbols:
            print(f"Fetching data for {symbol}...")
            df = self.fetch_historical_data(symbol, interval, limit)
            if not df.empty:
                all_data.append(df)
            time.sleep(0.2)  # Rate limiting
            
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    
    def fetch_historical_data(self, symbol, interval='1d', limit=1000):
        """Fetch historical data from Binance API"""
        endpoint = "/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert types
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
            
            # Convert timestamp to datetime
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            df['symbol'] = symbol
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
        
    def fetch_multiple_symbols(self, symbols=None, interval='1d', limit=1000):
        """Fetch data for multiple symbols"""
        if symbols is None:
            symbols = self.symbols
            
        all_data = []
        for symbol in symbols:
            print(f"Fetching data for {symbol}...")
            df = self.fetch_historical_data(symbol, interval, limit)
            if not df.empty:
                all_data.append(df)
            time.sleep(0.2)  # Rate limiting
            
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    
    def load_local_data(self):
        """Load data from local CSV file"""
        try:
            df = pd.read_csv(self.config['data']['raw_path'])
            return df
        except FileNotFoundError:
            print("Local data file not found. Using API data only.")
            return pd.DataFrame()
    
    def get_combined_data(self):
        """Combine local data with API data"""
        local_data = self.load_local_data()
        api_data = self.fetch_multiple_symbols(limit=2000)
        
        if not local_data.empty and not api_data.empty:
            # Combine both data sources
            combined = pd.concat([local_data, api_data], ignore_index=True)
            # Remove duplicates
            combined = combined.drop_duplicates(subset=['symbol', 'open_time'])
            return combined
        elif not api_data.empty:
            return api_data
        else:
            return local_data
    
    def save_data(self, df, filename="crypto_data_combined.csv"):
        """Save data to CSV"""
        os.makedirs(self.config['data']['raw_path'], exist_ok=True)
        df.to_csv(f"{self.config['data']['raw_path']}/{filename}", index=False)
        print(f"Data saved to {self.config['data']['raw_path']}/{filename}")

def main():
    collector = CryptoDataCollector()
    data = collector.get_combined_data()
    
    if not data.empty:
        collector.save_data(data)
        print(f"Data collection completed. Collected {len(data)} records for {data['symbol'].nunique()} symbols.")
    else:
        print("No data was collected.")

if __name__ == "__main__":
    main()