import numpy as np
import pandas as pd

def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    """Calculate Exponential Moving Average (EMA)."""
    return series.ewm(span=span, adjust=False).mean()

def calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """Calculate vectorized MACD Line, Signal Line, and Histogram."""
    fast_ema = calculate_ema(df['Close'], fast)
    slow_ema = calculate_ema(df['Close'], slow)
    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return pd.DataFrame({
        'MACD': macd_line,
        'MACD_Signal': signal_line,
        'MACD_Hist': histogram
    }, index=df.index)

def calculate_rsi(df: pd.DataFrame, period=14) -> pd.Series:
    """Calculate vectorized RSI matching TradingView's Wilder's Smoothing method."""
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Wilder's Smoothing (alpha = 1 / period)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-10)  # Prevent division by zero
    rsi = 100 - (100 / (1 + rs))
    return rsi
