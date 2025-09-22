import pandas as pd
import numpy as np
import joblib
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import os
import json
import yaml
from datetime import datetime

class CryptoTrainer:
    def __init__(self):
        # Load configuration
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.models = {}
        self.metrics = {}
        
    def prepare_data(self, symbol):
        """Prepare data for training for a specific symbol"""
        processed_path = f"{self.config['data']['processed_dir']}/processed_{symbol}.csv"
        
        try:
            df = pd.read_csv(processed_path)
        except FileNotFoundError:
            print(f"Processed data not found for {symbol}. Run feature engineering first.")
            return None, None, None
        
        # Filter features and target
        exclude_cols = ['target', 'open_time', 'close_time', 'symbol', 'ignore']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols]
        y = df['target']
        
        return X, y, feature_cols
    
    def train_model(self, symbol, test_size=0.2):
        """Train model for a specific symbol"""
        X, y, feature_cols = self.prepare_data(symbol)
        
        if X is None:
            return None, None
        
        # Time-based split
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Train LightGBM model
        model = lgb.LGBMRegressor(
            n_estimators=200,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'test_size': len(X_test),
            'train_size': len(X_train),
            'last_trained': datetime.now().isoformat()
        }
        
        return model, metrics
    
    def train_all_models(self):
        """Train models for all supported symbols"""
        for symbol in self.config['model']['supported_symbols']:
            print(f"Training model for {symbol}...")
            
            # Check if processed data exists
            processed_path = f"{self.config['data']['processed_dir']}/processed_{symbol}.csv"
            if not os.path.exists(processed_path):
                print(f"Skipping {symbol} - no processed data found")
                continue
                
            model, metrics = self.train_model(symbol)
            
            if model is not None:
                self.models[symbol] = model
                self.metrics[symbol] = metrics
                print(f"✅ {symbol} trained - MAE: {metrics['mae']:.4f}, RMSE: {metrics['rmse']:.4f}, MAPE: {metrics['mape']:.2f}%")
            else:
                print(f"❌ Failed to train model for {symbol}")
        
        return self.models, self.metrics
    
    def save_models(self):
        """Save trained models and metrics"""
        os.makedirs(self.config['model']['model_dir'], exist_ok=True)
        
        # Save models
        for symbol, model in self.models.items():
            joblib.dump(model, f"{self.config['model']['model_dir']}/{symbol}_model.joblib")
        
        # Save metrics
        with open(f"{self.config['model']['model_dir']}/model_metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=4)
        
        # Save feature columns for prediction
        # Get feature columns from first symbol
        if self.models:
            first_symbol = list(self.models.keys())[0]
            X, y, feature_cols = self.prepare_data(first_symbol)
            with open(f"{self.config['model']['model_dir']}/feature_columns.json", "w") as f:
                json.dump(feature_cols, f, indent=4)
        
        print("Models and metrics saved successfully!")
    
    def plot_predictions(self, symbol, save_dir="models/evaluation"):
        """Plot predictions vs actual values for a symbol"""
        X, y, feature_cols = self.prepare_data(symbol)
        
        if X is None or symbol not in self.models:
            return
        
        # Time-based split (same as training)
        test_size = 0.2
        split_idx = int(len(X) * (1 - test_size))
        X_test = X.iloc[split_idx:]
        y_test = y.iloc[split_idx:]
        
        y_pred = self.models[symbol].predict(X_test)
        
        os.makedirs(save_dir, exist_ok=True)
        
        plt.figure(figsize=(12, 6))
        plt.plot(y_test.values, label='Actual')
        plt.plot(y_pred, label='Predicted', alpha=0.7)
        plt.title(f"{symbol} Price Prediction")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plt.savefig(f"{save_dir}/{symbol}_prediction.png")
        plt.close()

def main():
    trainer = CryptoTrainer()
    models, metrics = trainer.train_all_models()
    trainer.save_models()
    
    # Plot predictions for each symbol
    for symbol in models.keys():
        trainer.plot_predictions(symbol)

if __name__ == "__main__":
    main()