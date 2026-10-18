import pandas as pd

sources = {
    "SAS": "data/sas_kpi_metier.csv",
    "Dataiku": "data/dataiku_kpi_metier.csv",
    "Python": "data/python_kpi_metier.csv",
}

for nom, chemin in sources.items():
    df = pd.read_csv(chemin)
    print(f"===== {nom} =====")
    print(df.head(3))
    print(df.dtypes)
    print()