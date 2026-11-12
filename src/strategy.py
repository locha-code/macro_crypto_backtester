import numpy as np
import pandas as pd

# src ෆෝල්ඩරය තුළම ඇති නිසා කෙලින්ම import කරගත හැක
try:
    from src.indicators import calculate_macd, calculate_rsi
    from src.macro_filter import apply_macro_regime_filter
except ModuleNotFoundError:
    from indicators import calculate_macd, calculate_rsi
    from macro_filter import apply_macro_regime_filter

def generate_signals(input_csv="data/processed/btc_macro_combined_5y.csv") -> pd.DataFrame:
    df = pd.read_csv(input_csv, index_col="Date", parse_dates=True)
    
    # 1. Technical Indicators ගණනය කිරීම
    macd_df = calculate_macd(df)
    df = pd.concat([df, macd_df], axis=1)
    df['RSI'] = calculate_rsi(df)
    
    # 2. Macro Filter එක් කිරීම (M2 Growth + Fed Rate Check)
    df = apply_macro_regime_filter(df)
    
    # 3. Pine Script Crossover & Conditions (Vectorized)
    macd_crossover = (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)) & (df['MACD'] > df['MACD_Signal'])
    macd_crossunder = (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)) & (df['MACD'] < df['MACD_Signal'])
    
    # සාමාන්‍ය Technical Entry / Exit
    df['Tech_Buy'] = macd_crossover & (df['RSI'] > 50)
    df['Tech_Sell'] = macd_crossunder | (df['RSI'] < 45)
    
    # 4. Macro-Enhanced Strategy Entry:
    # Technical Signal පැමිණියද, Macro Bullish පරිසරයක් ඇති විට පමණක් මිලදී ගනී
    df['Strategy_Buy'] = df['Tech_Buy'] & (df['Macro_Bullish'] == True)
    df['Strategy_Sell'] = df['Tech_Sell']
    
    # 5. Position State Tracking (1 = Invested, 0 = Cash)
    df['Signal'] = 0
    df.loc[df['Strategy_Buy'], 'Signal'] = 1
    df.loc[df['Strategy_Sell'], 'Signal'] = -1
    
    # Forward fill position state (Pandas 3.0+ Compatible)
    pos_series = df['Signal'].replace(0, np.nan).ffill().fillna(0)
    df['Position'] = pos_series.shift(1).fillna(0)
    df.loc[df['Position'] == -1, 'Position'] = 0
    
    output_path = "data/processed/btc_strategy_signals.csv"
    df.to_csv(output_path)
    
    total_tech = int(df['Tech_Buy'].sum())
    filtered_signals = int(df['Strategy_Buy'].sum())
    avoided_trades = total_tech - filtered_signals
    
    print("=== Strategy Engine Results ===")
    print(f"සම්පූර්ණ Technical Buy Signals: {total_tech}")
    print(f"Macro Filter මඟින් අනුමත කළ Buy Signals: {filtered_signals}")
    print(f"අවදානම් සහිත කාලවලදී වැළැක්වූ (Avoided) Trades ගණන: {avoided_trades}")
    
    return df

if __name__ == "__main__":
    generate_signals()
