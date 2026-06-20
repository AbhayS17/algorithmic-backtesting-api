import streamlit as st
import requests
from datetime import date, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Pro Quant Backtester", layout="wide")
st.title("⚡ Algorithmic Portfolio Backtester")
st.markdown("Execute multi-asset technical strategies against a high-performance FastAPI engine.")

# 2. The Sidebar (For clean, professional controls)
with st.sidebar:
    st.header("⚙️ Portfolio Setup")
    # Allow the user to type multiple tickers
    tickers_input = st.text_input("Tickers (comma-separated)", "AAPL, MSFT, TSLA")
    
    # Date pickers for custom ranges (defaults to 1 year ago)
    start_date = st.date_input("Start Date", date.today() - timedelta(days=365))
    end_date = st.date_input("End Date", date.today())
    
    st.header("🧠 Strategy Engine")
    # The Select Box that changes the UI
    strategy = st.selectbox("Select Algorithm", ["SMA", "MACD", "HOLD"])
    
    # 3. Dynamic UI based on the chosen strategy
    params = {}
    if strategy == "SMA":
        st.subheader("SMA Parameters")
        short_w = st.slider("Short Window", 5, 50, 20)
        long_w = st.slider("Long Window", 40, 200, 50)
        params = {"short_window": short_w, "long_window": long_w}
        
    elif strategy == "MACD":
        st.subheader("MACD Parameters")
        fast = st.slider("Fast Period", 5, 20, 12)
        slow = st.slider("Slow Period", 20, 40, 26)
        sig = st.slider("Signal Period", 5, 15, 9)
        params = {"fast": fast, "slow": slow, "signal": sig}
        
    run_btn = st.button("Execute Backtest", type="primary", use_container_width=True)

# 4. The Execution Logic
if run_btn:
    # Clean up the user's ticker string into a neat Python list
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    
    # Construct the JSON payload for our POST request
    payload = {
        "tickers": tickers,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "strategy_name": strategy,
        "params": params
    }
    
    with st.spinner("Connecting to Quantitative Engine..."):
        try:
            # Send the POST request across the bridge to FastAPI
            response = requests.post("http://127.0.0.1:8000/run", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"Execution Complete: Evaluated {data['date_range']}")
                
                st.subheader("📊 Portfolio Results")
                results = data["portfolio_results"]
                
                # Dynamically create visual columns based on how many tickers the user tested
                cols = st.columns(len(results))
                for idx, (ticker, metrics) in enumerate(results.items()):
                    with cols[idx]:
                        # Streamlit visual metric cards
                        st.markdown(f"### {ticker}")
                        st.metric("Market Return (Hold)", f"{metrics['market_return_pct']}%")
                        
                        # Add some visual color to the strategy return
                        strat_ret = metrics['strategy_return_pct']
                        color = "normal" if strat_ret > 0 else "inverse"
                        st.metric("Strategy Return", f"{strat_ret}%", delta_color=color)
            else:
                st.error(f"Engine Error: {response.json().get('detail', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            st.error("🚨 Connection failed. Is the FastAPI backend running in Terminal 1?")