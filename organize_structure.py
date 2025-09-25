import os
import shutil
import glob

def organize_project():
    """Organize the project structure properly"""
    
    # Create necessary directories
    directories = [
        'data/raw',
        'data/processed',
        'data/external',
        'models',
        'config',
        'notebooks',
        'scripts'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Move files to correct locations
    file_movements = [
        # Move config files to config directory
        ('requirements.txt', 'requirements.txt'),  # Keep in root
        ('environment.yml', 'environment.yml'),    # Keep in root
        ('README.md', 'README.md'),                # Keep in root
        
        # Move old scripts to scripts directory
        ('predict.py', 'scripts/legacy_predict.py'),
        ('preprocess.py', 'scripts/legacy_preprocess.py'),
        ('check_structure.py', 'scripts/check_structure.py'),
    ]
    
    for source, destination in file_movements:
        if os.path.exists(source) and source != destination:
            shutil.move(source, destination)
            print(f"📁 Moved {source} → {destination}")
    
    # Create essential missing files
    create_config_file()
    create_requirements_file()
    
    print("\n🎉 Project structure organized successfully!")

def create_config_file():
    """Create config file if missing"""
    config_content = """data:
  raw_path: "data/raw/top_100_cryptos_with_correct_network.csv"
  processed_dir: "data/processed"
  external_dir: "data/external"
  
model:
  model_dir: "models"
  supported_symbols: ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT"]
  
api:
  host: "0.0.0.0"
  port: 5001
  debug: true
  
features:
  lags: [1, 2, 3, 5, 7, 14]
  windows: [7, 14, 30]
  
binance:
  base_url: "https://api.binance.com/api/v3"
  intervals: ["1d"]
"""
    
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write(config_content)
        print("✅ Created config/config.yaml")

def create_requirements_file():
    """Create requirements.txt if missing or incomplete"""
    requirements_content = """flask==2.3.3
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2
python-dotenv==1.0.0
pyyaml==6.0.1
requests==2.31.0
lightgbm==4.1.0
ta==0.10.2
matplotlib==3.7.2
"""
    
    req_path = "requirements.txt"
    if not os.path.exists(req_path):
        with open(req_path, 'w') as f:
            f.write(requirements_content)
        print("✅ Created requirements.txt")

if __name__ == "__main__":
    organize_project()