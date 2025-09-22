import os
import sys
import json
import yaml
from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_processing.data_collector import CryptoDataCollector
from src.data_processing.feature_engineering import FeatureEngineer
from src.modeling.predict import CryptoPredictor

app = Flask(__name__)

# Load configuration
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize predictor
predictor = CryptoPredictor()

@app.route('/')
def index():
    return render_template('index.html', symbols=config['model']['supported_symbols'])

@app.route('/predict', methods=['POST'])
def predict():
    try:
        symbol = request.form.get('symbol')
        days = int(request.form.get('days', 1))
        
        if symbol not in config['model']['supported_symbols']:
            return jsonify({'error': f'Symbol {symbol} not supported'}), 400
            
        if symbol not in predictor.models:
            return jsonify({'error': f'No model available for {symbol}'}), 404
            
        if days < 1 or days > 7:
            return jsonify({'error': 'Days must be between 1 and 7'}), 400
        
        # Try to load processed data
        processed_path = f"{config['data']['processed_dir']}/processed_{symbol}.csv"
        try:
            df = pd.read_csv(processed_path)
        except FileNotFoundError:
            return jsonify({'error': f'No data found for {symbol}. Please run data processing first.'}), 404
        
        if df.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Make prediction
        current_price, predictions = predictor.predict_future(symbol, df, days)
        
        if current_price is None:
            return jsonify({'error': 'Prediction failed'}), 500
        
        # Generate prediction dates
        last_date = pd.to_datetime(df['open_time'].iloc[-1])
        prediction_dates = [last_date + timedelta(days=i) for i in range(1, days+1)]
        
        # Format response
        prediction_results = []
        for i, (date, price) in enumerate(zip(prediction_dates, predictions), 1):
            prediction_results.append({
                'day': f"Day +{i}",
                'date': date.strftime('%Y-%m-%d'),
                'price': round(float(price), 2)
            })
        
        # Load model metrics if available
        metrics = {}
        try:
            with open(f"{config['model']['model_dir']}/model_metrics.json", "r") as f:
                all_metrics = json.load(f)
                metrics = all_metrics.get(symbol, {})
        except FileNotFoundError:
            pass
        
        return jsonify({
            'symbol': symbol,
            'current_price': round(float(current_price), 2),
            'predictions': prediction_results,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/symbols', methods=['GET'])
def get_symbols():
    return jsonify({'symbols': config['model']['supported_symbols']})

@app.route('/model_info', methods=['GET'])
def model_info():
    symbol = request.args.get('symbol')
    if symbol and symbol in predictor.models:
        try:
            with open(f"{config['model']['model_dir']}/model_metrics.json", "r") as f:
                metrics = json.load(f)
                return jsonify(metrics.get(symbol, {}))
        except FileNotFoundError:
            return jsonify({'info': 'Model loaded but metrics not available'})
    return jsonify({'error': 'Model not found'}), 404

@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        collector = CryptoDataCollector()
        data = collector.get_combined_data()
        
        if not data.empty:
            collector.save_data(data)
            
            # Process data for all symbols
            engineer = FeatureEngineer()
            symbols = data['symbol'].unique()
            
            for symbol in symbols:
                if symbol in config['model']['supported_symbols']:
                    symbol_df = data[data['symbol'] == symbol]
                    processed_df = engineer.create_features(symbol_df)
                    engineer.save_processed_data(processed_df, symbol)
            
            return jsonify({'message': f'Data updated successfully. Processed {len(data)} records.'})
        else:
            return jsonify({'error': 'No data was collected'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host=config['api']['host'],
        port=config['api']['port'],
        debug=config['api']['debug']
    )