import pandas as pd
import datetime as dt
# --- lecture des fichiers ---
data_cam_2019 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2019stl_UTC.csv',sep=',')
data_cam_2020 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2020stl_UTC.csv',sep=',')
data_cam_2021 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2021stl.csv',sep=',')
data_cam_2022 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2022stl.csv',sep=',')
data_cam_2023 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2023stl.csv',sep=',')
data_cam_2024 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2024stl.csv',sep=',')

# --- Assembler les tableaux ---
data_concat = pd.concat([data_cam_2019, data_cam_2020, data_cam_2021, data_cam_2022, data_cam_2023, data_cam_2024], ignore_index=True)
data_cam = data_concat[["image","datetime_utc","concentration"]].copy()
data_cam['datetime_utc'] = pd.to_datetime(data_cam['datetime_utc'])
data_cam['date'] = data_cam['datetime_utc'].dt.date
data_cam['heure'] = data_cam['datetime_utc'].dt.strftime('%H:%M:%S')
data_cam['heure'] = pd.to_datetime(data_cam['heure'], format='%H:%M:%S').dt.time

# --- Filtrer les données entre 15:00:00 et 15:10:00 ---
data_cam['heure'] = pd.to_datetime(data_cam['heure'], format='%H:%M:%S').dt.time
start = dt.time(15, 0, 0)   
end   = dt.time(15, 10, 0) 

data_cam = data_cam[(data_cam['heure'] >= start) & (data_cam['heure'] <= end)]

# --- Réorganisation finale des colonnes ---
table_finale_cam = data_cam[["image", "date", "heure", "concentration"]]

# --- Afficher les résultats filtrés --- 
print(table_finale_cam.head(5))
# --- Export CSV --- 
#table_finale_cam.to_csv(
   #r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\table_finale_cam_2019_2024.csv',
    #index=False
#)
print("Table générale créée et prête au téléchargement.")