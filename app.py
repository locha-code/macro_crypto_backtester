import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import InstitutionalBacktester to ensure accurate fees, slippage, and next-open execution
try:
    from src.backtester import InstitutionalBacktester
except ImportError:
    from backtester import InstitutionalBacktester

# Page configuration (Wide Layout)
st.set_page_config(
    page_title="Macro Quant Crypto Backtester",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 Macro-Integrated BTC Quantitative Trading Dashboard")
st.markdown("Visualizing an Institutional Quantitative Trading Strategy driven by Global Liquidity (US M2 Money Supply & Fed Funds Rate).")

# 1. Load data and run institutional backtest
@st.cache_data
def load_and_run_backtest():
    signals_df = pd.read_csv("data/processed/btc_strategy_signals.csv", index_col="Date", parse_dates=True)
    
    # Run InstitutionalBacktester with 0.1% commission, 0.05% slippage, and next-open execution
    backtester = InstitutionalBacktester(initial_capital=10000.0, fee_pct=0.001, slippage_pct=0.0005)
    results = backtester.run_backtest(signals_df)
    
    return signals_df, results

try:
    df, bt_results = load_and_run_backtest()
except Exception as e:
    st.error(f"Error loading dataset or executing backtest: {e}")
    st.stop()

# 2. Extract net equity curves (No Look-Ahead Bias, Fees & Slippage Included)
initial_capital = 10000.0
df['Equity_Strategy'] = bt_results["Equity_Curve"]
df['BTC_Daily_Return'] = df['Close'].pct_change().fillna(0)
df['Equity_BuyHold'] = (df['Close'] / df['Close'].iloc[0]) * initial_capital
trades = bt_results["Trades_DF"]

# 3. KPI Metric Cards (Top Summary Bar)
col1, col2, col3, col4 = st.columns(4)

final_equity = bt_results["Ending Equity ($)"]
buy_hold_final = df['Equity_BuyHold'].iloc[-1]
total_trades = len(trades)
avoided_trades = int(df['Tech_Buy'].astype(bool).sum() - df['Strategy_Buy'].astype(bool).sum())
max_dd = bt_results["Max Drawdown (%)"]

with col1:
    st.metric(
        label="Strategy Ending Capital (Net of Fees)",
        value=f"${final_equity:,.2f}",
        delta=f"{(final_equity - initial_capital) / initial_capital * 100:.1f}% Total"
    )
with col2:
    st.metric(
        label="BTC Buy & Hold Capital",
        value=f"${buy_hold_final:,.2f}",
        delta=f"{(buy_hold_final - initial_capital) / initial_capital * 100:.1f}% Total"
    )
with col3:
    st.metric(
        label="Executed Trades",
        value=f"{total_trades}",
        delta=f"-{avoided_trades} Macro Filtered",
        delta_color="inverse"
    )
with col4:
    st.metric(
        label="Max Drawdown (Risk)",
        value=f"-{abs(max_dd):.2f}%",
        delta=f"Sharpe: {bt_results['Sharpe Ratio']}",
        delta_color="normal"
    )

st.markdown("---")

# 4. Interactive Chart 1: Equity Curve Comparison
st.subheader("📊 Portfolio Growth: Strategy vs. Buy & Hold ($10,000 Initial | 0.1% Fee + 0.05% Slippage)")
fig_equity = go.Figure()

fig_equity.add_trace(go.Scatter(
    x=df.index, y=df['Equity_Strategy'],
    name="Macro + Quant Strategy (Net)",
    line=dict(color='#00FFA3', width=2.5)
))

fig_equity.add_trace(go.Scatter(
    x=df.index, y=df['Equity_BuyHold'],
    name="BTC Buy & Hold",
    line=dict(color='#888888', width=1.5, dash='dot')
))

fig_equity.update_layout(
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="Portfolio Equity (USD)",
    height=450,
    margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig_equity, use_container_width=True)

# 5. Interactive Chart 2: BTC Price, Trade Executions & Macro Liquidity Regime
st.subheader("🧭 Market Regimes, Buy/Sell Signals & US M2 Liquidity")

fig_price = make_subplots(
    rows=2, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.08,
    row_heights=[0.7, 0.3],
    specs=[[{"secondary_y": False}], [{"secondary_y": True}]],
    subplot_titles=("BTC Price with Strategy Execution Points", "US M2 Money Supply & Fed Funds Rate")
)

# BTC Price Line
fig_price.add_trace(
    go.Scatter(x=df.index, y=df['Close'], name="BTC Price", line=dict(color='#F7931A', width=1.8)),
    row=1, col=1
)

# Buy Signal Markers (Safe Boolean Check)
buys = df[df['Strategy_Buy'].astype(bool)]
fig_price.add_trace(
    go.Scatter(
        x=buys.index, y=buys['Close'],
        mode='markers', name='Macro Buy Signal',
        marker=dict(symbol='triangle-up', size=11, color='#00FF00', line=dict(width=1, color='white'))
    ),
    row=1, col=1
)

# Sell Signal Markers (Safe Boolean Check)
sells = df[df['Strategy_Sell'].astype(bool)]
fig_price.add_trace(
    go.Scatter(
        x=sells.index, y=sells['Close'],
        mode='markers', name='Exit Signal',
        marker=dict(symbol='triangle-down', size=11, color='#FF3B30', line=dict(width=1, color='white'))
    ),
    row=1, col=1
)

# US M2 Money Supply (Left Y-Axis)
if 'M2_Supply' in df.columns:
    fig_price.add_trace(
        go.Scatter(x=df.index, y=df['M2_Supply'], name="US M2 Supply (Billions)", line=dict(color='#34C759', width=1.5)),
        row=2, col=1, secondary_y=False
    )

# Fed Funds Rate (Right Y-Axis)
if 'Fed_Rate' in df.columns:
    fig_price.add_trace(
        go.Scatter(x=df.index, y=df['Fed_Rate'], name="Fed Funds Rate (%)", line=dict(color='#FF9500', width=1.5, dash='dash')),
        row=2, col=1, secondary_y=True
    )

fig_price.update_layout(
    template="plotly_dark",
    height=650,
    margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig_price, use_container_width=True)

# 6. Trade Log Table
st.subheader("📑 Macro Strategy Trade Log (Executed at Next Open with Fees & Slippage)")
st.dataframe(trades, use_container_width=True)
