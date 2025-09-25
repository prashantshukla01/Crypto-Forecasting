import unittest
import pandas as pd
import os
from src.data_processing.feature_engineering import FeatureEngineer

class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.engineer = FeatureEngineer()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'symbol': ['BTCUSDT'] * 10,
            'open_time': pd.date_range('2023-01-01', periods=10),
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        })
    
    def test_feature_engineering(self):
        """Test that feature engineering creates expected features"""
        processed_data = self.engineer.create_features(self.test_data)
        
        # Check that features were created
        self.assertIn('returns', processed_data.columns)
        self.assertIn('close_lag_1', processed_data.columns)
        self.assertIn('roll_mean_7', processed_data.columns)
        self.assertIn('target', processed_data.columns)
        
        # Check that NaN values are handled
        self.assertFalse(processed_data.isnull().values.any())

if __name__ == '__main__':
    unittest.main()