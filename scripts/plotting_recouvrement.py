import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr

def spearman(g):
        x = g["concentration_normalized"]
        y = g["fraction_recouvrement_normalized"]
        m = x.notna() & y.notna()
        if m.sum() >= 3:
            return spearmanr(x[m], y[m]).correlation
        return np.nan

def plot_recouvrement():
    df = pd.read_csv(r'Y:\Mayssa_louati\wrack_S2_NDVI\STL_STATS\table_finale_stl_2019_2024.csv',sep=',')

    # --- courbe de variation du coefficient de corrélation de Spearman entre le recouvrement NDVI et la concentration caméra normalisée
    #  pour le polygone global (polygone 4) en fonction du seuil NDVI ---
    df = df.drop_duplicates(
        subset=[
            "name",
            "date",
            "median_normalized",
            "concentration_normalized",
            "threshold"
        ]
    )
    df_poly = df[df["name"] == "STL_S2_POLYGONE_4"]
    thr_vals, r_vals = [], []

    for thr, g in df_poly.groupby("threshold"):   #analyse la corrélation séparément pour chaque seuil
        x = pd.to_numeric(g["concentration_normalized"])
        y = pd.to_numeric(g["fraction_recouvrement_normalized"])
        r, _ = spearmanr(x, y)
        thr_vals.append(thr)
        r_vals.append(r)

    order = np.argsort(thr_vals)

    plt.plot(np.array(thr_vals)[order], np.array(r_vals)[order], "-o")
    plt.axhline(0, color='k', linestyle='--', linewidth=0.6)
    plt.xlabel("Seuils NDVI")
    plt.ylabel("r (NDVI recouvrement normalisé–Concentration caméra normalisée) ")
    plt.ylim(bottom=0.05)
    plt.grid(alpha=0.4)
    plt.tight_layout()

    # --- sauvegarde dans le dossier output ---
    plt.savefig(
        "output/correlation_camera_seuil_ndvi.png",
        dpi=300,
        bbox_inches="tight"
    )




    # --- carte de ...  Corrélation de Spearman recouvrement–concentration en fonction des seuils NDVI et des polygones ---
    df = df.drop_duplicates(
        subset=[
            "name",
            "date",
            "median_normalized",
            "concentration_normalized",
            "threshold"
        ]
    )
    

    df_corr = (
        df.groupby(["name", "threshold"])
        .apply(spearman)
        .reset_index(name="spearman_r")
    )


    # mise en forme de la matrice

    all_names = df["name"].unique()
    heatmap_data = (
        df_corr
        .pivot(index="name", columns="threshold", values="spearman_r")
        .reindex(all_names)
    )

    plt.figure(figsize=(10, 4))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="viridis",
        center=0,
        mask=heatmap_data.isna(),
        cbar_kws={"label": "Corrélation de Spearman (r , recouvrement–concentration)"}
    )

    plt.xlabel("Seuil NDVI")
    plt.ylabel("Polygones")
    plt.tight_layout()

    # --- sauvegarde dans le dossier output ---
    plt.savefig(
        "output/heatmap_correlation_camera_seuil_ndvi.png",
        dpi=300,
        bbox_inches="tight"
    )




