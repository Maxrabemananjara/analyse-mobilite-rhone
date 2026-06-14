# Transformation des donnees et exports Power BI

Projet : **Analyse Mobilite Rhone**
Etape : **passage des donnees profilees a un modele Power BI exploitable**

## Objectif

Apres le profiling, j'ai construit les tables chargees dans Power BI. Le but n'etait pas seulement de nettoyer les fichiers, mais de produire un petit datawarehouse analytique : des facts detaillees, des dimensions lisibles et des cles stables.

Les CSV finaux sont dans :

```text
data/powerbi/
```

Les donnees intermediaires restent dans :

```text
data/processed/
analysis/
```

## Script utilise

La generation principale est faite avec :

```bash
python scripts/build_powerbi_exports.py
```

Le script lit les fichiers filtres, appelle certaines API Grand Lyon pour les referentiels, puis ecrit les CSV au format Power BI FR.

Extraits importants du code :

```python
START_DATE = date(2026, 1, 1)
END_DATE_EXCLUSIVE = date(2026, 4, 1)

TRANCHES = [
    (1, "00h-04h", 0, 4),
    (2, "04h-08h", 4, 8),
    (3, "08h-12h", 8, 12),
    (4, "12h-16h", 12, 16),
    (5, "16h-20h", 16, 20),
    (6, "20h-00h", 20, 24),
]
```

```python
def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
```

## Format Power BI retenu

Comme le rapport est construit dans Power BI Desktop en francais, j'ai exporte les CSV avec :

| Parametre | Valeur |
|---|---|
| Separateur de colonnes | `;` |
| Separateur decimal | `,` |
| Encodage | UTF-8 avec BOM |
| Dates | `AAAA-MM-JJ` |
| Date-heures | `AAAA-MM-JJ HH:MM:SS` |
| Noms de colonnes | snake_case, sans espaces |
| Coordonnees | latitude et longitude separees |

Ce format evite les erreurs de decimal dans Power BI FR et rend les fichiers rechargeables sans retraitement manuel.

## Choix de modelisation

J'ai retenu une constellation plutot qu'une seule table plate. Les raisons :

- garder les trajets au niveau ligne ;
- eviter de dupliquer les libelles de date, commune et tranche horaire partout ;
- laisser Power BI faire les agregations ;
- limiter le DAX aux mesures utiles ;
- pouvoir ajouter les comptages, la meteo, les chantiers et les stations taxi sans relation fact-to-fact.

Regles appliquees :

- dimensions en `1` vers facts en `*` ;
- pas de lien direct entre tables de faits ;
- pas de lien direct entre dimensions ;
- cles techniques conservees dans les facts ;
- libelles et ordres de tri dans les dimensions.

## Tables generees

| Table | Lignes | Role |
|---|---:|---|
| `fact_trajets.csv` | 74 795 | Trajets detailles, distances, durees, revenu estime |
| `fact_comptages.csv` | 1 360 146 | Comptages horaires Grand Lyon |
| `fact_meteo_jour.csv` | 1 620 | Meteo quotidienne par station |
| `fact_stations_taxi.csv` | 113 | Stations taxi et capacite |
| `bridge_chantier_date_commune.csv` | 4 095 | Chantiers actifs par jour et commune |
| `dim_date.csv` | 90 | Date commune pour comptages, meteo et chantiers |
| `dim_date_depart.csv` | 90 | Date de depart des trajets |
| `dim_date_arrivee.csv` | 91 | Date d'arrivee estimee des trajets |
| `dim_tranche_horaire.csv` | 6 | Tranches horaires generiques |
| `dim_tranche_depart.csv` | 6 | Tranches horaires de depart |
| `dim_tranche_arrivee.csv` | 6 | Tranches horaires d'arrivee |
| `dim_commune.csv` | 385 | Communes enrichies |
| `dim_commune_depart.csv` | 385 | Communes de depart |
| `dim_commune_arrivee.csv` | 385 | Communes d'arrivee |
| `dim_secteur.csv` | 74 795 | Secteurs geographiques depart/arrivee par trajet |
| `dim_tarif_taxi.csv` | 4 | Tarifs taxi A/B/C/D |
| `dim_site_comptage.csv` | 292 | Sites de comptage |
| `dim_channel_comptage.csv` | 1 471 | Canaux de comptage |
| `dim_station_meteo.csv` | 18 | Stations Meteo-France |
| `dim_chantier.csv` | 94 | Detail des chantiers |

## Transformations metier

### Trajets

`fact_trajets.csv` garde le niveau le plus fin : une ligne par trajet conserve dans le modele.

J'ai ajoute :

- `trajet_ligne_id` comme cle technique ;
- `journey_id_occurrence` pour suivre les doublons de `journey_id` ;
- les dates de depart et d'arrivee estimee ;
- les IDs de jour de semaine et tranche horaire ;
- les IDs de commune depart/arrivee ;
- la distance en metres et kilometres ;
- une estimation de revenu.

Decision importante :

```python
arrival_dt = start_dt + timedelta(minutes=duration_min)
```

