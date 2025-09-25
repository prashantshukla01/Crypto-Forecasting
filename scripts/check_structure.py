import os

def check_project_structure():
    expected_dirs = [
        'data/raw',
        'data/processed', 
        'data/external',
        'src/data_processing',
        'src/modeling',
        'src/app/static',
        'src/app/templates',
        'src/utils',
        'config',
        'models'
    ]
    
    print("📁 Checking project structure...")
    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - creating...")
            os.makedirs(dir_path, exist_ok=True)
    
    # Check essential files
    essential_files = [
        'config/config.yaml',
        'requirements.txt',
        'src/app/app.py',
        'src/app/templates/index.html'
    ]
    
    print("\n📄 Checking essential files...")
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")

if __name__ == "__main__":
    check_project_structure()