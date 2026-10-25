from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FixedFormatter

RACINE = Path(__file__).resolve().parent.parent
SORTIES = RACINE / "outputs"
DOCS = RACINE / "docs"
DOCS.mkdir(exist_ok=True)

# Couleurs du thème bancaire du projet
OR = "#C9A227"
MARINE = "#13315C"
GRIS = "#B8C4D0"

LIBELLES = {
    "deja_contacte": "Déjà contacté",
    "C(contact, Treatment('telephone'))[T.cellular]": "Appelé sur portable",
    "campaign": "Chaque appel supplémentaire",
    "C(tranche_age, Treatment('2. 30-44'))[T.1. <30]": "Moins de 30 ans",
    "C(tranche_age, Treatment('2. 30-44'))[T.3. 45-59]": "45-59 ans",
    "C(tranche_age, Treatment('2. 30-44'))[T.4. 60+]": "60 ans et plus",
    "C(job, Treatment('admin.'))[T.blue-collar]": "Ouvrier",
    "C(job, Treatment('admin.'))[T.entrepreneur]": "Entrepreneur",
    "C(job, Treatment('admin.'))[T.housemaid]": "Employé de maison",
    "C(job, Treatment('admin.'))[T.management]": "Cadre",
    "C(job, Treatment('admin.'))[T.retired]": "Retraité",
    "C(job, Treatment('admin.'))[T.self-employed]": "Indépendant",
    "C(job, Treatment('admin.'))[T.services]": "Services",
    "C(job, Treatment('admin.'))[T.student]": "Étudiant",
    "C(job, Treatment('admin.'))[T.technician]": "Technicien",
    "C(job, Treatment('admin.'))[T.unemployed]": "Sans emploi",
}

# Lecture des résultats de la régression, sans la constante
odds = pd.read_csv(SORTIES / "odds_ratios.csv", index_col=0).drop(index="Intercept")
odds["libelle"] = odds.index.map(LIBELLES)
odds = odds.sort_values("odds_ratio").reset_index(drop=True)

# Un effet est significatif si son intervalle de confiance ne contient pas 1
odds["significatif"] = (odds["ic_95_bas"] > 1) | (odds["ic_95_haut"] < 1)
couleurs = np.where(
    odds["significatif"],
    np.where(odds["odds_ratio"] > 1, OR, MARINE),
    GRIS,
)

fig, ax = plt.subplots(figsize=(9, 7))
lignes = np.arange(len(odds))

# Le trait de l'intervalle de confiance, puis le point de l'odds ratio
ax.hlines(lignes, odds["ic_95_bas"], odds["ic_95_haut"], colors=couleurs, linewidth=2.5)
ax.scatter(odds["odds_ratio"], lignes, color=couleurs, s=60, zorder=3)

# La ligne de référence : odds ratio = 1, aucun effet
ax.axvline(1, color="#5C6B7A", linestyle="--", linewidth=1)

# La valeur de chaque odds ratio, à droite de son intervalle
for i, ligne in odds.iterrows():
    valeur = f"{ligne['odds_ratio']:.2f}".replace(".", ",")
    if ligne["odds_ratio"] >= 1:
        ax.text(ligne["ic_95_haut"] * 1.08, i, valeur, va="center", ha="left",
                fontsize=9, color="#333333")
    else:
        ax.text(ligne["ic_95_bas"] / 1.08, i, valeur, va="center", ha="right",
                fontsize=9, color="#333333")

# Axe horizontal en échelle logarithmique, avec des graduations lisibles
ax.set_xscale("log")
graduations = [0.5, 1, 2, 5, 10]
ax.xaxis.set_major_locator(FixedLocator(graduations))
ax.xaxis.set_major_formatter(FixedFormatter(["0,5", "1", "2", "5", "10"]))
ax.xaxis.set_minor_locator(FixedLocator([]))
ax.set_xlim(0.4, 18)

ax.set_yticks(lignes)
ax.set_yticklabels(odds["libelle"])
ax.set_xlabel("Rapport des chances (échelle logarithmique)")
ax.set_title(
    "Un contact précédent multiplie par 11 les chances de souscrire",
    loc="left", fontsize=13, fontweight="bold", color=MARINE,
)
for cote in ("top", "right"):
    ax.spines[cote].set_visible(False)

ax.legend(
    handles=[
        Patch(color=OR, label="Augmente les chances"),
        Patch(color=MARINE, label="Diminue les chances"),
        Patch(color=GRIS, label="Pas d'effet significatif"),
    ],
    loc="lower right", frameon=False, fontsize=9,
)

fig.text(
    0.01, 0.01,
    "Régression logistique sur 40 858 clients. Références : 30-44 ans, employé administratif, "
    "téléphone fixe.\nTraits : intervalle de confiance à 95 %. Durée de l'appel exclue "
    "(connue seulement après l'appel).",
    fontsize=8, color="#5C6B7A",
)

plt.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(DOCS / "odds_ratios.png", dpi=200)
print("Graphique écrit :", DOCS / "odds_ratios.png")