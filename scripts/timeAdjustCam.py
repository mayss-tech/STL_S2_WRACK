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


    