import pandas as pd

df = pd.read_csv("data/sas_kpi_metier.csv")
print("Colonnes :", list(df.columns))
print(df.head())