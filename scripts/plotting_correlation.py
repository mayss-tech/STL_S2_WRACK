import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from scipy.interpolate import make_interp_spline
import matplotlib.cm as cm
from matplotlib.lines import Line2D
import os

df = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\table_finale_stl_2019_2024.csv',sep=',')

# --- Nettoyage global du tableau ---
df = df.copy()
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna()


#--- courbe de corrélation entre la concentration normalisée mesurée par caméra et le NDVI normalisé mesuré par satellite (S2)
#  pour différents polygones (corrélation de Spearman) ---

plt.figure(figsize=(12, 6))

sns.set_theme(style="whitegrid", context='paper')

for name, subset in df.groupby("name"):
    corr = subset["median_normalized"].corr(subset["concentration_normalized"], method="spearman")
    plt.scatter(
        subset["concentration_normalized"],
        subset["median_normalized"],
        label=f"{name} (r={corr:.2f})",
        alpha=0.7
    )

plt.xlabel("Concentration normalisée (Caméra de suivi)",fontsize=10, fontweight="bold", labelpad=1)
plt.ylabel("NDVI normalisé",fontsize=10, fontweight="bold", labelpad=1)
plt.legend(loc="best")
# --- sauvegarde dans le dossier output ---
plt.savefig(
    "Output/correlation_camera_NDVI_spearman.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()



# Représentation du NDVI normalisé en fonction de la concentration des macroalgues normalisée détectée par caméra
# avec catégorisation des niveaux d’accord entre les deux sources de données.

df = df[df["name"] == "STL_S2_POLYGON_4"]

# Corrélation
r = df["median_normalized"].corr(
    df["concentration_normalized"], method="spearman"
)
print(f"Spearman r = {r:.2f}")

# Seuils (quartiles)
ndvi_q25, ndvi_q75 = df["median_normalized"].quantile([.25, .75])
cam_q25, cam_q75 = df["concentration_normalized"].quantile([.25, .75])

# Catégorisation vectorisée
df["Categorie"] = "Autres"
df.loc[(df.median_normalized < ndvi_q25) & (df.concentration_normalized < cam_q25),
       "Categorie"] = "NDVI faible - Caméra faible"
df.loc[(df.median_normalized > ndvi_q75) & (df.concentration_normalized > cam_q75),
       "Categorie"] = "NDVI élevé - Caméra élevé"
df.loc[(df.median_normalized < ndvi_q25) & (df.concentration_normalized > cam_q75),
       "Categorie"] = "NDVI faible - Caméra élevé"
df.loc[(df.median_normalized > ndvi_q75) & (df.concentration_normalized < cam_q25),
       "Categorie"] = "NDVI élevé - Caméra faible"


fig, ax = plt.subplots(figsize=(15, 6))

cats = df["Categorie"].astype("category")
codes = cats.cat.codes
cmap = cm.get_cmap("Set1", len(cats.cat.categories))

ax.scatter(
    df["concentration_normalized"],
    df["median_normalized"],
    c=codes, cmap=cmap, alpha=0.3, s=15   # ⬅ points plus petits
)

# Représenter les lignes des seuils
ax.axhline(ndvi_q25, ls="--", c="gray")
ax.axhline(ndvi_q75, ls="--", c="gray")
ax.axvline(cam_q25, ls="--", c="blue")
ax.axvline(cam_q75, ls="--", c="blue")

ax.set_xlabel("Concentration normalisée (Caméra)", fontweight="bold")
ax.set_ylabel("NDVI normalisé", fontweight="bold")

# Légende 
handles = [
    Line2D([0], [0], marker="o", color="w", label=l,
           markerfacecolor=cmap(i), markersize=6)
    for i, l in enumerate(cats.cat.categories)
]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.75, 0.95))

plt.tight_layout()
plt.show()


# Courbe de l’évolution temporelle du NDVI et de la concentration normalisée mesurée par caméra à Sainte-Luce entre 2019 et 2024.

sample = "STL_S2_POLYGON_4"

# Nettoyage
df = df[df["name"] == sample]
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date", "median_normalized", "concentration_normalized"])

# Mediane mensuelle
df["ym"] = df["date"].dt.to_period("M")
m = df.groupby("ym")[["median_normalized", "concentration_normalized"]].median()
m.index = m.index.to_timestamp("M")

# Lissage spline
x = mdates.date2num(m.index)

xs = np.linspace(x.min(), x.max(), 500)
ndvi_s = make_interp_spline(x, m["median_normalized"], k=3)(xs)
cam_s  = make_interp_spline(x, m["concentration_normalized"], k=3)(xs)


fig, ax = plt.subplots(figsize=(11, 5))

ax.plot_date(xs, ndvi_s, "-", lw=2, label="NDVI")
ax.plot_date(xs, cam_s,  "--", lw=2, label="Caméra")

ax.set_xlim(pd.Timestamp("2019-01-01"), pd.Timestamp("2024-12-31"))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.set_ylabel("Valeurs normalisées")
ax.set_ylim(0, 1)
ax.grid(True, axis="y", alpha=0.3)
ax.legend(frameon=False)

plt.tight_layout()
plt.show()




# Courbe mensuelle du cycle saisonnier du NDVI et de la concentration normalisée issue de la caméra.
# Paramétres
sample = "STL_S2_POLYGON_4"

MONTH_FR = {1:"janv",2:"févr",3:"mars",4:"avr",5:"mai",6:"juin",
            7:"juil",8:"août",9:"sept",10:"oct",11:"nov",12:"déc"}
ORDER = ["janv","févr","mars","avr","mai","juin","juil","août","sept","oct","nov","déc"]

# Filtrage +dates
df = df[df["name"] == sample]
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date", "median_normalized", "concentration_normalized"])
df["month"] = df["date"].dt.month.map(MONTH_FR)

# Agrégation mensuelle-
g = df.groupby("month")

ndvi_med = g["median_normalized"].median().reindex(ORDER)
ndvi_q25 = g["median_normalized"].quantile(0.25).reindex(ORDER)
ndvi_q75 = g["median_normalized"].quantile(0.75).reindex(ORDER)

cam_med  = g["concentration_normalized"].median().reindex(ORDER)
cam_q25  = g["concentration_normalized"].quantile(0.25).reindex(ORDER)
cam_q75  = g["concentration_normalized"].quantile(0.75).reindex(ORDER)

plt.figure(figsize=(8, 5))

plt.plot(ORDER, ndvi_med, "-o", label="NDVI (médiane)")
plt.fill_between(ORDER, ndvi_q25, ndvi_q75, alpha=0.25, label="IQR NDVI")

plt.plot(ORDER, cam_med, "--s", label="Caméra (médiane)")
plt.fill_between(ORDER, cam_q25, cam_q75, alpha=0.15, label="IQR Caméra")

plt.xlim("avr", "oct")
plt.xlabel("Mois")
plt.ylabel("Valeurs normalisées")
plt.grid(alpha=0.3)
plt.legend(frameon=False)

plt.tight_layout()
plt.show()


