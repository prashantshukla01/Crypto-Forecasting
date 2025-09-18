from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import joblib
from datetime import datetime, timedelta
import json

app = Flask(__name__)


# Load available symbols from your data
def get_available_symbols():
    data_path = os.path.join("data", "top_100_cryptos_with_correct_network.csv")
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        return sorted(df['symbol'].unique().tolist())
    return ["BTCUSDT", "ETHUSDT", "ADAUSDT"]  # fallback


@app.route('/')
def index():
    symbols = get_available_symbols()
    return render_template('index.html', symbols=symbols)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        symbol = request.form.get('symbol')
        days = int(request.form.get('days', 1))

        # Validate inputs
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400

        if days < 1 or days > 7:
            return jsonify({'error': 'Days must be between 1 and 7'}), 400

        # Check if model exists
        model_path = os.path.join("model", f"{symbol}_rf.joblib")
        if not os.path.exists(model_path):
            return jsonify({'error': f'Model not available for {symbol}'}), 404

        # Load data and make prediction
        processed_path = os.path.join("data", f"processed_{symbol}.csv")
        if not os.path.exists(processed_path):
            return jsonify({'error': f'Processed data not found for {symbol}'}), 404

        df = pd.read_csv(processed_path)
        feature_cols = [c for c in df.columns if c.startswith("lag_") or c.startswith("roll_") or c.startswith("ret_")]

        model = joblib.load(model_path)
        latest_data = df.iloc[-days:][feature_cols]
        preds = model.predict(latest_data)

        # Generate dates for predictions
        last_date = pd.to_datetime(df['date'].iloc[-1])
        prediction_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]

        # Format response
        predictions = []
        for i, (date, pred) in enumerate(zip(prediction_dates, preds), 1):
            predictions.append({
                'day': f"Day +{i}",
                'date': date.strftime('%Y-%m-%d'),
                'price': round(float(pred), 2)
            })

        # Get current price for comparison
        current_price = round(float(df['close'].iloc[-1]), 2)

        return jsonify({
            'symbol': symbol,
            'current_price': current_price,
            'predictions': predictions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)