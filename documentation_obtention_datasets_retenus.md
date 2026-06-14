# Obtention et selection des datasets

Projet : **Analyse Mobilite Rhone**
Periode : **janvier a mars 2026**

## Cadrage de l'analyse

Le projet etudie le potentiel de mobilite dans le Rhone et la Metropole de Lyon a partir de donnees ouvertes.

Le besoin analytique est operationnel : comprendre les zones de concentration des deplacements, les horaires de tension et la rentabilite theorique des trajets pour prioriser les secteurs ou une presence terrain aurait le plus de sens.

En l'absence de donnees commerciales ouvertes suffisamment detaillees, j'ai construit une approche indirecte a partir de sources publiques. L'objectif est de produire une lecture fiable du territoire sans extrapoler au-dela des signaux disponibles.

## Sujet retenu

**Analyse du potentiel de mobilite dans le Rhone a partir de donnees publiques ouvertes, janvier-mars 2026.**

Problematique :

**Comment transformer des donnees ouvertes de mobilite en outil d'aide a la decision pour identifier les zones, periodes et conditions favorables au deploiement d'une offre de transport dans le Rhone ?**

## Sources explorees

| Source | Decision | Raison |
|---|---|---|
| Registre de Preuve de Covoiturage | Retenu | Donnees de trajets individuels, horaires, distances, communes et coordonnees |
| Comptages Grand Lyon | Retenu | Gros volume horaire pour lire les rythmes de mobilite |
| Stations taxi Grand Lyon | Retenu | Offre taxi existante et couverture territoriale |
| Chantiers perturbants Grand Lyon | Retenu | Contexte de perturbation routiere |
| Meteo-France quotidienne | Retenu en version utile | Variables meteo exploitables par jour et station |
| Tarifs publics Rhone 2026 | Retenu | Base pour simuler un revenu theorique |
| Donnees commerciales detaillees | Ecarte | Donnees non disponibles en open data |
| Datasets taxis hors territoire | Ecarte du modele | Utiles comme reference de structure, mais hors perimetre local |
| Flux temps reel divers | Ecarte ou secondaire | Pas toujours d'historique propre pour janvier-mars 2026 |

## Script de profiling

Le profiling a ete realise avec :

```bash
python scripts/profile_datasets.py
```

Ce script :

- telecharge ou interroge les sources publiques ;
- filtre les donnees sur janvier-mars 2026 ;
- garde les trajets dont le depart ou l'arrivee appartient a la Metropole de Lyon ;
- calcule les lignes, colonnes, valeurs vides, NA litteraux, completude et doublons ;
- extrait les fichiers intermediaires dans `data/processed` ;
- genere le dictionnaire de donnees dans `analysis/dictionnaire_donnees_profiling.md`.

Principales API et fichiers utilises dans le code :

```python
RPC_MONTHS = {
    "2026-01": ".../2026-01.csv",
    "2026-02": ".../2026-02.csv",
    "2026-03": ".../2026-03.csv",
}

URLS = {
    "stations_taxi": "https://data.grandlyon.com/geoserver/...",
    "chantiers_perturbants": "https://data.grandlyon.com/geoserver/...",
    "comptage_sites": "https://data.grandlyon.com/geoserver/...",
    "comptage_channels": "https://download.data.grandlyon.com/ws/rdata/...",
    "meteo_rr_t_vent": "https://object.files.data.gouv.fr/meteofrance/...",
}
```

## Resultats du profiling

| Dataset profile | Lignes | Colonnes | Completude globale | Doublons exacts | Decision |
|---|---:|---:|---:|---:|---|
| `rpc_trajets_covoiturage_lyon` | 74 831 | 27 | 100,00 % | 0 | Base centrale |
| `stations_taxi` | 113 | 16 | 96,90 % | 0 | Retenu |
| `chantiers_perturbants` | 94 | 19 | 84,88 % | 0 | Retenu |
| `comptage_sites` | 292 | 11 | 74,28 % | 0 | Retenu pour geolocalisation |
| `comptage_channels` | 1 471 | 19 | 68,03 % | 0 | Retenu pour description des capteurs |
| `comptage_mesures_jan_mar_2026` | 1 360 146 | 5 | 99,99 % | 0 | Retenu |
| `meteo_rr_t_vent_jan_mar_2026` | 1 620 | 60 | 54,13 % | 0 | Retenu, avec vigilance |
| `meteo_autres_jan_mar_2026` | 1 620 | 88 | 21,02 % | 0 | Ecarte du coeur du modele |
| `tarifs_taxi_rhone_2026_reference` | 4 | 7 | 100,00 % | 0 | Retenu |