Le champ `journey_end_datetime` du RPC filtre est identique au depart. J'ai donc garde les champs sources pour tracabilite, mais l'analyse utilise une arrivee estimee a partir de la duree declaree.

### Tranches horaires

Les tranches ont ete creees pour alimenter les heatmaps et les filtres :

| ID | Libelle |
|---:|---|
| 1 | 00h-04h |
| 2 | 04h-08h |
| 3 | 08h-12h |
| 4 | 12h-16h |
| 5 | 16h-20h |
| 6 | 20h-00h |

Chaque dimension contient aussi `ordre_tranche`, ce qui evite un tri alphabetique dans Power BI.

### Dates

`dim_date.csv` contient les colonnes classiques :

- annee ;
- trimestre ;
- mois numero ;
- mois libelle ;
- jour du mois ;
- jour de semaine ;
- ordre du jour ;
- weekend flag.

J'ai ensuite ajoute des colonnes de lecture par semaine du mois pour faciliter la page temporelle :

- `semaine_mois_numero` ;
- `semaine_mois_libelle` ;
- `mois_semaine_libelle` ;
- `mois_semaine_ordre`.

### Communes

`dim_commune.csv` a ete enrichie avec des informations administratives et de geocodage :

- `region_libelle` ;
- `departement_libelle` ;
- `arrondissement_libelle` ;
- `commune_libelle_insee` ;
- `latitude` ;
- `longitude` ;
- `localisation_azure`.

J'ai conserve les colonnes d'origine pour ne pas casser le modele Power BI.

### Secteurs geographiques

La carte Power BI avait besoin d'un niveau plus lisible que les seules coordonnees. J'ai donc construit `dim_secteur.csv` a partir des coordonnees de depart et d'arrivee des trajets.

La table garde :

- `trajet_ligne_id` ;
- latitude/longitude depart ;
- secteur depart ;
- methode et confiance du secteur depart ;
- latitude/longitude arrivee ;
- secteur arrivee ;
- methode et confiance du secteur arrivee.

Cette approche evite de modifier `fact_trajets.csv` et permet de relier la nouvelle dimension au modele sans reconstruire toutes les mesures.

### Revenu estime

L'estimation ne pretend pas etre un revenu taxi reel. Elle sert a comparer les trajets entre eux.

Principe :

```python
night_or_special = start_dt.hour < 7 or start_dt.hour >= 19 or start_day_id == 7
tarif_id = "B" if night_or_special else "A"
revenu = max(minimum, prise + distance_km * price_km)
```

Le scenario retient les tarifs A/B selon l'heure, le dimanche et le jour ferie, hors attente et supplements.

## Relations Power BI

Relations principales du modele :

| Dimension | Fact / bridge | Cle |
|---|---|---|
| `dim_date_depart` | `fact_trajets` | `date_depart_id` |
| `dim_date_arrivee` | `fact_trajets` | `date_arrivee_id` |
| `dim_tranche_depart` | `fact_trajets` | `tranche_depart_id` |
| `dim_tranche_arrivee` | `fact_trajets` | `tranche_arrivee_id` |
| `dim_commune_depart` | `fact_trajets` | `commune_depart_id` |
| `dim_commune_arrivee` | `fact_trajets` | `commune_arrivee_id` |
| `dim_tarif_taxi` | `fact_trajets` | `tarif_id` -> `tarif_id_estime` |
| `dim_date` | `fact_comptages` | `date_id` |
| `dim_tranche_horaire` | `fact_comptages` | `tranche_horaire_id` |
| `dim_site_comptage` | `fact_comptages` | `site_id` |
| `dim_channel_comptage` | `fact_comptages` | `channel_id` |
| `dim_date` | `fact_meteo_jour` | `date_id` |
| `dim_station_meteo` | `fact_meteo_jour` | `station_meteo_id` |
| `dim_date` | `bridge_chantier_date_commune` | `date_id` |
| `dim_commune` | `bridge_chantier_date_commune` | `commune_id` |
| `dim_chantier` | `bridge_chantier_date_commune` | `chantier_id` |
| `dim_commune` | `fact_stations_taxi` | `commune_id` |
| `dim_secteur` | `fact_trajets` | `trajet_ligne_id` |

## Controles effectues

Le script d'analyse post-export :

```bash
python scripts/analyse_powerbi_ready.py
```

sert a produire des indicateurs de controle et des premieres reponses :

- volume de trajets ;
- repartition par mois, jour et tranche ;
- top communes ;
- origine-destination ;
- revenu estime ;
- comparaison meteo/trajets ;
- comparaison chantiers/trajets ;
- couverture de l'offre stationnaire.

Les resultats sont stockes dans :

```text
analysis/analyse_reponses_questions.json
```

## Limites techniques

- `fact_comptages.csv` est volumineux : il est versionne avec Git LFS.
- Le modele Power BI reste volontairement simple ; la plupart des calculs sont faits par les tables preparees et quelques mesures.
- Les champs bruts utiles sont conserves pour tracer les decisions, meme quand des colonnes corrigees ou estimees sont ajoutees.

Cette etape transforme les donnees ouvertes en tables directement exploitables dans Power BI, sans faire croire que les donnees sont plus precises qu'elles ne le sont.
