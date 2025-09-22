import json
import yaml
import pandas as pd
from datetime import datetime, timedelta

def load_config():
    """Load configuration from YAML file"""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def save_config(config):
    """Save configuration to YAML file"""
    with open('config/config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def load_model_metrics():
    """Load model metrics from JSON file"""
    config = load_config()
    try:
        with open(f"{config['model']['model_dir']}/model_metrics.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_available_symbols():
    """Get list of available symbols with trained models"""
    config = load_config()
    available_symbols = []
    
    for symbol in config['model']['supported_symbols']:
        model_path = f"{config['model']['model_dir']}/{symbol}_model.joblib"
        if os.path.exists(model_path):
            available_symbols.append(symbol)
    
    return available_symbols

def format_price(price):
    """Format price with appropriate decimal places"""
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    else:
        return f"${price:.8f}"

def calculate_percentage_change(current, previous):
    """Calculate percentage change between two values"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100