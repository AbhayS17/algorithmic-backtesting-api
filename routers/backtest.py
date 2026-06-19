# routers/backtest.py
from fastapi import APIRouter, Query
import yfinance as yf
import pandas as pd
from database import get_db_connection
from schemas import BacktestResult

# Create the mini-app
router = APIRouter()

# Notice it says @router.get now, instead of @app.get!
@router.get("/backtest")
def run_backtest(ticker: str = "AAPL", short_window: int = Query(20, ge=5, le=50), long_window: int = Query(50, ge=40, le=200)):
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    if df.empty:
        return {"error": "No data found"}
        
    df["Short_SMA"] = df["Close"].rolling(window=short_window).mean()
    df["Long_SMA"] = df["Close"].rolling(window=long_window).mean()
    df = df.dropna(subset=["Short_SMA", "Long_SMA"]).copy()
    
    df["Signal"] = 0
    df.loc[df["Short_SMA"] > df["Long_SMA"], "Signal"] = 1
    
    df["Market_Return"] = df["Close"].pct_change()
    df["Strategy_Return"] = df["Signal"].shift(1) * df["Market_Return"]
    
    cum_market = round(((1 + df["Market_Return"].dropna()).prod() - 1) * 100, 2)
    cum_strategy = round(((1 + df["Strategy_Return"].dropna()).prod() - 1) * 100, 2)
    
    # Grab the database connection from our other file
    conn, cursor = get_db_connection()
    
    cursor.execute("""
        INSERT INTO backtest_results (ticker, short_window, long_window, market_return, strategy_return)
        VALUES (?, ?, ?, ?, ?)
    """, (ticker.upper(), short_window, long_window, cum_market, cum_strategy))
    conn.commit()
    
    return {
        "status": "Calculated and Saved",
        "ticker": ticker.upper(),
        "metrics": {"market_return_pct": cum_market, "strategy_return_pct": cum_strategy}
    }

@router.get("/results")
def get_saved_results():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT * FROM backtest_results")
    raw_data = cursor.fetchall()
    
    formatted_results = [{"id": r[0], "ticker": r[1], "short_window": r[2], "long_window": r[3], "market_return": r[4], "strategy_return": r[5]} for r in raw_data]
    return {"history": formatted_results}