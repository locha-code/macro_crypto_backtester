import numpy as np
import pandas as pd

def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential Moving Average (EMA) ගණනය කිරීම."""
    return series.ewm(span=span, adjust=False).mean()

def calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """Vectorized MACD Line සහ Signal Line ගණනය කිරීම."""
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
    """TradingView Wilder's RSI ක්‍රමයට අනුකූල Vectorized RSI."""
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Wilder's Smoothing (alpha = 1 / period)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-10) # Division by zero වැළැක්වීම
    rsi = 100 - (100 / (1 + rs))
    return rsi
