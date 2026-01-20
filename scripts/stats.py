import ee
from ee_init import verifier_gee
from Input.s2_collections import ROI_STL
from reprocessing import S2_processed

# --- Init gee ---
etat = verifier_gee()
if not etat.get("authentifie", False):
    ee.Authenticate()
if not etat.get("initialise", False):
    ee.Initialize()

# --- Fonction pour calculer les statistiques de NDVI --- 
reducer_stats = (
    ee.Reducer.mean()
    .combine(ee.Reducer.median(), '', True)
    .combine(ee.Reducer.min(), '', True)
    .combine(ee.Reducer.max(), '', True)
    .combine(ee.Reducer.stdDev(), '', True)
    .combine(ee.Reducer.percentile([25, 75]), '', True)
    .combine(ee.Reducer.count(), '', True)
)
def NDVI_stats(image, band_name):
    stats = image.select(band_name).reduceRegions(
        collection=ROI_STL,   
        reducer=reducer_stats,
        scale=10
    )
    
    return stats.map(
        lambda f: f.set({
            'name': f.get('name'),
            'date': image.date().format('YYYY-MM-dd')
            
        })
    )

# --- Fonction pour calculer le pourcentage de recouvrement NDVI ---

def recouvrement_ndvi(image):

    thresholds = ee.List.sequence(0.1, 0.8, 0.05)

    def per_threshold(t):
        t = ee.Number(t)

        ndvi = image.select('NDVI')

        # Pixels NDVI >= seuil (les autres masqués)
        ndvi_bin = ndvi.gte(t)

        stats = ndvi_bin.reduceRegions(
            collection=ROI_STL,
            reducer=ee.Reducer.mean(),  # fraction directe
            scale=10,
            tileScale=2
        )

        return stats.map(lambda f: f.set({
            'name': f.get('name'),
            'date': image.date().format('YYYY-MM-dd'),
            'threshold': t,
            'fraction_recouvrement': f.get('mean')
        }))

    return ee.FeatureCollection(thresholds.map(per_threshold)).flatten()


# --- Traitement principal ---
print("Début du traitement...")

# Calculer les stats NDVI 

stats = S2_processed.map(
    lambda img: NDVI_stats(img, 'NDVI')
).flatten()
# Calculer le pourcentage de recouvrement pour toutes les images

stats_recouvrement = S2_processed.map(recouvrement_ndvi).flatten()
print("Calculs terminés. Préparation de l'export...")


# --- Export vers Google Drive ---

# Export 1 : Statistiques NDVI
#export_ndvi = ee.batch.Export.table.toDrive(
    #collection=stats,
    #description='NDVI_Stats',
    #folder='GEE_Exports', 
    #fileFormat='CSV',
    #selectors=['name', 'date','count', 'mean', 'median', 'min', 'max', 'stdDev', 'p25', 'p75']  
#)

#export_ndvi.start()
#print(f"Export NDVI démarré - Task ID: {export_ndvi.id}")

# Export 2 : Recouvrement NDVI
export_recouvrement = ee.batch.Export.table.toDrive(
    collection=stats_recouvrement,
    description='NDVI_Recouvrement',
    folder='GEE_Exports',
    fileNamePrefix='ndvi_recouvrement',
    fileFormat='CSV',
    selectors=['name', 'date','threshold', 'fraction_recouvrement'] 
)
export_recouvrement.start()
print(f"Export Recouvrement démarré - Task ID: {export_recouvrement.id}")

