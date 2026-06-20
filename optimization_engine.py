import numpy as np
import pandas as pd
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, portfolio_data: dict, risk_free_rate: float = 0.02):
        """
        Takes the raw dictionary of dataframes from MarketDataEngine
        """
        self.portfolio_data = portfolio_data
        self.risk_free_rate = risk_free_rate
        self.tickers = list(portfolio_data.keys())
        self.num_assets = len(self.tickers)

    def _get_daily_returns(self) -> pd.DataFrame:
        """Extracts the 'Close' prices and calculates daily percentage returns."""
        close_prices = pd.DataFrame()
        for ticker, df in self.portfolio_data.items():
            close_prices[ticker] = df['Close']
            
        # Drop the first row since pct_change leaves a NaN
        return close_prices.pct_change().dropna()

    def optimize_sharpe_ratio(self) -> dict:
        """Runs the SciPy SLSQP minimizer to find the optimal portfolio weights."""
        returns = self._get_daily_returns()
        
        # 1. Calculate Expected Returns and Covariance Matrix (Annualized)
        # 252 is the standard number of trading days in a year
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252

        # 2. Define the Objective Function (The thing we want to minimize)
        # SciPy only minimizes. To MAXIMIZE the Sharpe Ratio, we MINIMIZE the negative Sharpe Ratio.
        def negative_sharpe(weights):
            p_ret = np.sum(mean_returns * weights)
            p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -(p_ret - self.risk_free_rate) / p_vol

        # 3. Define Constraints and Bounds
        # Constraint: All weights must sum to exactly 1.0 (100%)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # Bound: No short-selling. Every asset weight must be between 0.0 and 1.0
        bounds = tuple((0.0, 1.0) for _ in range(self.num_assets))
        
        # Initial Guess: Equal weighting (e.g., 33% for 3 assets)
        init_guess = self.num_assets * [1. / self.num_assets]

        # 4. The SciPy Optimization Engine
        # SLSQP = Sequential Least Squares Programming
        optimal_result = minimize(
            negative_sharpe, 
            init_guess, 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints
        )

        # 5. Package the Results
        optimal_weights = optimal_result.x
        expected_return = np.sum(mean_returns * optimal_weights)
        expected_volatility = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        sharpe_ratio = (expected_return - self.risk_free_rate) / expected_volatility

        # Create a clean dictionary mapping tickers to their percentage weights
        weight_dict = {self.tickers[i]: round(optimal_weights[i] * 100, 2) for i in range(self.num_assets)}

        return {
            "optimal_weights": weight_dict,
            "expected_annual_return_pct": round(expected_return * 100, 2),
            "expected_annual_volatility_pct": round(expected_volatility * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2)
        }