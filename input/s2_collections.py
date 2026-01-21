import ee
from ee_init import init_gee
from .geometries import build_roi_featurecollection

# --- Init GEE ---
init_gee()

# --- ROI ---
ROI_STL = build_roi_featurecollection(ee)

# --- Dates ---
START = '2019-01-01'
END = '2024-12-31'

# --- Collections sources ---
S2 = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate(START, END)
    .filterBounds(ROI_STL)
)

S2c = (
    ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
    .filterDate(START, END)
    .filterBounds(ROI_STL)
)

# --- Joindre des 2 collections --- 
S2_joined = ee.ImageCollection(
    ee.Join.saveFirst("cloud_prob").apply(
        primary=S2,
        secondary=S2c,
        condition=ee.Filter.equals(
            leftField="system:index",
            rightField="system:index"
        )
    )
)






