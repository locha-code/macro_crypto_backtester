import numpy as np
import pandas as pd

try:
    from metrics import calculate_drawdown, calculate_sharpe_ratio, calculate_sortino_ratio, calculate_trade_metrics
except ImportError:
    from src.metrics import calculate_drawdown, calculate_sharpe_ratio, calculate_sortino_ratio, calculate_trade_metrics

class InstitutionalBacktester:
    def __init__(self, initial_capital=10000.0, fee_pct=0.001, slippage_pct=0.0005):
        self.initial_capital = initial_capital
        self.fee_pct = fee_pct            # 0.1% Broker Commission
        self.slippage_pct = slippage_pct  # 0.05% Slippage
        
    def run_backtest(self, df: pd.DataFrame, signal_col='Strategy_Buy', exit_col='Strategy_Sell') -> dict:
        data = df.copy()
        capital = self.initial_capital
        in_position = False
        entry_price = 0.0
        entry_date = None
        position_size = 0.0
        trades = []
        
        equity_curve = pd.Series(index=data.index, dtype=float)
        
        for i in range(len(data) - 1):
            current_date = data.index[i]
            next_date = data.index[i + 1]
            next_open = data['Open'].iloc[i + 1]
            
            # --- BUY EXECUTION (Next Open Price) ---
            if not in_position and bool(data[signal_col].iloc[i]):
                effective_entry = next_open * (1 + self.slippage_pct)
                position_size = (capital * (1 - self.fee_pct)) / effective_entry
                in_position = True
                entry_price = effective_entry
                entry_date = next_date
                capital = 0.0
                
            # --- SELL EXECUTION (Next Open Price) ---
            elif in_position and bool(data[exit_col].iloc[i]):
                effective_exit = next_open * (1 - self.slippage_pct)
                gross_proceeds = position_size * effective_exit
                capital = gross_proceeds * (1 - self.fee_pct)
                
                trade_return = (effective_exit * (1 - self.fee_pct)) / (entry_price * (1 + self.fee_pct)) - 1
                trades.append({
                    'Entry_Date': entry_date,
                    'Exit_Date': next_date,
                    'Entry_Price': round(entry_price, 2),
                    'Exit_Price': round(effective_exit, 2),
                    'Return_Pct': round(trade_return * 100, 2),
                    'Net_Profit': round(capital - (position_size * entry_price), 2)
                })
                in_position = False
                position_size = 0.0
                
            # Current Day Portfolio Value
            if in_position:
                current_close = data['Close'].iloc[i]
                equity_curve.loc[current_date] = position_size * current_close * (1 - self.fee_pct)
            else:
                equity_curve.loc[current_date] = capital
                
        # Final day evaluation
        equity_curve.iloc[-1] = capital if not in_position else position_size * data['Close'].iloc[-1]
        equity_curve = equity_curve.ffill()
        
        # Risk Metrics Calculations
        daily_returns = equity_curve.pct_change().dropna()
        max_dd, dd_series = calculate_drawdown(equity_curve)
        sharpe = calculate_sharpe_ratio(daily_returns)
        sortino = calculate_sortino_ratio(daily_returns)
        
        # Benchmark: BTC Buy and Hold
        btc_bh_equity = (data['Close'] / data['Close'].iloc[0]) * self.initial_capital
        btc_daily_ret = data['Close'].pct_change().dropna()
        btc_max_dd, _ = calculate_drawdown(btc_bh_equity)
        btc_sharpe = calculate_sharpe_ratio(btc_daily_ret)
        
        trades_df = pd.DataFrame(trades)
        trade_summary = calculate_trade_metrics(trades_df)
        
        years = (data.index[-1] - data.index[0]).days / 365.25
        cagr = ((equity_curve.iloc[-1] / self.initial_capital) ** (1 / years) - 1) * 100
        btc_cagr = ((btc_bh_equity.iloc[-1] / self.initial_capital) ** (1 / years) - 1) * 100
        
        return {
            "Ending Equity ($)": round(equity_curve.iloc[-1], 2),
            "CAGR (%)": round(cagr, 2),
            "Benchmark CAGR (%)": round(btc_cagr, 2),
            "Max Drawdown (%)": round(max_dd * 100, 2),
            "Benchmark Max DD (%)": round(btc_max_dd * 100, 2),
            "Sharpe Ratio": round(sharpe, 2),
            "Benchmark Sharpe": round(btc_sharpe, 2),
            "Sortino Ratio": round(sortino, 2),
            "Trades Summary": trade_summary,
            "Trades_DF": trades_df,
            "Equity_Curve": equity_curve
        }
