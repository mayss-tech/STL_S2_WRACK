import ee
from input.s2_collections import ROI_STL




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

def NDVI_recouvrement(image):

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



