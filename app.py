import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# පිටුවේ මූලික සැකසුම (Wide Layout)
st.set_page_config(
    page_title="Macro Quant Crypto Backtester",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 Macro-Integrated BTC Quantitative Trading Dashboard")
st.markdown("Global Liquidity (US M2 & Fed Rates) පදනම් කරගත් Quant Trading Strategy දෘශ්‍යමාන කිරීම.")

# 1. දත්ත කියවීම
@st.cache_data
def load_data():
    signals_df = pd.read_csv("data/processed/btc_strategy_signals.csv", index_col="Date", parse_dates=True)
    trades_df = pd.read_csv("data/processed/macro_trade_log.csv")
    return signals_df, trades_df

try:
    df, trades = load_data()
except Exception as e:
    st.error(f"දත්ත ගොනු කියවීමේදී දෝෂයක් ඇති විය: {e}")
    st.stop()

# 2. Performance & Cumulative Returns ගණනය කිරීම
df['BTC_Daily_Return'] = df['Close'].pct_change().fillna(0)

# Technical Strategy Return
# Crossover Signal එකට අනුව Position එක 0 හෝ 1 වේ
df['Strategy_Daily_Return'] = df['Position'] * df['BTC_Daily_Return']

# Equity Curves (ආරම්භක ප්‍රාග්ධනය $10,000)
initial_capital = 10000.0
df['Equity_Strategy'] = initial_capital * (1 + df['Strategy_Daily_Return']).cumprod()
df['Equity_BuyHold'] = initial_capital * (1 + df['BTC_Daily_Return']).cumprod()

# 3. KPI Metric Cards (ඉහළ පුවරුව)
col1, col2, col3, col4 = st.columns(4)

final_equity = df['Equity_Strategy'].iloc[-1]
buy_hold_final = df['Equity_BuyHold'].iloc[-1]
total_trades = len(trades)
avoided_trades = int(df['Tech_Buy'].sum() - df['Strategy_Buy'].sum())

with col1:
    st.metric(
        label="Strategy Ending Capital",
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
        delta=f"-{avoided_trades} Filtered",
        delta_color="inverse"
    )
with col4:
    # Max Drawdown
    roll_max = df['Equity_Strategy'].cummax()
    drawdown = (df['Equity_Strategy'] - roll_max) / roll_max
    max_dd = drawdown.min() * 100
    st.metric(
        label="Max Drawdown (Risk)",
        value=f"{max_dd:.2f}%",
        delta="Controlled Risk",
        delta_color="normal"
    )

st.markdown("---")

# 4. Interactive Chart 1: Equity Curve Comparison
st.subheader("📊 Portfolio Growth: Strategy vs. Buy & Hold ($10,000 Initial)")
fig_equity = go.Figure()

fig_equity.add_trace(go.Scatter(
    x=df.index, y=df['Equity_Strategy'],
    name="Macro + Quant Strategy",
    line=dict(color='#00FFA3', width=2.5)
))

fig_equity.add_trace(go.Scatter(
    x=df.index, y=df['Equity_BuyHold'],
    name="BTC Buy & Hold",
    line=dict(color='#888888', width=1.5, dash='dot')
))

fig_equity.update_layout(
    template="plotly_dark",
    xaxis_title="දිනය (Date)",
    yaxis_title="ප්‍රාග්ධනය (USD)",
    height=450,
    margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig_equity, use_container_width=True)

# 5. Interactive Chart 2: BTC Price, Trades & Macro Liquidity Regime
st.subheader("🧭 Market Regimes, Buy/Sell Signals & US M2 Liquidity")

fig_price = make_subplots(
    rows=2, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.08,
    row_heights=[0.7, 0.3],
    subplot_titles=("BTC Price with Strategy Execution Points", "US M2 Money Supply & Fed Rate")
)

# BTC Price Line
fig_price.add_trace(
    go.Scatter(x=df.index, y=df['Close'], name="BTC Price", line=dict(color='#F7931A', width=1.8)),
    row=1, col=1
)

# Buy Signals Markers
buys = df[df['Strategy_Buy'] == True]
fig_price.add_trace(
    go.Scatter(
        x=buys.index, y=buys['Close'],
        mode='markers', name='Macro Buy Signal',
        marker=dict(symbol='triangle-up', size=11, color='#00FF00', line=dict(width=1, color='white'))
    ),
    row=1, col=1
)

# Sell Signals Markers
sells = df[df['Strategy_Sell'] == True]
fig_price.add_trace(
    go.Scatter(
        x=sells.index, y=sells['Close'],
        mode='markers', name='Exit Signal',
        marker=dict(symbol='triangle-down', size=11, color='#FF3B30', line=dict(width=1, color='white'))
    ),
    row=1, col=1
)

# M2 Money Supply
fig_price.add_trace(
    go.Scatter(x=df.index, y=df['M2_Supply'], name="US M2 Supply (Billions)", line=dict(color='#34C759', width=1.5)),
    row=2, col=1
)

# Fed Funds Rate (දෙවන y-axis එකක් ලෙස)
fig_price.add_trace(
    go.Scatter(x=df.index, y=df['Fed_Rate'], name="Fed Funds Rate (%)", line=dict(color='#FF9500', width=1.5, dash='dash')),
    row=2, col=1
)

fig_price.update_layout(
    template="plotly_dark",
    height=650,
    margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig_price, use_container_width=True)

# 6. Trade Log Table
st.subheader("📑 Macro Strategy Trade Log")
st.dataframe(trades, use_container_width=True)
