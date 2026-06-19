# schemas.py
from pydantic import BaseModel

class BacktestResult(BaseModel):
    ticker: str
    short_window: int
    long_window: int
    market_return: float
    strategy_return: float