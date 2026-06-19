# Algorithmic Backtesting Engine API

A high-performance, RESTful API backend built to fetch live market data, execute vectorized technical indicator strategies, and persist performance metrics.

## System Architecture
This project implements a modular, scalable architecture with a strict separation of concerns:
* **Framework:** FastAPI for high-speed, asynchronous request routing.
* **Math Engine:** Pandas and NumPy for zero-loop, vectorized moving average calculations.
* **Data Integration:** `yfinance` for automated historical market data ingestion.
* **Persistence:** SQLite for local state management and permanent metric storage.
* **Validation:** Pydantic models to ensure strict data integrity on all endpoints.

## Core Features
1. **Dynamic Backtesting:** Users can submit query parameters to test custom SMA (Simple Moving Average) crossover strategies across various equities.
2. **Automated Data Processing:** The engine handles NaN dropping, index resetting, and dictionary serialization autonomously.
3. **Automated Persistence:** The API calculates cumulative market vs. strategy returns and automatically logs the experiment to a relational database.

## API Endpoints
* `GET /backtest?ticker=AAPL&short_window=20&long_window=50` : Executes a fresh backtest and saves results.
* `GET /results` : Retrieves all historical backtest experiments from the database.

## Local Setup
1. Clone the repository: `git clone <your-repo-link>`
2. Install dependencies: `pip install fastapi uvicorn yfinance pandas pydantic`
3. Run the server: `uvicorn main:app --reload`
4. Access the interactive testing dashboard at `http://127.0.0.1:8000/docs`