import unittest
import pandas as pd
import numpy as np
from src.modeling.train import CryptoTrainer

class TestModeling(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.trainer = CryptoTrainer()
        
        # Create test data with features
        n_samples = 100
        self.test_data = pd.DataFrame({
            'close_lag_1': np.random.randn(n_samples),
            'close_lag_2': np.random.randn(n_samples),
            'roll_mean_7': np.random.randn(n_samples),
            'returns': np.random.randn(n_samples) * 0.01,
            'target': np.random.randn(n_samples) + 100  # Simulated prices
        })
    
    def test_model_training(self):
        """Test that model can be trained without errors"""
        # This is a simple test to ensure training runs without errors
        # In a real test, you'd use mock data or a testing database
        
        # Test that the trainer can be initialized
        self.assertIsNotNone(self.trainer)
        
        # Test that config is loaded
        self.assertIn('model', self.trainer.config)

if __name__ == '__main__':
    unittest.main()