from pathlib import Path

import pandas as pd

# Racine du dépôt, quel que soit le dossier d'où on lance le script
OUTPUTS = Path(__file__).resolve().parent.parent / "outputs"

df = pd.read_csv(OUTPUTS / "sas_kpi_metier.csv")
print("Colonnes :", list(df.columns))
print(df.head())