from abc import ABC, abstractmethod
import pandas as pd
from ta.trend import MACD

# --- THE CONTRACT (BASE CLASS) ---
class BaseStrategy(ABC):
    """
    This is the blueprint. It doesn't do any math itself. 
    It just forces every child strategy to follow the rules.
    """
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        pass


# --- SPECIFIC STRATEGIES (CHILD CLASSES) ---

class SMACrossoverStrategy(BaseStrategy):
    """
    This class inherits from BaseStrategy. It MUST contain a generate_signals function,
    otherwise Python will throw an error before the server even starts.
    """
    def generate_signals(self, df: pd.DataFrame, short_window: int = 20, long_window: int = 50, **kwargs) -> pd.DataFrame:
        # We work on a copy to avoid altering the original downloaded data
        data = df.copy() 
        
        # The exact vectorized math we wrote earlier!
        data['Short_SMA'] = data['Close'].rolling(window=short_window).mean()
        data['Long_SMA'] = data['Close'].rolling(window=long_window).mean()
        
        data['Signal'] = 0
        data.loc[data['Short_SMA'] > data['Long_SMA'], 'Signal'] = 1
        
        return data

class BuyAndHoldStrategy(BaseStrategy):
    """
    A baseline strategy to compare our algorithm against. 
    It just buys on day 1 and holds forever.
    """
    def generate_signals(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        data = df.copy()
        data['Signal'] = 1 # Always holding the stock
        return data
    
class MACDStrategy(BaseStrategy):
    """
    Moving Average Convergence Divergence using the stable 'ta' library.
    """
    def generate_signals(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, **kwargs) -> pd.DataFrame:
        data = df.copy()
        
        # 1. Initialize the MACD object
        macd_indicator = MACD(close=data['Close'], window_fast=fast, window_slow=slow, window_sign=signal)
        
        # 2. Extract the math into our dataframe
        data['MACD_Line'] = macd_indicator.macd()
        data['Signal_Line'] = macd_indicator.macd_signal()
        
        # 3. Generate Signal: Buy when MACD > Signal Line
        data['Signal'] = 0
        data.loc[data['MACD_Line'] > data['Signal_Line'], 'Signal'] = 1
        
        return data