from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import statsmodels.formula.api as smf

RACINE = Path(__file__).resolve().parent.parent
FICHIER = RACINE / "data" / "processed" / "bank_clean.csv"
SORTIES = RACINE / "outputs"
SORTIES.mkdir(exist_ok=True)

df = pd.read_csv(FICHIER)


def test_khi_deux(colonne):
    """Teste le lien entre une variable et la souscription."""
    tableau = pd.crosstab(df[colonne], df["souscrit"])
    khi2, p_valeur, ddl, _ = chi2_contingency(tableau)
    n = tableau.to_numpy().sum()
    v_cramer = np.sqrt(khi2 / (n * (min(tableau.shape) - 1)))
    print(f"\n===== {colonne} × souscription =====")
    print(tableau)
    print(f"Khi-deux : {khi2:,.1f} | degrés de liberté : {ddl} | p-valeur : {p_valeur:.2e}")
    print(f"V de Cramér : {v_cramer:.3f}")


# 1. Tests du khi-deux
test_khi_deux("deja_contacte")
test_khi_deux("contact")
test_khi_deux("tranche_age")

# 2. Régression logistique
donnees = df.dropna(subset=["job"]).copy()

formule = (
    "souscrit ~ deja_contacte"
    " + C(contact, Treatment('telephone'))"
    " + campaign"
    " + C(tranche_age, Treatment('2. 30-44'))"
    " + C(job, Treatment('admin.'))"
)
resultat = smf.logit(formule, data=donnees).fit()
print(resultat.summary())

intervalles = resultat.conf_int()
odds_ratios = pd.DataFrame({
    "odds_ratio": np.exp(resultat.params),
    "ic_95_bas": np.exp(intervalles[0]),
    "ic_95_haut": np.exp(intervalles[1]),
    "p_valeur": resultat.pvalues,
}).round(3)

print("\n===== Odds ratios =====")
print(odds_ratios)
print(f"\nPseudo R² de McFadden : {resultat.prsquared:.3f}")
print(f"Observations utilisées : {int(resultat.nobs):,}")

odds_ratios.to_csv(SORTIES / "odds_ratios.csv")