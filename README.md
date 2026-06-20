# Quantitative Alpha Engine & Portfolio Optimizer

A high-performance, full-stack quantitative research platform built to execute vectorized technical algorithmic backtests and perform convex portfolio optimization.

## System Architecture
* **Backend Engine:** FastAPI (Python) routing high-speed, asynchronous network requests.
* **Quantitative Mathematics:** Vectorized Pandas for technical indicator generation; SciPy (`SLSQP` minimization) for Markowitz Efficient Frontier optimization.
* **Data Pipeline:** Custom, object-oriented `MarketDataEngine` handling dynamic multi-asset batch downloading, NaN forward-filling, and cross-sectional data alignment.
* **Frontend Client:** Dynamic Streamlit dashboard featuring robust state management for seamless toggling between algorithmic backtesting and capital allocation modes.

## Core Capabilities
1. **Dynamic Portfolio Optimization:** Calculates the exact fractional asset weights required to maximize the Sharpe Ratio (return per unit of risk) of a multi-asset portfolio using Modern Portfolio Theory.
2. **Object-Oriented Strategy Factory:** Implements the Open-Closed Principle. New trading algorithms (e.g., MACD, SMA Crossover) inherit from an abstract base class, allowing infinite strategy expansion without modifying core API routing.
3. **Multi-Asset Execution:** Backtests technical strategies across custom user-defined portfolios and historical timeframes, generating localized performance metrics versus baseline market hold returns.

## Local Setup
1. Clone the repository and navigate to the root directory.
2. Install dependencies: `pip install "pandas<3" "numpy<2" ta scipy fastapi uvicorn yfinance pydantic streamlit requests`
3. Launch the Backend API (Terminal 1): `uvicorn main:app --reload`
4. Launch the Frontend Client (Terminal 2): `streamlit run frontend.py`