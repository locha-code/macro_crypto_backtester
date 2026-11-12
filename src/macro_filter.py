import numpy as np
import pandas as pd

def apply_macro_regime_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    යාවත්කාලීන කළ Macroeconomic Filters:
    1. M2 YoY Growth: පසුගිය මාස 12ට (Trading days 252) සාපේක්ෂව M2 වර්ධනය වේද?
    2. M2 Trend: දින 30 කට පෙර අගයට වඩා M2 ඉහළ මට්ටමක පවතීද?
    3. Fed Rate Hike Protection: පසුගිය දින 90ට සාපේක්ෂව පොලී අනුපාත ඉහළ නොදමන 
       (ස්ථාවර හෝ පොලී කපන - Rate Cut/Pause) කාල පරිච්ඡේද හඳුනාගැනීම.
    """
    df = df.copy()
    
    # 1. M2 වාර්ෂික වර්ධන ප්‍රතිශතය (YoY % Change)
    df['M2_YoY_Growth'] = df['M2_Supply'].pct_change(periods=252) * 100
    
    # 2. M2 දින 30ක ප්‍රවණතාවය
    df['M2_Trend'] = df['M2_Supply'] > df['M2_Supply'].shift(30)
    
    # 3. Fed Rate වෙනස්වීම (දින 90 තුළ පොලී වැඩි කිරීම් සිදුව ඇත්ද?)
    # පසුගිය දින 90ට වඩා අද පොලී අනුපාතය වැඩි නම් Rate Hike තත්ත්වයක් පවතී
    df['Fed_Rate_Change_90d'] = df['Fed_Rate'] - df['Fed_Rate'].shift(90)
    df['Fed_Not_Hiking'] = df['Fed_Rate_Change_90d'] <= 0  # ස්ථාවර හෝ පොලී අඩුවන කාල
    
    # 4. අවසාන Macro Bullish Regime කොන්දේසිය:
    # M2 වර්ධනය ධනාත්මක විය යුතු අතර, Fed එක අඛණ්ඩව පොලී ඉහළ නොදමන කාලවල පමණක් Crypto සඳහා BULL ලෙස සලකයි
    df['Macro_Bullish'] = (df['M2_YoY_Growth'] > 0) & (df['M2_Trend'] == True) & (df['Fed_Not_Hiking'] == True)
    
    return df
