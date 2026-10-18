from pathlib import Path

import pandas as pd

# Racine du dépôt, quel que soit le dossier d'où on lance le script
OUTPUTS = Path(__file__).resolve().parent.parent / "outputs"

sources = {
    "SAS": OUTPUTS / "sas_kpi_metier.csv",
    "Dataiku": OUTPUTS / "dataiku_kpi_metier.csv",
    "Python": OUTPUTS / "python_kpi_metier.csv",
}

for nom, chemin in sources.items():
    df = pd.read_csv(chemin)
    print(f"===== {nom} =====")
    print(df.head(3))
    print(df.dtypes)
    print()