## Volumes utiles

| Source | Janvier 2026 | Fevrier 2026 | Mars 2026 | Total |
|---|---:|---:|---:|---:|
| RPC national brut | 937 369 | 915 542 | 1 093 455 | 2 946 366 |
| RPC filtre Metropole de Lyon | 23 854 | 22 717 | 28 260 | 74 831 |
| Mesures de comptage Grand Lyon | 407 814 | 426 299 | 526 033 | 1 360 146 |

## Decisions de conservation

### Registre de Preuve de Covoiturage

Je l'ai retenu comme base centrale parce que c'est le seul dataset public qui ressemble a des trajets individuels : heure, distance, duree, commune de depart, commune d'arrivee et coordonnees arrondies.

Je n'ai pas supprime automatiquement les trajets similaires, car plusieurs lignes proches peuvent representer des trajets multi-passagers ou des trajets tres proches dans le temps.

### Comptages Grand Lyon

Les comptages ne remplacent pas les trajets, mais ils donnent une lecture de l'intensite generale de mobilite. Ils sont utiles pour comparer les rythmes horaires et consolider la lecture des pics.

### Stations taxi

Ce fichier est petit, propre et tres utile pour comparer la demande potentielle a l'offre taxi stationnaire. Je l'ai conserve tel quel en gardant les informations d'adresse, commune, capacite et geometrie.

### Chantiers perturbants

Les chantiers apportent un contexte metier : une zone forte peut etre influencee par des travaux. Le volume est faible, donc le dataset est facile a controler et a integrer via une table pont par date et commune.

### Meteo

J'ai conserve la meteo quotidienne principale, meme si la completude globale est moyenne. Les variables utiles restent exploitables pour une analyse de contexte : pluie, temperatures et vent. Le fichier des autres parametres est trop incomplet pour etre central.

### Tarifs publics 2026

La grille tarifaire publique a ete saisie comme reference de calcul. Elle ne donne pas un chiffre d'affaires reel, mais elle permet d'estimer un revenu theorique comparable entre trajets.

## Cles relationnelles retenues

| Source | Cible | Cle |
|---|---|---|
| RPC trajets | communes | `journey_start_insee` / `journey_end_insee` |
| RPC trajets | dates | date de depart et date d'arrivee estimee |
| RPC trajets | tranches horaires | heure de depart et heure d'arrivee estimee |
| RPC trajets | tarifs publics | tarif A/B selon heure, dimanche et jour ferie |
| Comptage mesures | channels | `channel_id` |
| Channels | sites de comptage | `site_id` |
| Meteo | dates | `AAAAMMJJ` |
| Meteo | stations meteo | `NUM_POSTE` |
| Chantiers | dates et communes | date entre debut/fin + code INSEE |

## Limites assumees

- Le covoiturage n'est pas une course professionnelle. C'est un proxy de mobilite, pas une mesure directe d'une demande commerciale.
- Les coordonnees RPC sont arrondies : elles sont suffisantes pour une lecture sectorielle, pas pour une adresse exacte.
- Le revenu estime est theorique : il applique une grille tarifaire simplifiee sans supplements, attente reelle ou conditions de circulation.
- La meteo est integree au jour et non au trajet minute par minute.

## Fichiers produits

| Fichier | Role |
|---|---|
| `analysis/profiling_resultats.json` | Resultats bruts du profiling |
| `analysis/dictionnaire_donnees_profiling.md` | Dictionnaire de donnees et controles qualite |
| `data/processed/rpc_trajets_covoiturage_metropole_lyon_2026_01_03.csv` | RPC filtre |
| `data/processed/chantiers_perturbants_jan_mar_2026.csv` | Chantiers filtres |
| `data/processed/meteo_rr_t_vent_jan_mar_2026.csv` | Meteo principale filtree |
| `data/processed/tarifs_taxi_rhone_2026_reference.csv` | Reference tarifaire |

Cette selection permet de construire une analyse de mobilite ouverte, reproductible et exploitable dans Power BI, en restant sur des sources publiques.
