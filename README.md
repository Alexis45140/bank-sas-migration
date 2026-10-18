# Migration d'un traitement SAS vers Dataiku et Python

Un traitement de données bancaires réécrit en SAS, puis dans Dataiku et en Python. Une recette automatisée prouve que les trois versions produisent les mêmes indicateurs, et un tableau de bord Power BI présente les résultats.

![Tableau de bord Power BI de la campagne de dépôt à terme](powerbi/dashboard.png)

**En bref**

- Un même traitement (nettoyage et deux indicateurs) mis en œuvre dans SAS, Dataiku et Python sur 41 188 clients.
- Une recette Python compare automatiquement les sorties : Dataiku et Python sont identiques à SAS (tolérance relative 1e-6).
- Six pièges de migration documentés, de l'échantillonnage de Dataiku aux paramètres régionaux de Power BI.

## Sommaire

- [Contexte](#contexte)
- [Données](#données)
- [Démarche](#démarche)
- [Règles de traitement](#règles-de-traitement)
- [Recette de migration](#recette-de-migration)
- [Résultats clés](#résultats-clés)
- [Pièges rencontrés et solutions](#pièges-rencontrés-et-solutions)
- [Limites](#limites)
- [Reproduire le projet](#reproduire-le-projet)
- [Outils](#outils)
- [Contact](#contact)

## Contexte

Les banques ont longtemps fait tourner leurs traitements de données sur SAS : reporting, scoring, ciblage commercial. Beaucoup les migrent aujourd'hui vers des plateformes comme Dataiku ou vers Python, pour trois raisons principales : le coût des licences, la difficulté à recruter des profils SAS, et la volonté de rapprocher les traitements des outils de data science et du cloud.

Une migration n'a de valeur que si elle reproduit exactement les chiffres de l'ancien système. Un indicateur qui change après migration peut fausser un pilotage commercial ou un reporting réglementaire. Ce projet reproduit cette situation à petite échelle : un traitement SAS de référence, sa traduction dans deux outils cibles, puis une recette automatisée qui compare les sorties.

## Données

| | |
|---|---|
| Source | [UCI Machine Learning Repository, Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing) |
| Fichier | `bank-additional-full.csv` (séparateur `;`) |
| Volume | 41 188 clients, 21 colonnes |
| Contexte | campagnes de télémarketing d'une banque portugaise pour un dépôt à terme, 2008-2010 |
| Variable cible | `y` : le client a-t-il souscrit le dépôt à terme (`yes` / `no`) |
| Licence | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

Principales variables utilisées : `age`, `job` (métier), `marital`, `education`, `default` (défaut de crédit), `housing`, `loan`, `contact` (portable ou fixe), `campaign` (nombre d'appels pendant la campagne), `pdays` (jours écoulés depuis un contact lors d'une campagne précédente, 999 signifiant « jamais contacté ») et `y`.

Référence :

> Moro, S., Cortez, P. et Rita, P. (2014). A data-driven approach to predict the success of bank telemarketing. *Decision Support Systems*, 62, 22-31. https://doi.org/10.1016/j.dss.2014.03.001

La licence CC BY 4.0 autorise la redistribution du fichier dans ce dépôt (`data/raw/`), avec citation des auteurs.

## Démarche

1. **SAS, la référence.** Le script [`sas/01_traitement_sas.sas`](sas/01_traitement_sas.sas), exécuté sous SAS OnDemand for Academics, enchaîne `proc import`, une étape DATA pour le nettoyage, deux `proc sql` pour les indicateurs et `proc export` vers CSV.
2. **Dataiku, la migration visuelle.** Le même traitement est reconstruit sur Dataiku Cloud avec une recette Préparer (cinq étapes) suivie de deux recettes Grouper.
3. **Python, la migration en code.** [`python/traitement.py`](python/traitement.py) traduit le traitement en pandas, puis [`python/recette.py`](python/recette.py) compare automatiquement les trois versions.
4. **Power BI, la restitution.** Le tableau de bord s'appuie sur `data/processed/bank_clean.csv` et utilise un thème aux couleurs d'une banque ([`powerbi/theme_banque.json`](powerbi/theme_banque.json)).

**Flow Dataiku**

![Flow Dataiku : bank_raw, recette Préparer, bank_clean, puis deux recettes Grouper vers kpi_contact et kpi_metier](dataiku/flow.png)

**Résumé de la recette Préparer**

![Résumé de la recette Préparer : les cinq étapes de nettoyage](dataiku/recette_preparer.png)

### Arborescence du dépôt

```
bank-sas-migration/
├── data/
│   ├── raw/bank-additional-full.csv       données UCI d'origine
│   └── processed/bank_clean.csv           données nettoyées (sortie de traitement.py)
├── outputs/
│   ├── sas_kpi_metier.csv                 indicateurs exportés par SAS (référence)
│   ├── sas_kpi_contact.csv
│   ├── dataiku_kpi_metier.csv             indicateurs exportés par Dataiku
│   ├── dataiku_kpi_contact.csv
│   ├── python_kpi_metier.csv              indicateurs produits par traitement.py
│   ├── python_kpi_contact.csv
│   └── archive/                           premiers exports SAS, avec formats (test d'échec)
├── sas/
│   └── 01_traitement_sas.sas
├── dataiku/
│   ├── flow.png
│   └── recette_preparer.png
├── python/
│   ├── traitement.py                      nettoyage et indicateurs
│   ├── recette.py                         comparaison SAS / Dataiku / Python
│   ├── inspection.py                      aperçu des colonnes et des types des trois exports
│   └── diagnostic.py                      contrôle rapide d'un export SAS
├── powerbi/
│   ├── bank_dashboard.pbix
│   ├── theme_banque.json
│   └── dashboard.png
├── requirements.txt
└── README.md
```

## Règles de traitement

Les cinq règles sont appliquées dans le même ordre dans les trois outils.

| # | Règle | SAS | Dataiku (recette Préparer) | Python (pandas) |
|---|---|---|---|---|
| 1 | `unknown` devient une valeur manquante sur `job`, `marital`, `education`, `default`, `housing`, `loan` | tableau `array txt{*}` parcouru par une boucle : `if txt{i} = "unknown" then txt{i} = "";` | Remplacer `unknown` par `''` dans 6 colonnes | `clean[colonnes_texte].replace("unknown", pd.NA)` |
| 2 | `souscrit` vaut 1 si `y = "yes"`, sinon 0 | `souscrit = (y = "yes");` | Formule `if(y == "yes", 1, 0)` | `(clean["y"] == "yes").astype(int)` |
| 3 | `deja_contacte` vaut 1 si `pdays` est différent de 999, calculé avant la règle 4 | `deja_contacte = (pdays ne 999);` | Formule `if(pdays != 999, 1, 0)` | `(clean["pdays"] != 999).astype(int)` |
| 4 | `pdays = 999` devient une valeur manquante | `if pdays = 999 then pdays = .;` | Remplacer `999` par `''` dans `pdays` | `clean["pdays"].mask(clean["pdays"] == 999)` |
| 5 | `tranche_age` : `1. <30`, `2. 30-44`, `3. 45-59`, `4. 60+` | `if age < 30 then ...; else if age < 45 then ...;` | Formule `if(age < 30, "1. <30", if(age < 45, ...))` | `pd.cut(age, bins=[0, 30, 45, 60, 200], right=False, labels=[...])` |

L'ordre des règles 3 et 4 est imposé : une fois 999 remplacé par une valeur manquante, l'information « jamais contacté » ne pourrait plus être calculée. Les préfixes numérotés de `tranche_age` garantissent un tri correct dans tous les outils ; sans eux, `<30` serait classé après `60+`.

Deux indicateurs sont ensuite calculés à partir de la table nettoyée :

| Indicateur | Contenu | SAS | Dataiku | Python |
|---|---|---|---|---|
| `kpi_metier` | par métier, métiers inconnus exclus : `nb_clients`, `nb_souscriptions`, `taux_souscription`, `nb_appels_moyen` | `proc sql` avec `where job ne ""` et `group by job` | recette Grouper sur `job`, pré-filtre « `job` est défini » | `dropna(subset=["job"]).groupby("job").agg(...)` |
| `kpi_contact` | par `deja_contacte` : `nb_clients`, `taux_souscription` | `proc sql` avec `group by deja_contacte` | recette Grouper sur `deja_contacte` | `groupby("deja_contacte").agg(...)` |

Le taux de souscription est la moyenne de `souscrit` et le nombre d'appels moyen est la moyenne de `campaign`.

## Recette de migration

[`python/recette.py`](python/recette.py) compare les indicateurs de Dataiku et de Python à ceux de SAS, pris comme référence. Pour chaque indicateur, le script :

1. lit les trois fichiers CSV du dossier `outputs/` ;
2. remet les colonnes dans un ordre fixe, car Dataiku les exporte dans un autre ordre que SAS et Python ;
3. trie les lignes sur la clé (`job` ou `deja_contacte`), car SAS et Python trient par taux décroissant alors que Dataiku trie par métier ;
4. compare chaque version à SAS avec `pandas.testing.assert_frame_equal`, en ignorant les seules différences de type (`check_dtype=False`) et avec une tolérance relative de 1e-6 (`rtol=1e-6`), car SAS arrondit à 10 décimales à l'export (`0.3142857143`) alors que pandas en écrit 16 (`0.3142857142857143`) ;
5. affiche `identique`, ou `ÉCART` suivi du détail de la première différence.

Résultat obtenu :

```
===== Taux par métier =====
Dataiku vs SAS : identique
Python vs SAS : identique

===== Effet d'un contact précédent =====
Dataiku vs SAS : identique
Python vs SAS : identique
```

**Test d'échec.** Une recette qui répond toujours « identique » ne prouve rien. Le premier export SAS, réalisé avec les formats d'affichage (voir le piège 4), est conservé dans `outputs/archive/sas_kpi_metier_ancien.csv`. Pris comme référence, il fait bien échouer la recette :

```
Python vs SAS : ÉCART
DataFrame.iloc[:, 3] (column name="taux_souscription") are different
...
At positional index 0, first diff: 13.0% != 0.1297255805027825
```

## Résultats clés

Sur les 41 188 clients contactés, 4 640 ont souscrit un dépôt à terme, soit un taux global de **11,27 %**, avec en moyenne 2,6 appels par client.

| Constat | Chiffres |
|---|---|
| Les étudiants et les retraités souscrivent le plus | étudiants 31,4 %, retraités 25,2 % |
| Les ouvriers sont très sollicités mais souscrivent le moins | 6,9 %, alors qu'ils forment le 2e groupe le plus appelé (9 254 clients) |
| Un client déjà contacté lors d'une campagne précédente souscrit environ 7 fois plus | 63,8 % (1 515 clients) contre 9,3 % (39 673 clients) |
| Les moins de 30 ans et les 60 ans et plus répondent le mieux | moins de 30 ans 16,3 %, 30-44 ans 9,6 %, 45-59 ans 9,2 %, 60 ans et plus 39,6 % |
| Le portable convertit près de 3 fois mieux que le fixe | portable 14,7 %, fixe 5,2 % |
| La colonne `default` est peu exploitable | 3 valeurs `yes` seulement et environ 21 % de valeurs inconnues |

### Recommandations métier

1. **Recontacter en priorité les clients déjà approchés** : 63,8 % de souscription, contre 9,3 % pour un premier contact.
2. **Cibler les moins de 30 ans et les plus de 60 ans**, dont les taux (16,3 % et 39,6 %) dépassent nettement la moyenne de 11,27 %.
3. **Réduire les appels aux ouvriers** : deuxième population la plus appelée, elle affiche le taux le plus faible (6,9 %).
4. **Privilégier le portable** : 14,7 % de souscription, contre 5,2 % sur le fixe.

Ces recommandations doivent être lues avec les [limites](#limites) de l'analyse.

## Pièges rencontrés et solutions

### 1. L'échantillon Dataiku donnait une fausse image de `pdays`

Dataiku analyse par défaut un échantillon formé des 10 000 premières lignes. Le fichier étant trié par date, cet échantillon indiquait 100 % de `pdays = 999`, contre 96,3 % sur l'ensemble des 41 188 lignes. Avant de tirer une conclusion d'un profil de colonne, il faut passer l'échantillon en mode aléatoire ou travailler sur le jeu complet.

### 2. Recette Grouper : « Nombre » ou « Somme »

Dans la recette Grouper, l'agrégation « Nombre » compte les lignes non vides. Appliquée à `souscrit`, qui vaut toujours 0 ou 1, elle renvoie le nombre de clients et non le nombre de souscriptions. Le nombre de souscriptions s'obtient avec « Somme », qui additionne les 1.

### 3. Pré-filtre inversé

Le pré-filtre chargé d'exclure les métiers inconnus avait été réglé sur « N'est pas défini » au lieu de « Est défini ». La sortie ne contenait plus qu'une seule ligne, celle des 330 clients au métier inconnu, au lieu des 11 métiers attendus. Inverser la condition a rétabli le résultat.

### 4. `proc export` écrit les valeurs formatées

`proc export` exporte les valeurs telles qu'elles sont affichées, formats compris. Le format `percent8.1` a produit le texte `31.4%` au lieu d'un nombre, et le format `8.1` a arrondi le nombre moyen d'appels des étudiants de 2,104 à 2,1. La correction consiste à retirer les formats dans une étape DATA juste avant l'export (`format taux_souscription nb_appels_moyen;`), en les conservant pour l'affichage dans SAS.

### 5. Une session SAS expirée a produit un export vide

Après l'expiration de la session SAS OnDemand, une étape DATA s'est exécutée en erreur et a créé une table vide, que `proc export` a écrite sans la moindre alerte. Le script [`python/diagnostic.py`](python/diagnostic.py), qui affiche les colonnes et les premières lignes d'un export, a révélé le problème. Depuis, le journal SAS et le contenu de chaque export sont contrôlés avant toute comparaison.

### 6. Power BI en paramètres régionaux français

Avec des paramètres régionaux français, la détection automatique des types de Power Query a interprété `emp.var.rate` (valeur `1.1`) comme une date. La correction consiste à typer les colonnes dans le code M en précisant la culture du fichier source, selon ce principe :

```
Table.TransformColumnTypes(Source, {{"emp.var.rate", type number}}, "en-US")
```

## Limites

- **Corrélation n'est pas causalité.** Le taux de 63,8 % des clients déjà contactés ne prouve pas que le contact précédent provoque la souscription : ces clients ont pu être rappelés justement parce qu'ils s'étaient montrés intéressés. Seule une campagne test avec un groupe témoin permettrait de mesurer l'effet propre du recontact.
- **Petit effectif des étudiants.** Le taux de 31,4 % repose sur 875 clients seulement, soit environ 2 % de la base. Il est moins robuste que les taux des grands groupes et doit être confirmé sur d'autres campagnes.
- **`duration` à exclure de tout modèle prédictif.** La durée de l'appel n'est connue qu'une fois l'appel terminé, quand l'issue est déjà connue. L'utiliser pour prédire la souscription serait une fuite de données : le modèle paraîtrait très performant mais ne pourrait pas servir à décider qui appeler.

## Reproduire le projet

Prérequis : Python 3.11 ou plus récent (projet testé avec Python 3.14 et pandas 3.0.5).

```bash
git clone https://github.com/Alexis45140/bank-sas-migration.git
cd bank-sas-migration
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Lancer ensuite les scripts :

```bash
python python/traitement.py    # nettoyage et indicateurs : data/processed/ et outputs/python_*
python python/recette.py       # comparaison SAS / Dataiku / Python
python python/inspection.py    # aperçu des trois exports kpi_metier
python python/diagnostic.py    # contrôle de l'export SAS kpi_metier
```

Les scripts repèrent la racine du dépôt à partir de leur propre emplacement : ils fonctionnent quel que soit le dossier d'où on les lance.

Pour les autres outils :

- **SAS** : charger `data/raw/bank-additional-full.csv` dans SAS Studio (SAS OnDemand for Academics), remplacer les chemins `/home/u64631998/bank/` du script par votre propre espace, puis exécuter `sas/01_traitement_sas.sas`.
- **Dataiku** : le projet Dataiku n'est pas exporté ; les captures du dossier `dataiku/` et le tableau des règles ci-dessus permettent de reconstruire le Flow.
- **Power BI** : ouvrir `powerbi/bank_dashboard.pbix` dans Power BI Desktop, faire pointer la source vers `data/processed/bank_clean.csv` de votre copie du dépôt (Accueil > Transformer les données > Paramètres de la source de données), puis actualiser. Le thème s'importe depuis `powerbi/theme_banque.json` (Affichage > Thèmes > Parcourir les thèmes).

## Outils

| Outil | Rôle |
|---|---|
| SAS OnDemand for Academics | traitement de référence |
| Dataiku Cloud | migration en mode visuel |
| Python 3.14, pandas 3.0.5 | migration en code et recette automatisée |
| Power BI Desktop | tableau de bord |

## Contact

<div align="center">

### Alexis Claudeon
**Data Analyst | Analytics Engineer junior**

[![GitHub](https://img.shields.io/badge/GitHub-Alexis45140-181717?logo=github&logoColor=white)](https://github.com/Alexis45140)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-alexis--claudeon-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/alexis-claudeon)

</div>
