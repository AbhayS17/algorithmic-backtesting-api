import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Pro Quant Platform", layout="wide")
st.title("⚡ Quantitative Alpha Platform")
st.markdown("Execute algorithmic backtests and optimize portfolio allocations via the FastAPI engine.")

# 2. The Sidebar
with st.sidebar:
    st.header("⚙️ Portfolio Setup")
    tickers_input = st.text_input("Tickers (comma-separated)", "AAPL, MSFT, JNJ")
    
    start_date = st.date_input("Start Date", date.today() - timedelta(days=365))
    end_date = st.date_input("End Date", date.today())
    
    st.header("🧠 Engine Mode")
    # Added "OPTIMIZE" as a completely new mode
    mode = st.selectbox("Select Engine Mode", ["OPTIMIZE", "SMA", "MACD", "HOLD"])
    
    # 3. Dynamic UI Controls
    params = {}
    if mode == "SMA":
        st.subheader("SMA Parameters")
        params = {"short_window": st.slider("Short Window", 5, 50, 20), "long_window": st.slider("Long Window", 40, 200, 50)}
    elif mode == "MACD":
        st.subheader("MACD Parameters")
        params = {"fast": st.slider("Fast", 5, 20, 12), "slow": st.slider("Slow", 20, 40, 26), "signal": st.slider("Signal", 5, 15, 9)}
    elif mode == "OPTIMIZE":
        st.info("Uses Markowitz Efficient Frontier to maximize Sharpe Ratio.")
        
    run_btn = st.button("Execute", type="primary", use_container_width=True)

# 4. The Execution Logic
if run_btn:
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    
    # --- MODE 1: PORTFOLIO OPTIMIZATION ---
    if mode == "OPTIMIZE":
        payload = {"tickers": tickers, "start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")}
        
        with st.spinner("Running SLSQP Optimizer..."):
            response = requests.post("http://127.0.0.1:8000/optimize", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                metrics = data["optimization_metrics"]
                
                st.success("Optimization Complete!")
                
                # Render Top-Level Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Expected Annual Return", f"{metrics['expected_annual_return_pct']}%")
                col2.metric("Annual Volatility (Risk)", f"{metrics['expected_annual_volatility_pct']}%")
                col3.metric("Sharpe Ratio", metrics['sharpe_ratio'])
                
                st.subheader("⚖️ Optimal Capital Allocation")
                
                # Streamlit Magic: Turn the JSON dictionary into a visual bar chart instantly
                weights_df = pd.DataFrame.from_dict(metrics['optimal_weights'], orient='index', columns=['Weight (%)'])
                st.bar_chart(weights_df)
            else:
                st.error(f"Error: {response.text}")

    # --- MODE 2: STRATEGY BACKTESTING ---
    else:
        payload = {"tickers": tickers, "start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d"), "strategy_name": mode, "params": params}
        
        with st.spinner(f"Running {mode} Backtest..."):
            response = requests.post("http://127.0.0.1:8000/run", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"Backtest Complete: {data['date_range']}")
                
                results = data["portfolio_results"]
                cols = st.columns(len(results))
                for idx, (ticker, metric) in enumerate(results.items()):
                    with cols[idx]:
                        st.markdown(f"### {ticker}")
                        st.metric("Market Return", f"{metric['market_return_pct']}%")
                        color = "normal" if metric['strategy_return_pct'] > 0 else "inverse"
                        st.metric("Strategy Return", f"{metric['strategy_return_pct']}%", delta_color=color)
            else:
                st.error(f"Error: {response.text}")