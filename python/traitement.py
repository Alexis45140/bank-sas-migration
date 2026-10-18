from pathlib import Path

import pandas as pd

# Racine du dépôt, quel que soit le dossier d'où on lance le script
RACINE = Path(__file__).resolve().parent.parent

# 1. Import (l'équivalent de proc import)
df = pd.read_csv(RACINE / "data" / "raw" / "bank-additional-full.csv", sep=";")
print("Lignes, colonnes :", df.shape)

# 2. Nettoyage (l'équivalent de l'étape DATA)
clean = df.copy()

colonnes_texte = ["job", "marital", "education", "default", "housing", "loan"]
clean[colonnes_texte] = clean[colonnes_texte].replace("unknown", pd.NA)

clean["souscrit"] = (clean["y"] == "yes").astype(int)

# Toujours dans cet ordre : on lit le 999 avant de l'effacer
clean["deja_contacte"] = (clean["pdays"] != 999).astype(int)
clean["pdays"] = clean["pdays"].mask(clean["pdays"] == 999)

clean["tranche_age"] = pd.cut(
    clean["age"],
    bins=[0, 30, 45, 60, 200],
    right=False,
    labels=["1. <30", "2. 30-44", "3. 45-59", "4. 60+"],
)

# 3. Indicateur 1 : par métier (l'équivalent du proc sql)
kpi_metier = (
    clean.dropna(subset=["job"])
    .groupby("job")
    .agg(
        nb_clients=("souscrit", "size"),
        nb_souscriptions=("souscrit", "sum"),
        taux_souscription=("souscrit", "mean"),
        nb_appels_moyen=("campaign", "mean"),
    )
    .reset_index()
    .sort_values("taux_souscription", ascending=False)
)

# 4. Indicateur 2 : selon un contact précédent
kpi_contact = (
    clean.groupby("deja_contacte")
    .agg(
        nb_clients=("souscrit", "size"),
        taux_souscription=("souscrit", "mean"),
    )
    .reset_index()
)

print(kpi_metier)
print(kpi_contact)

# 5. Export
kpi_metier.to_csv(RACINE / "outputs" / "python_kpi_metier.csv", index=False)
kpi_contact.to_csv(RACINE / "outputs" / "python_kpi_contact.csv", index=False)
clean.to_csv(RACINE / "data" / "processed" / "bank_clean.csv", index=False)