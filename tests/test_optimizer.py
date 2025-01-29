import unittest
import numpy as np
from portfolio_optimizer.optimizer import PortfolioOptimizer

class TestPortfolioOptimizer(unittest.TestCase):
    def setUp(self):
        self.assets = ["AAPL", "GOOG", "TSLA"]
        self.returns = [0.12, 0.15, 0.18]  # Expected returns
        self.cov_matrix = np.array([
            [0.1, 0.03, 0.05],
            [0.03, 0.08, 0.04],
            [0.05, 0.04, 0.09]
        ])
        self.optimizer = PortfolioOptimizer(self.assets, self.returns, self.cov_matrix)

    def test_sharpe_ratio(self):
        weights = np.array([0.4, 0.3, 0.3])  # Example weights
        sharpe = self.optimizer.calculate_sharpe_ratio(weights)
        self.assertGreater(sharpe, 0)  # Sharpe ratio should be positive

if __name__ == "__main__":
    unittest.main()