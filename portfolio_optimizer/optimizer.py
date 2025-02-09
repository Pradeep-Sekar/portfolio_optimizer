import numpy as np
import yfinance as yf

class PortfolioOptimizer:
    def __init__(self, assets, returns, cov_matrix, risk_free_rate=0.02):
        self.assets = assets
        self.returns = np.array(returns)
        self.cov_matrix = np.array(cov_matrix)
        self.risk_free_rate = risk_free_rate

    def get_live_prices(self):
        """
        Fetches real-time stock prices for all assets in the portfolio.
        :return: Dictionary with asset tickers as keys and latest Close prices as values.
        """
        prices = {}
        for ticker in self.assets:
            try:
                stock = yf.Ticker(ticker)
                prices[ticker] = stock.history(period="1d")["Close"].iloc[-1]
            except Exception as e:
                print(f"Error fetching price for {ticker}: {e}")
                prices[ticker] = None  # Mark missing prices
        return prices

    def calculate_portfolio_value(self, holdings):
        """
        Computes the total value of the portfolio based on live prices.
        :param holdings: Dictionary mapping asset tickers to (quantity, purchase_price).
        :return: Portfolio total value and individual asset values.
        """
        live_prices = self.get_live_prices()
        portfolio_value = 0
        asset_values = {}

        for ticker, (quantity, purchase_price) in holdings.items():
            if live_prices[ticker] is not None:
                current_value = quantity * live_prices[ticker]
                asset_values[ticker] = {
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "current_price": live_prices[ticker],
                    "current_value": current_value,
                    "profit_loss": current_value - (quantity * purchase_price),
                    "percentage_change": ((current_value - (quantity * purchase_price)) / (quantity * purchase_price)) * 100
                }
                portfolio_value += current_value
            else:
                asset_values[ticker] = {
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "current_price": "N/A",
                    "current_value": "N/A",
                    "profit_loss": "N/A",
                    "percentage_change": "N/A"
                }

        return portfolio_value, asset_values

    def calculate_sharpe_ratio(self, weights):
        """
        Calculate the Sharpe Ratio given a set of portfolio weights.
        :param weights: Asset allocation weights.
        :return: Sharpe Ratio value.
        """
        portfolio_return = np.dot(weights, self.returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        return sharpe_ratio

    def optimize(self):
        """
        Placeholder for future optimization logic.
        """
        return "Optimization logic to be implemented."
