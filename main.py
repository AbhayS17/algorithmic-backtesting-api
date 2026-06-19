# main.py
from fastapi import FastAPI
from routers import backtest

app = FastAPI()

# This plugs your entire math engine into the main server
app.include_router(backtest.router)

@app.get("/")
def read_root():
    return {"message": "Quant Backtesting Engine Online."}
