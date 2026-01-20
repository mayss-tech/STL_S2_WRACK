import ee
from Input.s2_collections import S2_joined

# --- seuil probabilité nuage (en %) --- 
MAX_CLOUD_PROB = 65


# --- ajouter indices --- 
def add_indices(image):
    image = ee.Image(image)
    # calculer NDWI et NDVI
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands([ndwi, ndvi])

# --- Masquer les nuages --- 
def mask_clouds(image):
    cloud_prob = ee.Image(image.get("cloud_prob"))
    return image.updateMask(cloud_prob.select("probability").lt(MAX_CLOUD_PROB))


# --- Masquer eau (NDWI) ---
def mask_water(image):
    image = ee.Image(image)
    return ee.Algorithms.If(
        image.bandNames().contains('NDWI'),
        image.updateMask(image.select('NDWI').lte(0)),  # garde terre (NDWI <= 0)
        image
    )

# --- Pipeline ---
S2_processed = (
    S2_joined
    .map(add_indices)
    .map(mask_clouds)
    .map(mask_water)
)

