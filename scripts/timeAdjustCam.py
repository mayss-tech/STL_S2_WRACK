import pytz # bib pour la gestion des fuseaux horaires 
import pandas as pd

# --- Fonction pour convertir lheure local to UTC  
def convert_to_utc(df, date_col='date', time_col='heure', tz_source='America/Toronto'):
    df['datetime_local'] = df[date_col].astype(str) + ' ' + df[time_col].astype(str)
    df['datetime_local'] = pd.to_datetime(df['datetime_local'])

    source_timezone = pytz.timezone(tz_source)
    df['datetime_local'] = df['datetime_local'].dt.tz_localize(source_timezone)
    df['datetime_utc'] = df['datetime_local'].dt.tz_convert('UTC')
    df['datetime_utc'] = df['datetime_utc'].dt.tz_localize(None)
    return df

csvs = [
    r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2019stl.csv',
    r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2020stl.csv'
    
]

for fp in csvs:
    df_raw = pd.read_csv(fp, sep=";")
    df_clean = convert_to_utc(df_raw, date_col='date', time_col='heure',tz_source='America/Toronto')
    df_clean.to_csv(fp.replace(".csv", "_UTC.csv"), index=False)
    