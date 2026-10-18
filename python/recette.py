from pathlib import Path

import pandas as pd

# Racine du dépôt, quel que soit le dossier d'où on lance le script
RACINE = Path(__file__).resolve().parent.parent
OUTPUTS = RACINE / "outputs"

def charger(chemin, cle, colonnes):
    """Lit un fichier, garde les colonnes dans un ordre fixe et trie les lignes."""
    df = pd.read_csv(chemin)
    return df[colonnes].sort_values(cle).reset_index(drop=True)

def comparer(nom_kpi, cle, colonnes, fichiers):
    print(f"===== {nom_kpi} =====")
    reference = charger(fichiers["SAS"], cle, colonnes)

    for nom, chemin in fichiers.items():
        if nom == "SAS":
            continue
        autre = charger(chemin, cle, colonnes)
        try:
            pd.testing.assert_frame_equal(
                reference, autre, check_dtype=False, rtol=1e-6
            )
            print(f"{nom} vs SAS : identique")
        except AssertionError as erreur:
            print(f"{nom} vs SAS : ÉCART")
            print(erreur)
    print()

comparer(
    "Taux par métier",
    cle="job",
    colonnes=["job", "nb_clients", "nb_souscriptions",
              "taux_souscription", "nb_appels_moyen"],
    fichiers={
        "SAS": OUTPUTS / "sas_kpi_metier.csv",
        "Dataiku": OUTPUTS / "dataiku_kpi_metier.csv",
        "Python": OUTPUTS / "python_kpi_metier.csv",
    },
)

comparer(
    "Effet d'un contact précédent",
    cle="deja_contacte",
    colonnes=["deja_contacte", "nb_clients", "taux_souscription"],
    fichiers={
        "SAS": OUTPUTS / "sas_kpi_contact.csv",
        "Dataiku": OUTPUTS / "dataiku_kpi_contact.csv",
        "Python": OUTPUTS / "python_kpi_contact.csv",
    },
)