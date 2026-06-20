import yfinance as yf
import pandas as pd

class MarketDataEngine:
    def __init__(self, tickers: list[str], start_date: str, end_date: str):
        # Clean the inputs automatically when the object is created
        self.tickers = [t.upper() for t in tickers]
        self.start_date = start_date
        self.end_date = end_date
        self.portfolio_data = {}

    def fetch_data(self) -> dict:
        """Downloads and formats data for all tickers in a single batch request."""
        
        # 1. Batch Download: Fetches all stocks at once. 
        # Much faster and avoids API rate limits.
        raw_data = yf.download(self.tickers, start=self.start_date, end=self.end_date)

        if raw_data.empty:
            raise ValueError("No data found for the provided tickers and dates.")

        # 2. Standardize the Output
        # yfinance returns a flat table for 1 stock, but a complex MultiIndex 
        # table (a table inside a table) if you ask for multiple stocks.
        if len(self.tickers) == 1:
            ticker = self.tickers[0]
            self.portfolio_data[ticker] = self._clean_dataframe(raw_data)
        else:
            for ticker in self.tickers:
                # .xs() is a Pandas "Cross-Section" tool. 
                # It slices through the 3D table to pull out just one stock's 2D table.
                single_stock_df = raw_data.xs(ticker, axis=1, level=1)
                self.portfolio_data[ticker] = self._clean_dataframe(single_stock_df)

        return self.portfolio_data

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Private method to clean data to Quantitative Finance standards."""
        # Remove days where the market was completely closed (e.g., weekends)
        df = df.dropna(how='all')
        
        # Forward Fill (ffill): If a stock was halted on a Wednesday, don't leave it blank (NaN).
        # Assume the price is exactly the same as Tuesday's closing price.
        df = df.ffill() 
        
        return df