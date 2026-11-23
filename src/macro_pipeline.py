import os
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv

load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

def fetch_macro_and_merge(crypto_csv_path="data/raw/btc_historical_5y.csv"):
    if not FRED_API_KEY:
        raise ValueError("FRED_API_KEY is not configured in the .env file.")

    fred = Fred(api_key=FRED_API_KEY)

    # 1. Fetch Macroeconomic Indicators from FRED
    print("Downloading macroeconomic data from FRED...")
    m2 = fred.get_series('M2SL')             # US M2 Money Supply (Monthly)
    fed_funds = fred.get_series('FEDFUNDS')   # Federal Funds Effective Rate (Monthly)
    cpi = fred.get_series('CPIAUCSL')         # Consumer Price Index / Inflation (Monthly)

    macro_df = pd.DataFrame({
        'M2_Supply': m2,
        'Fed_Rate': fed_funds,
        'CPI': cpi
    })
    macro_df.index = pd.to_datetime(macro_df.index)
    macro_df.index.name = "Date"

    # 2. Load Daily Crypto Historical Data
    btc_df = pd.read_csv(crypto_csv_path, index_col="Date", parse_dates=True)

    # 3. Merge Monthly Macro Data into Daily Crypto Data via Forward-Fill
    # Forward-fill (ffill) propagates only published values forward to prevent look-ahead bias
    combined_df = btc_df.merge(macro_df, left_index=True, right_index=True, how='left')
    combined_df[['M2_Supply', 'Fed_Rate', 'CPI']] = combined_df[['M2_Supply', 'Fed_Rate', 'CPI']].ffill()

    # Drop initial rows containing missing macro values
    combined_df = combined_df.dropna()

    output_path = "data/processed/btc_macro_combined_5y.csv"
    combined_df.to_csv(output_path)
    print(f"Successfully merged and saved dataset: {output_path}")
    print(combined_df[['Close', 'M2_Supply', 'Fed_Rate']].tail(5))
    return combined_df

if __name__ == "__main__":
    fetch_macro_and_merge()
