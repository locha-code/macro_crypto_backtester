import numpy as np
import pandas as pd

def calculate_drawdown(equity_series: pd.Series):
    hwm = equity_series.cummax()
    drawdown = (equity_series - hwm) / hwm
    max_drawdown = drawdown.min()
    return max_drawdown, drawdown

def calculate_sharpe_ratio(daily_returns: pd.Series, risk_free_rate=0.04) -> float:
    daily_rf = (1 + risk_free_rate) ** (1 / 365) - 1
    excess_returns = daily_returns - daily_rf
    std = excess_returns.std()
    if std == 0 or np.isnan(std):
        return 0.0
    return float((excess_returns.mean() / std) * np.sqrt(365))

def calculate_sortino_ratio(daily_returns: pd.Series, risk_free_rate=0.04) -> float:
    daily_rf = (1 + risk_free_rate) ** (1 / 365) - 1
    excess_returns = daily_returns - daily_rf
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = downside_returns.std()
    if downside_std == 0 or np.isnan(downside_std):
        return 0.0
    return float((excess_returns.mean() / downside_std) * np.sqrt(365))

def calculate_trade_metrics(trades_df: pd.DataFrame) -> dict:
    if trades_df.empty:
        return {"Win Rate (%)": 0, "Profit Factor": 0, "Risk-Reward Ratio": 0, "Total Trades": 0}
    wins = trades_df[trades_df['Net_Profit'] > 0]
    losses = trades_df[trades_df['Net_Profit'] < 0]
    win_rate = (len(wins) / len(trades_df)) * 100
    gross_profits = wins['Net_Profit'].sum()
    gross_losses = abs(losses['Net_Profit'].sum())
    profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else np.nan
    avg_win = wins['Return_Pct'].mean() if len(wins) > 0 else 0
    avg_loss = abs(losses['Return_Pct'].mean()) if len(losses) > 0 else 0
    risk_reward = (avg_win / avg_loss) if avg_loss > 0 else np.nan
    return {
        "Total Trades": len(trades_df),
        "Win Rate (%)": round(win_rate, 2),
        "Profit Factor": round(profit_factor, 2) if not np.isnan(profit_factor) else "Inf",
        "Risk-Reward Ratio": round(risk_reward, 2) if not np.isnan(risk_reward) else "N/A"
    }
