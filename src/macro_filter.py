import numpy as np
import pandas as pd

def apply_macro_regime_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Macroeconomic Liquidity Regime Filter:
    1. M2 YoY Growth: Checks whether US M2 Money Supply has expanded over the past 12 months (252 trading days).
    2. M2 Trend: Verifies whether current M2 Money Supply is higher than its level 30 days ago.
    3. Fed Rate Hike Protection: Identifies periods where the Federal Reserve is not actively hiking rates (Rate Pause or Cut) compared to 90 days ago.
    """
    df = df.copy()
    
    # 1. M2 Year-over-Year (YoY) Growth Percentage
    df['M2_YoY_Growth'] = df['M2_Supply'].pct_change(periods=252) * 100
    
    # 2. M2 30-Day Momentum Trend
    df['M2_Trend'] = df['M2_Supply'] > df['M2_Supply'].shift(30)
    
    # 3. Fed Funds Rate Change (Check for rate hikes over the trailing 90 days)
    # If current interest rate is higher than 90 days ago, a tightening/rate-hike regime is active
    df['Fed_Rate_Change_90d'] = df['Fed_Rate'] - df['Fed_Rate'].shift(90)
    df['Fed_Not_Hiking'] = df['Fed_Rate_Change_90d'] <= 0  # Rate pause or rate-cutting environment
    
    # 4. Composite Macro Bullish Regime Condition:
    # Classifies regime as BULLISH only when M2 YoY growth is positive, 30-day trend is upward, and the Fed is not hiking rates
    df['Macro_Bullish'] = (df['M2_YoY_Growth'] > 0) & (df['M2_Trend'] == True) & (df['Fed_Not_Hiking'] == True)
    
    return df
