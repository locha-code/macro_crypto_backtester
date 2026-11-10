import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def fetch_crypto_history(ticker="BTC-USD", years=5) -> pd.DataFrame:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)

    print(f"බාගත කරමින්: {ticker} ({start_date.strftime('%Y-%m-%d')} සිට {end_date.strftime('%Y-%m-%d')} දක්වා)...")
    df = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1d")

    # Column names පිරිසිදු කිරීම
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"

    output_path = "data/raw/btc_historical_5y.csv"
    df.to_csv(output_path)
    print(f"දත්ත ගබඩා කළා: {output_path} (සම්පූර්ණ පේළි: {len(df)})")
    return df

if __name__ == "__main__":
    fetch_crypto_history()
