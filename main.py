import ee
from ee_init import init_gee
from input.s2_collections import S2_joined
from scripts import reprocessing, time_ajust_cam,plotting_stats,plotting_correlation,plotting_recouvrement
from scripts.stats import NDVI_stats, NDVI_recouvrement
import pandas as pd
import datetime as dt




def main ():

    # --- init gee ---
    init_gee()

    # ---  calculer les indices (NDVI et NDWI) et masquer les nuages et l'eau ---
    S2_processed = (
        S2_joined
        .map(reprocessing.add_indices)
        .map(reprocessing.mask_clouds)
        .map(reprocessing.mask_water)
    )

    # --- calcul statistique NDVI ---
    print("Début du calcul...")

    # Calculer les stats NDVI pour toutes les images
    stats = S2_processed.map(
        lambda img: NDVI_stats(img, 'NDVI')
    ).flatten()

    # Calculer le pourcentage de recouvrement pour toutes les images
    stats_recouvrement = S2_processed.map(NDVI_recouvrement).flatten()
    print("Calculs terminés. Préparation de l'export...")


    # --- export vers Google Drive --- 

    # export 1 : Statistiques NDVI
    NDVI_tab = ee.batch.Export.table.toDrive(
        collection=stats,
        description='NDVI_Stats',
        folder='GEE_Exports',   #les fichiers csv seront téléchargés dans ce dossier, il faut creer un dossier dans drive
        fileFormat='CSV',
        selectors=['name', 'date','count', 'mean', 'median', 'min', 'max', 'stdDev', 'p25', 'p75']  
    )
    NDVI_tab.start()
    print(f"Export NDVI démarré - Task ID: {NDVI_tab.id}") 

    # export 2 : Recouvrement NDVI
    recouvrement_NDVI_tab = ee.batch.Export.table.toDrive(
        collection=stats_recouvrement,
        description='NDVI_Recouvrement',
        folder='GEE_Exports',
        fileNamePrefix='ndvi_recouvrement',
        fileFormat='CSV',
        selectors=['name', 'date','threshold', 'fraction_recouvrement'] 
    )
    recouvrement_NDVI_tab.start()
    print(f"Export Recouvrement démarré - Task ID: {recouvrement_NDVI_tab.id}")
     
    # --- commencer le traitement des donnees issues de la camera ---
    print("commencer le traitement des donnees issues de la camera... ")

    # --- ajuster les heures en UTC pour les donnees de camera de suivi ---
    
    # lecture les tab 
    csvs = [
    r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2019stl.csv',
    r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2020stl.csv'
    
    ]

    for fp in csvs:
        df_raw = pd.read_csv(fp, sep=";")
        df_clean = time_ajust_cam.convert_to_utc(df_raw, date_col='date', time_col='heure',tz_source='America/Toronto')
        df_clean.to_csv(fp.replace(".csv", "_UTC.csv"), index=False)

    print("l'heure est bien corrige en UTC")

    # --- lecture des tableaux contenant les données issues de la caméra de suivi ---
    data_cam_2019 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2019stl_UTC.csv',sep=',')
    data_cam_2020 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2020stl_UTC.csv',sep=',')
    data_cam_2021 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2021stl.csv',sep=',')
    data_cam_2022 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2022stl.csv',sep=',')
    data_cam_2023 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2023stl.csv',sep=',')
    data_cam_2024 = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\2024stl.csv',sep=',')

    # assembler les tableaux
    data_concat = pd.concat([data_cam_2019, data_cam_2020, data_cam_2021, data_cam_2022, data_cam_2023, data_cam_2024], ignore_index=True)
    data_cam = data_concat[["image","datetime_utc","concentration"]].copy()
    data_cam['datetime_utc'] = pd.to_datetime(data_cam['datetime_utc'])
    data_cam['date'] = data_cam['datetime_utc'].dt.date
    data_cam['heure'] = data_cam['datetime_utc'].dt.strftime('%H:%M:%S')
    data_cam['heure'] = pd.to_datetime(data_cam['heure'], format='%H:%M:%S').dt.time

    # filtrer les données entre 15:00:00 et 15:10:00 
    data_cam['heure'] = pd.to_datetime(data_cam['heure'], format='%H:%M:%S').dt.time
    start = dt.time(15, 0, 0)   
    end   = dt.time(15, 10, 0) 

    data_cam = data_cam[(data_cam['heure'] >= start) & (data_cam['heure'] <= end)]

    # réorganisation finale des colonnes 
    cam_tab = data_cam[["image", "date", "heure", "concentration"]]
    
    print("la colonne heure est bien filtree a 15 h ")
    # --- Afficher les résultats filtrés --- 
    print(cam_tab.head(5))
    
    # export 3 : donnees de camera de suivi
    cam_tab.to_csv(
        r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\table_finale_cam_2019_2024.csv',
        index=False
    )
    print("table des donnees de la camera créée et prête au téléchargement")

    # --- Lecture des fichiers --- 
    df_stats_csv = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\ndvi_statistics_stl_s2.csv',sep=',')
    df_recouvr_csv = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\ndvi_recouvrement_stl_s2.csv',sep=',')
    df_cam = pd.read_csv(r"Y:\Mayssa_louati\wrack_S2_NDVI\STL_DATA_CAM\table_finale_cam_2019_2024.csv", sep=",")

    # --- supprimer les lignes avec NAN + copie explicite ---
    df_drop_stats = df_stats_csv.dropna().copy()
    df_drop_recouvr = df_recouvr_csv.dropna().copy()
    df_cam = df_cam.dropna().copy()
    
    # --- réduire chaque tableau a l'essentiel ---
    df_drop_stats = df_drop_stats[['date', 'name', 'count','mean','median','min','max','stdDev','p25','p75']]
    df_drop_recouvr = df_drop_recouvr[['date', 'fraction_recouvrement','threshold']]
    df_cam = df_cam[['image','date', 'concentration']]

    # --- conversion des champs date en format datetime --- 
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
    # merger les 3 tableaux 
    df = (
        df_drop_stats
        .merge(df_drop_recouvr, on='date', how='inner')
        .merge(df_cam, on='date', how='inner')
    )
    df_final = df.loc[:, ~df.columns.duplicated()]


    # --- calculer ndvi normalisé en utilisant la colonne median, fraction_recouvrement normalisée et concentration de camera normalisée --- 
    columns_to_normalize = [
        'median','concentration', "fraction_recouvrement"
    ]
    for col in columns_to_normalize:
        df_final[col + '_normalized'] = (df_final[col] - df_final[col].min()) / (df_final[col].max() - df_final[col].min())


    # vérification 
    print(df_final.head(5))

    # export 4 : export tab final avec des colonnes normalissées
    df_final.to_csv(
    r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\table_finale_stl_2019_2024.csv',
        index=False
    )
    print("tableau final contient des colonnes normalissées créée et prête au téléchargement")

    # --- visualisation graphique ---
    print("la génération des graphiques est en cours...")

    plotting_recouvrement.plot_recouvrement()
    plotting_stats.serie_temp_matrice()
    plotting_correlation.plot_correlation()
    
    print("les graphiques sont là, ils vous attendent dans le dossier output 🎉 🚀 😄")
    

if __name__=="__main__":
    main()