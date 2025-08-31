# 📈 Crypto Price Prediction Project

## 🚀 Overview
A machine learning web application that predicts cryptocurrency prices using historical data and Random Forest regression. The system provides both CLI tools for data processing and a web interface for interactive predictions.

## 🛠️ Tech Stack
- **Backend**: Python, Flask, Scikit-learn, Pandas, Joblib
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **ML Model**: Random Forest Regressor
- **Data Processing**: Pandas for feature engineering
- **Visualization**: Chart.js (ready for integration)

## 📋 Project Structure
```bash
Crypto-Forecasting/
├── app.py                 # Flask web server
├── preprocess.py          # Data preprocessing script
├── train.py              # Model training script
├── predict.py            # Prediction script
├── data/
│   ├── top_100_cryptos_with_correct_network.csv
│   └── processed_*.csv
├── model/
│   ├── *_rf.joblib       # Trained models
│   └── *_metrics.json    # Model performance metrics
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── requirements.txt       # Dependencies
```
# 📊 Model Details

**Algorithm**: Random Forest Regressor (150 estimators)

**Features**: Lag prices, rolling means/STD, returns

**Metrics**: MAE, RMSE tracked per model

**Validation**: Time-based train-test split (80-20)

