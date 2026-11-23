Macro-Integrated BTC Trading Backtester

A Python backtesting tool and interactive dashboard for Bitcoin (BTC) trading. This project combines technical indicators (**MACD & RSI**) with US economic data (**US M2 Money Supply & Fed Interest Rates**) to make smarter trading decisions.

**Live Dashboard:** [locha-art-cryptobacktester.streamlit.app](https://locha-art-cryptobacktester.streamlit.app/)

---

## Backtest Results (2022–2026 | $10,000 Starting Capital)
* **Strategy Final Balance (After Fees):** `$16,048.98` (**+60.5% Profit**)
* **BTC Buy & Hold Final Balance:** `$13,032.48` (**+30.3% Profit**)
* **Maximum Drawdown (Biggest Drop):** `-19.91%`
* **Total Trades:** `26` executed trades (`15` risky trades were avoided using the macro filter)

---

## How This Trading System Works (Trading Rules)
Many basic backtests show fake profits because they ignore trading fees or use future prices. This system uses realistic market rules:

* **Spot Trading Only (Long-Only):** It only buys BTC when prices are expected to go up. There is no leverage and no short-selling.
* **All-In / All-Out:** When a Buy signal happens, it uses 100% of the available cash. When a Sell signal happens, it sells 100% of the BTC.
* **No Look-Ahead Bias:** If a signal appears at today's market close, the trade happens at **tomorrow's opening price**.
* **Real Trading Costs Included:** Every buy and sell includes a **0.10% broker fee** and **0.05% slippage** (price difference).
* **Smart Buy & Sell Rules:**
  * **Buy Rule:** Buys only when technical indicators are bullish (`MACD Crossover` + `RSI > 50`) **AND** the US economy has good liquidity (`Macro_Bullish == True`).
  * **Sell Rule:** Sells immediately when technical indicators turn weak (`MACD Crossunder` OR `RSI < 45`). It ignores macro data when selling so it can protect money quickly.

---

## Project Files
* `app.py` – The interactive Streamlit web dashboard with charts and trade history.
* `src/backtester.py` – Calculates real profits, losses, trading fees, slippage, and risk metrics.
* `src/strategy.py` – Creates the Buy and Sell signals.
* `src/indicators.py` – Calculates MACD and RSI values.
* `src/macro_filter.py` – Checks US M2 Money Supply growth and Fed interest rate changes.
* `src/data_loader.py` & `src/macro_pipeline.py` – Downloads and cleans BTC price data and FRED economic data.

---

## Tools & Technologies Used
* **Programming:** Python (Pandas, NumPy)
* **Charts & Web App:** Plotly, Streamlit
* **Data Sources:** Yahoo Finance (BTC-USD), FRED Economic Database (US M2 & Fed Rates)
