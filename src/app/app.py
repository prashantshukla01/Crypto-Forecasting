import os
import sys
import json
import pandas as pd
import joblib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

# Fix import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..')
sys.path.append(src_dir)

try:
    from data_processing.data_collector import CryptoDataCollector
    from data_processing.feature_engineering import FeatureEngineer
    from modeling.predict import CryptoPredictor
    import yaml
except ImportError as e:
    print(f"Import warning: {e}")
    # Fallback to simple mode if imports fail

app = Flask(__name__)

# Simple configuration since config file might not be ready
CONFIG = {
    'model': {
        'supported_symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT'],
        'model_dir': 'models'
    },
    'api': {
        'host': '0.0.0.0',
        'port': 5001,
        'debug': True
    }
}

@app.route('/')
def index():
    """Main page"""
    symbols = CONFIG['model']['supported_symbols']
    return render_template('index.html', symbols=symbols)

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint with fallback"""
    try:
        symbol = request.form.get('symbol', 'BTCUSDT')
        days = int(request.form.get('days', 3))
        
        # Simple mock prediction for demo
        current_price = 45000  # Mock BTC price
        
        predictions = []
        for i in range(1, days + 1):
            future_date = datetime.now() + timedelta(days=i)
            # Simple prediction with some randomness
            predicted_price = current_price * (1 + 0.01 * i)  # 1% increase per day
            
            predictions.append({
                'day': f'Day +{i}',
                'date': future_date.strftime('%Y-%m-%d'),
                'price': round(predicted_price, 2)
            })
        
        return jsonify({
            'symbol': symbol,
            'current_price': current_price,
            'predictions': predictions,
            'message': 'Demo mode using mock data'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Crypto Forecasting API is running'})

@app.route('/symbols')
def symbols():
    """Get available symbols"""
    return jsonify({'symbols': CONFIG['model']['supported_symbols']})

if __name__ == '__main__':
    print("🚀 Starting Crypto Forecasting Application...")
    print("📍 Local: http://localhost:5001")
    print("🌐 Network: http://0.0.0.0:5001")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run(
        host=CONFIG['api']['host'],
        port=CONFIG['api']['port'],
        debug=CONFIG['api']['debug']
    )