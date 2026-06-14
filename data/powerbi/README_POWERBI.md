# Exports Power BI

Ce dossier contient les CSV charges dans Power BI Desktop pour le projet **Analyse Mobilite Rhone**.

Ces fichiers ont ete generes avec :

```bash
python scripts/build_powerbi_exports.py
```

## Format des CSV

| Parametre | Valeur |
|---|---|
| Separateur de colonnes | `;` |
| Separateur decimal | `,` |
| Encodage | UTF-8 avec BOM |
| Dates | `AAAA-MM-JJ` |
| Date-heures | `AAAA-MM-JJ HH:MM:SS` |

Ce format est volontairement adapte a Power BI Desktop en francais.

## Tables de faits

| Fichier | Role |
|---|---|
| `fact_trajets.csv` | Trajets detailles issus du RPC filtre |
| `fact_comptages.csv` | Mesures horaires de comptage Grand Lyon |
| `fact_meteo_jour.csv` | Observations meteo quotidiennes |
| `fact_stations_taxi.csv` | Stations taxi et capacites |
| `bridge_chantier_date_commune.csv` | Chantiers actifs par jour et commune |

## Dimensions principales

| Fichier | Role |
|---|---|
| `dim_date.csv` | Date commune pour comptages, meteo et chantiers |
| `dim_date_depart.csv` | Date de depart des trajets |
| `dim_date_arrivee.csv` | Date d'arrivee estimee |
| `dim_tranche_horaire.csv` | Tranches horaires generiques |
| `dim_tranche_depart.csv` | Tranches horaires de depart |
| `dim_tranche_arrivee.csv` | Tranches horaires d'arrivee |
| `dim_commune.csv` | Communes enrichies |
| `dim_commune_depart.csv` | Communes de depart |
| `dim_commune_arrivee.csv` | Communes d'arrivee |
| `dim_secteur.csv` | Secteurs geographiques par trajet |
| `dim_tarif_taxi.csv` | Tarifs taxi A/B/C/D |
| `dim_site_comptage.csv` | Sites de comptage |
| `dim_channel_comptage.csv` | Canaux de comptage |
| `dim_station_meteo.csv` | Stations meteo |
| `dim_chantier.csv` | Chantiers |

## Decisions techniques

- `journey_id` n'est pas utilise comme cle primaire stricte : le modele utilise `trajet_ligne_id`.
- `date_heure_arrivee_estimee` est calculee a partir du depart et de la duree.
- Les tranches horaires sont codees de 1 a 6 pour permettre un tri propre.
- Les colonnes latitude/longitude sont separees pour les visuels cartographiques Power BI.
- Les relations doivent rester de type dimension `1` vers fact `*`.
- Les tables de faits ne doivent pas etre reliees directement entre elles.

## Cartographie

Pour les cartes Power BI :

- declarer les champs `latitude*` en categorie **Latitude** ;
- declarer les champs `longitude*` en categorie **Longitude** ;
- utiliser `dim_secteur` quand une lecture par rue/secteur est plus claire que des points GPS seuls.
