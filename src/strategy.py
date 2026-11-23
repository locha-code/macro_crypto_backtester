import numpy as np
import pandas as pd

# Direct imports when running inside or outside the src directory
try:
    from src.indicators import calculate_macd, calculate_rsi
    from src.macro_filter import apply_macro_regime_filter
except ModuleNotFoundError:
    from indicators import calculate_macd, calculate_rsi
    from macro_filter import apply_macro_regime_filter

def generate_signals(input_csv="data/processed/btc_macro_combined_5y.csv") -> pd.DataFrame:
    df = pd.read_csv(input_csv, index_col="Date", parse_dates=True)
    
    # 1. Compute Technical Indicators
    macd_df = calculate_macd(df)
    df = pd.concat([df, macd_df], axis=1)
    df['RSI'] = calculate_rsi(df)
    
    # 2. Apply Macroeconomic Liquidity Filter (M2 Growth + Fed Rate Check)
    df = apply_macro_regime_filter(df)
    
    # 3. Vectorized Crossover & Technical Conditions
    macd_crossover = (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)) & (df['MACD'] > df['MACD_Signal'])
    macd_crossunder = (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)) & (df['MACD'] < df['MACD_Signal'])
    
    # Baseline Technical Entry / Exit Signals
    df['Tech_Buy'] = macd_crossover & (df['RSI'] > 50)
    df['Tech_Sell'] = macd_crossunder | (df['RSI'] < 45)
    
    # 4. Macro-Enhanced Strategy Entry & Exit:
    # Enter long only when both technical momentum and macro liquidity regime are bullish
    df['Strategy_Buy'] = df['Tech_Buy'] & (df['Macro_Bullish'] == True)
    df['Strategy_Sell'] = df['Tech_Sell']
    
    # 5. Position State Tracking (1 = Invested, 0 = Cash)
    df['Signal'] = 0
    df.loc[df['Strategy_Buy'], 'Signal'] = 1
    df.loc[df['Strategy_Sell'], 'Signal'] = -1
    
    # Forward-fill position state (Pandas 3.0+ Compatible)
    pos_series = df['Signal'].replace(0, np.nan).ffill().fillna(0)
    df['Position'] = pos_series.shift(1).fillna(0)
    df.loc[df['Position'] == -1, 'Position'] = 0
    
    output_path = "data/processed/btc_strategy_signals.csv"
    df.to_csv(output_path)
    
    total_tech = int(df['Tech_Buy'].sum())
    filtered_signals = int(df['Strategy_Buy'].sum())
    avoided_trades = total_tech - filtered_signals
    
    print("=== Strategy Engine Results ===")
    print(f"Total Technical Buy Signals: {total_tech}")
    print(f"Macro-Approved Buy Signals: {filtered_signals}")
    print(f"High-Risk Trades Avoided via Macro Filter: {avoided_trades}")
    
    return df

if __name__ == "__main__":
    generate_signals()
