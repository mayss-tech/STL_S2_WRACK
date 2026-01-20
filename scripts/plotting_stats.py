import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy.stats import spearmanr
import numpy as np

df_csv = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\ndvi_statistics_stl_s2.csv',sep=',')
# --- Nettoyage global du tableau 

df = df_csv.copy()
df = df_csv.replace([np.inf, -np.inf], np.nan)
df = df_csv.dropna()

# Série temporelle du NDVI de Sentinel-2 entre 2019 et 2024 extraite sur la plage de Sainte-Luce, Québec.

df["date"] = pd.to_datetime(df["date"])
# Convertir les dimensions en pouces
width_inch = 42 / 2.54  # Largeur
height_inch = 12 / 2.54  # Hauteur

# Créer la figure et les axes
fig, ax = plt.subplots(figsize=(width_inch, height_inch))

# Boucle sur chaque groupe de données
for sample_name, group in df.groupby("name"):
    ax.plot(group["date"], group["median"], marker="o", linestyle="-", label=sample_name)

# Axe X : ticks principaux = années, ticks secondaires = mois
ax.xaxis.set_major_locator(mdates.YearLocator())  
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  

ax.xaxis.set_minor_locator(mdates.MonthLocator())  
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))  

# Afficher les labels des mois en plus petit
for label in ax.get_xminorticklabels():
    label.set_rotation(90)
    label.set_fontsize(8)

# Affichage propre
plt.setp(ax.get_xticklabels(), rotation=90, ha='center')


#  Ajouter des lignes verticales par année
for year in pd.date_range(df["date"].min(), df["date"].max(), freq='YS'):
    ax.axvline(x=year, color='gray', linestyle='--', linewidth=0.1)

# Affichage propre des ticks
plt.setp(ax.get_xticklabels(), rotation=90, ha='center')

# Configuration des labels et de la légende
ax.set_xlabel("Date", fontsize=14, fontweight="bold", labelpad=15)
ax.set_ylabel("NDVI", fontsize=14, fontweight="bold", labelpad=15)
ax.legend(title="Polygones", fontsize=10)
ax.grid(True)
plt.show()

# Matrice de corrélation (Spearman) de l’indices NDVI entre les polygones.

#j'utilise la mediane car la distribution des donnees est asymetrique.
colonnes_NDVI = df[["name", "median"]]
# Restructurer les données pour avoir un format adapté
data_pivot_NDVI = colonnes_NDVI.pivot(columns='name', values='median')
# Pour chaque colonne, supprimer les NaN
df_cleaned_NDVI = data_pivot_NDVI.apply(lambda col: col.dropna().reset_index(drop=True))
df_filled_NDVI =df_cleaned_NDVI.fillna(0)

# Convertir les dimensions en pouces
width_inch =19/ 2.54  # Largeur
height_inch = 15 / 2.54  # Hauteur

fig, ax = plt.subplots(figsize=(width_inch, height_inch))
# Calculer la corrélation de Spearman entre toutes les paires d'échantillons
correlation_matrix,_= spearmanr(df_filled_NDVI, axis=0)
print(correlation_matrix,_)
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm',  xticklabels=df_filled_NDVI.columns , yticklabels=df_filled_NDVI.columns, ax=ax)
plt.show()






