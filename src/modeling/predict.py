import pandas as pd
import numpy as np
import os
from src.data_processing.feature_engineering import FeatureEngineer
import joblib
import json
import yaml
from datetime import datetime, timedelta
from src.data_processing.feature_engineering import FeatureEngineer

class CryptoPredictor:
    def __init__(self):
        # Load configuration
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.models = {}
        self.feature_columns = []
        self.load_models()
    
    def load_models(self):
        """Load trained models and feature columns"""
        try:
            # Load feature columns
            with open(f"{self.config['model']['model_dir']}/feature_columns.json", "r") as f:
                self.feature_columns = json.load(f)
            
            # Load models for each symbol
            for symbol in self.config['model']['supported_symbols']:
                model_path = f"{self.config['model']['model_dir']}/{symbol}_model.joblib"
                if os.path.exists(model_path):
                    self.models[symbol] = joblib.load(model_path)
                    print(f"✅ Loaded model for {symbol}")
                else:
                    print(f"❌ Model not found for {symbol}")
                    
        except FileNotFoundError as e:
            print(f"Error loading models: {e}. Train models first.")
    
    def prepare_prediction_data(self, symbol, df):
        """Prepare data for prediction"""
        engineer = FeatureEngineer()
        processed_df = engineer.create_features(df)
        
        if processed_df.empty:
            return None
        
        # Get the most recent data point
        latest_data = processed_df.iloc[-1:]
        
        # Ensure we have the right features
        available_features = [col for col in self.feature_columns if col in latest_data.columns]
        missing_features = [col for col in self.feature_columns if col not in latest_data.columns]
        
        if missing_features:
            print(f"Warning: Missing features for prediction: {missing_features}")
        
        return latest_data[available_features]
    
    def predict(self, symbol, df, days=1):
        """Make prediction for a symbol"""
        if symbol not in self.models:
            return None, None
        
        # Prepare data for prediction
        prediction_data = self.prepare_prediction_data(symbol, df)
        
        if prediction_data is None:
            return None, None
        
        # Make prediction
        prediction = self.models[symbol].predict(prediction_data)[0]
        current_price = df['close'].iloc[-1]
        
        return current_price, prediction
    
    def predict_future(self, symbol, df, days=7):
        """Predict future prices for multiple days"""
        if symbol not in self.models:
            return None, None
        
        # For multi-day prediction, we'll use a simple approach
        # In a real application, you might want to use a more sophisticated method
        current_price, next_day_pred = self.predict(symbol, df, 1)
        
        if current_price is None:
            return None, None
        
        # Generate simple projections
        price_change_per_day = (next_day_pred - current_price) / current_price
        predictions = []
        
        for day in range(1, days + 1):
            projected_price = current_price * (1 + price_change_per_day * day)
            predictions.append(projected_price)
        
        return current_price, predictions

def main():
    # Example usage
    predictor = CryptoPredictor()
    
    # Load some data for prediction
    symbol = "BTCUSDT"
    processed_path = f"data/processed/processed_{symbol}.csv"
    
    try:
        df = pd.read_csv(processed_path)
        current_price, predictions = predictor.predict_future(symbol, df, days=7)
        
        if current_price is not None:
            print(f"Current price: {current_price:.2f}")
            for i, pred in enumerate(predictions, 1):
                print(f"Day +{i}: {pred:.2f}")
        else:
            print("Prediction failed")
            
    except FileNotFoundError:
        print("Processed data not found. Run feature engineering first.")

if __name__ == "__main__":
    main()