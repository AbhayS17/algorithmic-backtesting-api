# routers/backtest.py
from fastapi import APIRouter, Query
import yfinance as yf
import pandas as pd
from database import get_db_connection
from schemas import BacktestResult
from optimization_engine import PortfolioOptimizer

# Create the mini-app
router = APIRouter()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from data_engine import MarketDataEngine
from strategy_engine import SMACrossoverStrategy, BuyAndHoldStrategy, MACDStrategy

router = APIRouter()

# --- 1. The Strategy Factory (The Switchboard) ---
# This maps a string name to the actual Python Class Object
STRATEGY_MAP = {
    "SMA": SMACrossoverStrategy(),
    "HOLD": BuyAndHoldStrategy(),
    "MACD": MACDStrategy()
}

# --- 2. The Dynamic Request Blueprint ---
class BacktestRequest(BaseModel):
    tickers: list[str]
    start_date: str
    end_date: str
    strategy_name: str
    # 'params' allows the user to send ANY custom variables (like short_window or fast_macd)
    params: dict = {} 

# --- 3. The Master POST Endpoint ---
@router.post("/run")
def run_portfolio_backtest(request: BacktestRequest):
    
    # 1. Select the correct algorithm brain
    if request.strategy_name not in STRATEGY_MAP:
        raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy_name}' not found.")
    
    strategy = STRATEGY_MAP[request.strategy_name]

    # 2. Fetch the clean data using our new Engine
    try:
        data_engine = MarketDataEngine(request.tickers, request.start_date, request.end_date)
        portfolio_data = data_engine.fetch_data()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data fetching error: {str(e)}")

    # 3. Process the portfolio
    portfolio_results = {}
    
    for ticker, df in portfolio_data.items():
        # Pass the user's custom dictionary directly into the strategy's **kwargs!
        signaled_df = strategy.generate_signals(df, **request.params)

        # Calculate Returns
        signaled_df['Market_Return'] = signaled_df['Close'].pct_change()
        signaled_df['Strategy_Return'] = signaled_df['Signal'].shift(1) * signaled_df['Market_Return']

        cum_market = round(((1 + signaled_df['Market_Return'].dropna()).prod() - 1) * 100, 2)
        cum_strategy = round(((1 + signaled_df['Strategy_Return'].dropna()).prod() - 1) * 100, 2)

        portfolio_results[ticker] = {
            "market_return_pct": cum_market,
            "strategy_return_pct": cum_strategy
        }

    # Return the aggregated report
    return {
        "status": "Success",
        "strategy_executed": request.strategy_name,
        "date_range": f"{request.start_date} to {request.end_date}",
        "portfolio_results": portfolio_results
    }

@router.get("/results")
def get_saved_results():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT * FROM backtest_results")
    raw_data = cursor.fetchall()
    
    formatted_results = [{"id": r[0], "ticker": r[1], "short_window": r[2], "long_window": r[3], "market_return": r[4], "strategy_return": r[5]} for r in raw_data]
    return {"history": formatted_results}

# Create a new Pydantic blueprint for the optimization request
class OptimizationRequest(BaseModel):
    tickers: list[str]
    start_date: str
    end_date: str

# The new API Endpoint
@router.post("/optimize")
def run_portfolio_optimization(request: OptimizationRequest):
    try:
        # 1. Fetch the data using our existing engine
        data_engine = MarketDataEngine(request.tickers, request.start_date, request.end_date)
        portfolio_data = data_engine.fetch_data()
        
        # 2. Run the optimization engine
        optimizer = PortfolioOptimizer(portfolio_data)
        optimal_results = optimizer.optimize_sharpe_ratio()
        
        return {
            "status": "Success",
            "date_range": f"{request.start_date} to {request.end_date}",
            "optimization_metrics": optimal_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Optimization failed: {str(e)}")