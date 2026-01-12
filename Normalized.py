import pandas as pd

# --- Lecture des fichiers --- 
df_stats_csv = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\ndvi_statistics_stl_s2.csv',sep=',')
df_recouvr_csv = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\ndvi_recouvrement_stl_s2.csv',sep=',')
df_cam = pd.read_csv(r"Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\table_finale_cam_2019_2024.csv", sep=",")

# --- Supprimer les lignes avec NAN + copie explicite ---
df_drop_stats = df_stats_csv.dropna().copy()
df_drop_recouvr = df_recouvr_csv.dropna().copy()
df_cam = df_cam.dropna().copy()
# --- Réduit chaque tableau a l'essentiel ---
df_drop_stats = df_drop_stats[['date', 'name', 'count','mean','median','min','max','stdDev','p25','p75']]
df_drop_recouvr = df_drop_recouvr[['date', 'fraction_recouvrement','threshold']]
df_cam = df_cam[['image','date', 'concentration']]

# --- Conversion des dates --- 
df_drop_stats.loc[:, 'date'] = pd.to_datetime(
    df_drop_stats.loc[:, 'date'],
    errors='coerce'
)
df_drop_recouvr.loc[:, 'date'] = pd.to_datetime(
    df_drop_recouvr.loc[:, 'date'],
    errors='coerce'
)
df_cam.loc[:, 'date'] = pd.to_datetime(
    df_cam.loc[:, 'date'],
    errors='coerce'
)
df = (
    df_drop_stats
    .merge(df_drop_recouvr, on='date', how='inner')
    .merge(df_cam, on='date', how='inner')
)
df_final = df.loc[:, ~df.columns.duplicated()]


# --- Calculer ndvi normalisé et concentration de camera normalisée --- 
columns_to_normalize = [
    'median','concentration', "fraction_recouvrement"
]
for col in columns_to_normalize:
    df_final[col + '_normalized'] = (df_final[col] - df_final[col].min()) / (df_final[col].max() - df_final[col].min())


# --- Vérification ---
print(df_final.head(5))

# --- Export CSV ---
df_final.to_csv(
   r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\table_finale_stl_2019_2024.csv',
    index=False
)