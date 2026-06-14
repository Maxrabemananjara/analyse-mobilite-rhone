# Dictionnaire de donnees et profiling - Mobilite Lyon

Periode analysee : **1er janvier 2026 au 31 mars 2026**.

Les statistiques ci-dessous sont calculees sur les donnees retenues pour le projet, c'est-a-dire filtrees sur le perimetre utile quand un filtre est indique.

## Synthese des tables

| Table | Lignes | Colonnes | Doublons exacts | Doublons de cle | Commentaire |
|---|---:|---:|---:|---|---|
| `rpc_trajets_covoiturage_lyon` | 74831 | 27 | 0 | journey_spatio_temporal_without_ids: 6525, journey_id: 5 | Filtre applique: depart ou arrivee dans 'Métropole de Lyon'. Fichier filtre ecrit: C:/Users/Utilisateur/Documents/New project/data/processed/rpc_trajets_covoiturage_metropole_lyon_ |
| `stations_taxi` | 113 | 16 | 0 | 0 |  |
| `chantiers_perturbants` | 94 | 19 | 0 | 0 | Filtre applique: chantier chevauchant janvier-mars 2026. |
| `comptage_sites` | 292 | 11 | 0 | 0 |  |
| `comptage_channels` | 1471 | 19 | 0 | 0 |  |
| `comptage_mesures_jan_mar_2026` | 1360146 | 5 | 0 | 0 | Fenetre interrogee: start_datetime >= 2026-01-01 et < 2026-04-01. |
| `meteo_rr_t_vent_jan_mar_2026` | 1620 | 60 | 0 | 0 | Filtre applique: observations quotidiennes du departement 69 entre 2026-01-01 et 2026-03-31. |
| `meteo_autres_jan_mar_2026` | 1620 | 88 | 0 | 0 | Filtre applique: observations quotidiennes du departement 69 entre 2026-01-01 et 2026-03-31. |
| `tarifs_taxi_rhone_2026_reference` | 4 | 7 | 0 | 0 | Reference saisie depuis la page tarifs maximum 2026 de la Metropole de Lyon. |

## Cles relationnelles proposees

| Source | Cle primaire / naturelle | Peut rejoindre | Cle de jointure | Usage |
|---|---|---|---|---|
| rpc_trajets_covoiturage_lyon | journey_id | stations_taxi | journey_start_insee / journey_end_insee -> insee | Analyse par commune et proximite geographique. |
| rpc_trajets_covoiturage_lyon | journey_id | meteo_rr_t_vent_jan_mar_2026 | journey_start_date -> AAAAMMJJ | Enrichissement meteo journalier. |
| rpc_trajets_covoiturage_lyon | journey_id | chantiers_perturbants | journey_start_date entre debutchantier et finchantier + zone/commune | Contexte perturbations travaux. |
| comptage_mesures_jan_mar_2026 | channel_id + start_datetime + end_datetime | comptage_channels | channel_id | Description du canal mesure. |
| comptage_channels | channel_id | comptage_sites | site_id | Localisation du site de comptage. |
| rpc_trajets_covoiturage_lyon | journey_id | tarifs_taxi_rhone_2026_reference | heure/jour -> tarif A/B/C/D | Simulation de revenu taxi. |

## `rpc_trajets_covoiturage_lyon`

- Lignes : **74831**
- Colonnes : **27**
- Doublons exacts : **0**
- Doublons de cle : `journey_spatio_temporal_without_ids` = 6525, `journey_id` = 5
- Note : Filtre applique: depart ou arrivee dans 'Métropole de Lyon'.
- Note : Fichier filtre ecrit: C:/Users/Utilisateur/Documents/New project/data/processed/rpc_trajets_covoiturage_metropole_lyon_2026_01_03.csv.

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `journey_id` | Identifiant unique du trajet passager-conducteur dans le registre. | 0 | 0 | 100.0% | `62675893`, `62675894` |
| `trip_id` | Identifiant operateur permettant de regrouper plusieurs passagers dans un meme vehicule. | 0 | 0 | 100.0% | `72bfd586539a5e08af93a1212da9adbef5a85a9880888dd6b1537377466a6ee9`, `65f8ac16e9aa9b5170b5b2da68d20c49c8ff09cab3445bd171cbd55fbb7100bc` |
| `journey_start_datetime` | Date et heure de depart avec fuseau horaire Paris. | 0 | 0 | 100.0% | `2026-01-01T02:10:00+0100`, `2026-01-01T02:40:00+0100` |
| `journey_start_date` | Date de depart au format AAAA-MM-JJ. | 0 | 0 | 100.0% | `2026-01-01`, `2026-01-02` |
| `journey_start_time` | Heure de depart arrondie, au format HH:MM:SS. | 0 | 0 | 100.0% | `01:10:00`, `01:40:00` |
| `journey_start_lon` | Longitude WGS84 du point de prise en charge, arrondie au niveau source. | 0 | 0 | 100.0% | `4.935`, `4.966` |
| `journey_start_lat` | Latitude WGS84 du point de prise en charge, arrondie au niveau source. | 0 | 0 | 100.0% | `45.688`, `45.775` |
| `journey_start_insee` | Code INSEE de la commune ou arrondissement de depart. | 0 | 0 | 100.0% | `69290`, `69275` |
| `journey_start_department` | Departement du point de depart. | 0 | 0 | 100.0% | `69`, `38` |
| `journey_start_town` | Commune ou arrondissement de depart. | 0 | 0 | 100.0% | `Saint-Priest`, `Décines-Charpieu` |
| `journey_start_towngroup` | EPCI/AOM du point de depart. | 0 | 0 | 100.0% | `Métropole de Lyon`, `Communauté de communes Beaujolais Pierres Dorées` |
| `journey_start_country` | Pays du point de depart. | 0 | 0 | 100.0% | `France` |
| `journey_end_datetime` | Date et heure d'arrivee avec fuseau horaire Paris. | 0 | 0 | 100.0% | `2026-01-01T02:10:00+0100`, `2026-01-01T02:40:00+0100` |
| `journey_end_date` | Date d'arrivee au format AAAA-MM-JJ. | 0 | 0 | 100.0% | `2026-01-01`, `2026-01-02` |
| `journey_end_time` | Heure d'arrivee arrondie, au format HH:MM:SS. | 0 | 0 | 100.0% | `01:30:00`, `02:00:00` |
| `journey_end_lon` | Longitude WGS84 du point de depose, arrondie au niveau source. | 0 | 0 | 100.0% | `4.970`, `4.900` |
| `journey_end_lat` | Latitude WGS84 du point de depose, arrondie au niveau source. | 0 | 0 | 100.0% | `45.775`, `45.702` |
| `journey_end_insee` | Code INSEE de la commune ou arrondissement d'arrivee. | 0 | 0 | 100.0% | `69275`, `69290` |
| `journey_end_department` | Departement du point d'arrivee. | 0 | 0 | 100.0% | `69`, `38` |
| `journey_end_town` | Commune ou arrondissement d'arrivee. | 0 | 0 | 100.0% | `Décines-Charpieu`, `Saint-Priest` |
| `journey_end_towngroup` | EPCI/AOM du point d'arrivee. | 0 | 0 | 100.0% | `Métropole de Lyon`, `Communauté de communes des Vallons du Lyonnais (CCVL)` |
| `journey_end_country` | Pays du point d'arrivee. | 0 | 0 | 100.0% | `France` |
| `passenger_seats` | Nombre de places reservees par le passager. | 0 | 0 | 100.0% | `1` |
| `operator_class` | Classe de preuve de covoiturage. | 0 | 0 | 100.0% | `C`, `A` |
| `journey_distance` | Distance declaree par l'operateur, en metres. | 0 | 0 | 100.0% | `14657`, `14659` |
| `journey_duration` | Duree declaree par l'operateur, arrondie en minutes. | 0 | 0 | 100.0% | `14`, `19` |
| `has_incentive` | Indique si le trajet est incite par une campagne ou un operateur. | 0 | 0 | 100.0% | `NON` |

## `stations_taxi`

- Lignes : **113**
- Colonnes : **16**
- Doublons exacts : **0**

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `FID` | Identifiant technique WFS. | 0 | 0 | 100.0% | `pvo_patrimoine_voirie.pvostationtaxi.4028`, `pvo_patrimoine_voirie.pvostationtaxi.4045` |
| `nom` | Code ou nom court de la station taxi. | 0 | 0 | 100.0% | `TAXGIV01`, `TAXFL01` |
| `adresse` | Adresse de la station. | 0 | 0 | 100.0% | `14, Quai Robichon-Malgontier`, `7, Avenue Maréchal Foch` |
| `commune` | Commune de localisation. | 0 | 0 | 100.0% | `Givors`, `Sainte-Foy-lès-Lyon` |
| `insee` | Code INSEE de la commune. | 0 | 0 | 100.0% | `69091`, `69202` |
| `nbemplacement` | Nombre d'emplacements taxi declares. | 2 | 0 | 98.23% | `1`, `2` |
| `telephone` | Presence d'un telephone ou information assimilee. | 3 | 0 | 97.35% | `false`, `true` |
| `separateurtaxi` | Type de separateur ou marquage de l'emplacement. | 4 | 0 | 96.46% | `Peinture`, `Autre` |
| `abri` | Presence d'un abri. | 2 | 0 | 98.23% | `false`, `true` |
| `panneau` | Presence d'un panneau. | 3 | 0 | 97.35% | `true`, `false` |
| `diodes` | Presence de diodes lumineuses. | 3 | 0 | 97.35% | `false`, `true` |
| `totem` | Presence d'un totem. | 3 | 0 | 97.35% | `false`, `true` |
| `observation` | Commentaire libre. | 36 | 0 | 68.14% | `Emplacement réservé ambulance et taxi`, `Arrêté n°830 le 25/06/19` |
| `validite` | Statut de validation de l'objet. | 0 | 0 | 100.0% | `Validé`, `En projet ou en cours de validation` |
| `gid` | Identifiant numerique Grand Lyon. | 0 | 0 | 100.0% | `4028`, `4045` |
| `the_geom` | Geometrie WKT en WGS84. | 0 | 0 | 100.0% | `POINT (4.777287412600262 45.58246772528973)`, `POINT (4.796192762937808 45.74917361266503)` |

## `chantiers_perturbants`

- Lignes : **94**
- Colonnes : **19**
- Doublons exacts : **0**
- Note : Filtre applique: chantier chevauchant janvier-mars 2026.

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `FID` | Identifiant technique WFS. | 0 | 0 | 100.0% | `pvo_patrimoine_voirie.pvochantierperturbant.412954`, `pvo_patrimoine_voirie.pvochantierperturbant.413894` |
| `nom` | Voie ou axe concerne. | 0 | 0 | 100.0% | `Rue Carnot`, `Avenue de l'Europe` |
| `nomchantier` | Nom du chantier. | 0 | 0 | 100.0% | `Travaux T10`, `Assainissement d'eau potable` |
| `commune1` | Commune principale concernee. | 0 | 0 | 100.0% | `Saint-Fons`, `Rillieux-la-Pape` |
| `insee` | Code INSEE de la commune. | 0 | 0 | 100.0% | `69199`, `69286` |
| `precisionlocalisation` | Precision textuelle sur la localisation. | 14 | 0 | 85.11% | `Ensemble de l'axe`, `de la Rue Edouard Vaillant jusqu'à l'Avenue Roger Salengro` |
| `debutchantier` | Date de debut du chantier. | 0 | 0 | 100.0% | `2026-01-05`, `2026-02-28` |
| `finchantier` | Date de fin prevue du chantier. | 0 | 0 | 100.0% | `2026-07-31`, `2026-04-30` |
| `descripchantierinternet` | Description publiee sur internet. | 68 | 0 | 27.66% | `Dans le sens Est-Ouest`, `De 7h à 17h, du lundi au vendredi` |
| `avancement` | Etat d'avancement. | 0 | 0 | 100.0% | `Chantier en cours` |
| `importance` | Niveau d'importance ou de perturbation. | 0 | 0 | 100.0% | `Chantier très perturbant`, `Chantier perturbant` |
| `typeperturbation` | Nature de la perturbation. | 0 | 0 | 100.0% | `Circulation interdite`, `Circulation réduite` |
| `intervenant` | Intervenant ou maitre d'ouvrage. | 0 | 0 | 100.0% | `Autre`, `Concessionnaire` |
| `validite` | Statut de validation. | 0 | 0 | 100.0% | `A vérifier` |
| `codeimportance` | Code numerique d'importance. | 0 | 0 | 100.0% | `1`, `2` |
| `document_joint` | Reference eventuelle d'un document joint. | 94 | 0 | 0.0% |  |
| `url_document` | URL du document joint. | 94 | 0 | 0.0% |  |
| `gid` | Identifiant numerique Grand Lyon. | 0 | 0 | 100.0% | `412954`, `413894` |
| `the_geom` | Geometrie WKT en WGS84. | 0 | 0 | 100.0% | `MULTIPOLYGON (((4.8553494290019374 45.708493659832534, 4.855949311766088 45.70831009484694, 4.856343225700489 45.7082292`, `MULTIPOLYGON (((4.88989985856637 45.812119208202766, 4.88987560948356 45.812169086157404, 4.891382202236321 45.812643773` |

## `comptage_sites`

- Lignes : **292**
- Colonnes : **11**
- Doublons exacts : **0**

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `FID` | Identifiant technique WFS. | 0 | 0 | 100.0% | `pvo_patrimoine_voirie.pvocomptagesite.100017792`, `pvo_patrimoine_voirie.pvocomptagesite.100017793` |
| `gid` |  | 0 | 0 | 100.0% | `100017792`, `100017793` |
| `site_id` | Identifiant du site de comptage. | 0 | 0 | 100.0% | `100017792`, `100017793` |
| `parent_site_id` |  | 267 | 0 | 8.56% | `69149.00072.12`, `69194.00013.02` |
| `fr_insee_code` |  | 0 | 0 | 100.0% | `69256`, `69275` |
| `xlong` |  | 0 | 0 | 100.0% | `4.93579835`, `4.9543418` |
| `ylat` |  | 0 | 0 | 100.0% | `45.77052963`, `45.77486441` |
| `external_ids` |  | 292 | 0 | 0.0% |  |
| `infrastructure_type` |  | 267 | 0 | 8.56% | `OTHER SPECIFIC SITE` |
| `the_geom` | Geometrie WKT en WGS84. | 0 | 0 | 100.0% | `POINT (4.935798346996308 45.770529629835806)`, `POINT (4.954341799020768 45.77486440927123)` |
| `site_name` |  | 0 | 0 | 100.0% | `Vaulx en Velin_Pont de la Sucrerie`, `Décines_Passerelle Nelson Mandela` |

## `comptage_channels`

- Lignes : **1471**
- Colonnes : **19**
- Doublons exacts : **0**

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `channel_id` | Identifiant du canal de mesure. | 0 | 0 | 100.0% | `69091.00052.02.00`, `69091.00052.02.01` |
| `channel_provider_id` | Identifiant du canal chez le fournisseur. | 0 | 0 | 100.0% | `69091.00052.02.00`, `69091.00052.02.01` |
| `site_provider_id` | Identifiant fournisseur du site rattache. | 48 | 0 | 96.74% | `100013842`, `100030470` |
| `site_id` | Identifiant du site rattache. | 0 | 0 | 100.0% | `69091.00052.02`, `69266.00611.02` |
| `mobility_type` | Type de mobilite mesuree. | 4 | 0 | 99.73% | `PEDESTRIAN`, `E-SCOOTER` |
| `comment` | Commentaire libre. | 17 | 0 | 98.84% | `Lyon 7_Pont Raymond Barre`, `Sentier de la marinade` |
| `counter_transmission_type` | Mode de transmission du compteur. | 1423 | 0 | 3.26% | `REMOTE TRANSMISSION` |
| `publication_transmission_type` | Mode de transmission pour publication. | 0 | 0 | 100.0% | `API` |
| `counter_type` | Type de compteur. | 1423 | 0 | 3.26% | `ACTIVE INFRARED`, `ACTIVE INFRARED,PIEZOELECTRIC SENSOR` |
| `direction` | Direction mesuree. | 1423 | 0 | 3.26% | `N`, `W` |
| `provider_direction_code` | Code direction chez le fournisseur. | 0 | 0 | 100.0% | `IN`, `OUT` |
| `provider_direction_name` | Nom direction chez le fournisseur. | 1423 | 0 | 3.26% | `JCDecaux` |
| `data_provider_name` | Nom du fournisseur de donnees. | 0 | 0 | 100.0% | `JCDecaux`, `EcoCounter` |
| `temporality` | Temporalite de la mesure. | 0 | 0 | 100.0% | `PERMANENT` |
| `started_at` | Date de debut de validite du canal. | 18 | 0 | 98.78% | `2025-12-15 14:00:00+01:00`, `2024-04-03 22:00:00+02:00` |
| `ended_at` | Date de fin de validite du canal. | 1471 | 0 | 0.0% |  |
| `last_updated_at` | Date de derniere mise a jour. | 214 | 0 | 85.45% | `2025-12-17 09:00:00+01:00`, `2026-04-16 17:00:00+02:00` |
| `time_step` | Pas temporel de mesure, en minutes. | 0 | 0 | 100.0% | `3600`, `900` |
| `provider_portal_url` | URL source du fournisseur. | 1471 | 0 | 0.0% |  |

## `comptage_mesures_jan_mar_2026`

- Lignes : **1360146**
- Colonnes : **5**
- Doublons exacts : **0**
- Note : Fenetre interrogee: start_datetime >= 2026-01-01 et < 2026-04-01.

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `channel_id` | Identifiant du canal de mesure. | 0 | 0 | 100.0% | `101017787`, `101017788` |
| `counter_id` | Identifiant du compteur physique. | 488 | 0 | 99.96% | `X2H17041932`, `ZLT24111466` |
| `start_datetime` | Debut de la fenetre de comptage. | 0 | 0 | 100.0% | `2026-01-01 00:00:00+01:00`, `2026-01-01 00:45:00+01:00` |
| `end_datetime` | Fin de la fenetre de comptage. | 0 | 0 | 100.0% | `2026-01-01 01:00:00+01:00`, `2026-01-01 00:30:00+01:00` |
| `count` | Nombre de passages comptes sur la fenetre. | 0 | 0 | 100.0% | `0`, `2` |

## `meteo_rr_t_vent_jan_mar_2026`

- Lignes : **1620**
- Colonnes : **60**
- Doublons exacts : **0**
- Note : Filtre applique: observations quotidiennes du departement 69 entre 2026-01-01 et 2026-03-31.

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `NUM_POSTE` | Identifiant de la station meteorologique. | 0 | 0 | 100.0% | `69008001`, `69028001` |
| `NOM_USUEL` | Nom usuel de la station. | 0 | 0 | 100.0% | `ANCY_SAPC`, `BRINDAS` |
| `LAT` | Latitude de la station. | 0 | 0 | 100.0% | `45.843333`, `45.713333` |
| `LON` | Longitude de la station. | 0 | 0 | 100.0% | `4.508167`, `4.693167` |
| `ALTI` | Altitude de la station. | 0 | 0 | 100.0% | `626`, `317` |
| `AAAAMMJJ` | Date d'observation au format AAAAMMJJ. | 0 | 0 | 100.0% | `20260101`, `20260102` |
| `RR` | Cumul quotidien de precipitations. | 0 | 0 | 100.0% | `0.0`, `0.8` |
| `QRR` |  | 0 | 0 | 100.0% | `1` |
| `TN` | Temperature minimale quotidienne. | 0 | 0 | 100.0% | `-5.7`, `-3.6` |
| `QTN` |  | 0 | 0 | 100.0% | `1` |
| `HTN` |  | 1 | 0 | 99.94% | `651`, `549` |
| `QHTN` |  | 0 | 0 | 100.0% | `9`, `1` |
| `TX` | Temperature maximale quotidienne. | 0 | 0 | 100.0% | `4.2`, `4.5` |
| `QTX` |  | 0 | 0 | 100.0% | `1` |
| `HTX` |  | 2 | 0 | 99.88% | `1339`, `1317` |
| `QHTX` |  | 2 | 0 | 99.88% | `9`, `1` |
| `TM` | Temperature moyenne quotidienne, si disponible. | 1 | 0 | 99.94% | `-1.5`, `0.2` |
| `QTM` |  | 0 | 0 | 100.0% | `1` |
| `TNTXM` |  | 0 | 0 | 100.0% | `-0.8`, `0.5` |
| `QTNTXM` |  | 0 | 0 | 100.0% | `1` |
| `TAMPLI` |  | 0 | 0 | 100.0% | `9.9`, `8.1` |
| `QTAMPLI` |  | 0 | 0 | 100.0% | `1` |
| `TNSOL` |  | 1170 | 0 | 27.78% | `-9.5`, `-8.3` |
| `QTNSOL` |  | 1170 | 0 | 27.78% | `9`, `1` |
| `TN50` |  | 1269 | 0 | 21.67% | `-10.2`, `-10.0` |
| `QTN50` |  | 1269 | 0 | 21.67% | `9`, `1` |
| `DG` |  | 38 | 0 | 97.65% | `896`, `566` |
| `QDG` |  | 36 | 0 | 97.78% | `9`, `1` |
| `FFM` | Vitesse moyenne quotidienne du vent, si disponible. | 1080 | 0 | 33.33% | `1.1`, `1.3` |
| `QFFM` |  | 1080 | 0 | 33.33% | `1` |
| `FF2M` |  | 1620 | 0 | 0.0% |  |
| `QFF2M` |  | 1620 | 0 | 0.0% |  |
| `FXY` | Rafale maximale quotidienne, si disponible. | 1081 | 0 | 33.27% | `2.6`, `2.8` |
| `QFXY` |  | 1081 | 0 | 33.27% | `1` |
| `DXY` |  | 1081 | 0 | 33.27% | `150`, `330` |
| `QDXY` |  | 1081 | 0 | 33.27% | `1`, `9` |
| `HXY` |  | 1081 | 0 | 33.27% | `1028`, `240` |
| `QHXY` |  | 1081 | 0 | 33.27% | `9`, `1` |
| `FXI` |  | 1080 | 0 | 33.33% | `4.2`, `5.1` |
| `QFXI` |  | 1080 | 0 | 33.33% | `1` |
| `DXI` |  | 1081 | 0 | 33.27% | `180`, `340` |
| `QDXI` |  | 1081 | 0 | 33.27% | `1`, `9` |
| `HXI` |  | 1081 | 0 | 33.27% | `1140`, `1802` |
| `QHXI` |  | 1081 | 0 | 33.27% | `9`, `1` |
| `FXI2` |  | 1620 | 0 | 0.0% |  |
| `QFXI2` |  | 1620 | 0 | 0.0% |  |
| `DXI2` |  | 1620 | 0 | 0.0% |  |
| `QDXI2` |  | 1620 | 0 | 0.0% |  |
| `HXI2` |  | 1620 | 0 | 0.0% |  |
| `QHXI2` |  | 1620 | 0 | 0.0% |  |
| `FXI3S` |  | 1081 | 0 | 33.27% | `3.7`, `4.7` |
| `QFXI3S` |  | 1081 | 0 | 33.27% | `1` |
| `DXI3S` |  | 1081 | 0 | 33.27% | `180`, `340` |
| `QDXI3S` |  | 1081 | 0 | 33.27% | `1` |
| `HXI3S` |  | 1081 | 0 | 33.27% | `1140`, `1802` |
| `QHXI3S` |  | 1081 | 0 | 33.27% | `9`, `1` |
| `DRR` |  | 1448 | 0 | 10.62% | `0`, `579` |
| `QDRR` |  | 1442 | 0 | 10.99% | `9`, `1` |
| `STATUS_FXI3S` |  | 1081 | 0 | 33.27% | `0` |
| `STATUS_DXI3S` |  | 1081 | 0 | 33.27% | `1`, `0` |

## `meteo_autres_jan_mar_2026`

- Lignes : **1620**
- Colonnes : **88**
- Doublons exacts : **0**
- Note : Filtre applique: observations quotidiennes du departement 69 entre 2026-01-01 et 2026-03-31.

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `NUM_POSTE` | Identifiant de la station meteorologique. | 0 | 0 | 100.0% | `69008001`, `69028001` |
| `NOM_USUEL` | Nom usuel de la station. | 0 | 0 | 100.0% | `ANCY_SAPC`, `BRINDAS` |
| `LAT` | Latitude de la station. | 0 | 0 | 100.0% | `45.843333`, `45.713333` |
| `LON` | Longitude de la station. | 0 | 0 | 100.0% | `4.508167`, `4.693167` |
| `ALTI` | Altitude de la station. | 0 | 0 | 100.0% | `626`, `317` |
| `AAAAMMJJ` | Date d'observation au format AAAAMMJJ. | 0 | 0 | 100.0% | `20260101`, `20260102` |
| `DHUMEC` |  | 1534 | 0 | 5.31% | `0`, `84` |
| `QDHUMEC` |  | 1534 | 0 | 5.31% | `9` |
| `PMERM` |  | 1440 | 0 | 11.11% | `1017.8`, `1012.1` |
| `QPMERM` |  | 1440 | 0 | 11.11% | `1` |
| `PMERMIN` |  | 1443 | 0 | 10.93% | `1014.1`, `1009.4` |
| `QPMERMIN` |  | 1443 | 0 | 10.93% | `1`, `9` |
| `INST` |  | 1440 | 0 | 11.11% | `471`, `472` |
| `QINST` |  | 1440 | 0 | 11.11% | `9`, `1` |
| `GLOT` |  | 1440 | 0 | 11.11% | `710`, `739` |
| `QGLOT` |  | 1440 | 0 | 11.11% | `9`, `1` |
| `DIFT` |  | 1620 | 0 | 0.0% |  |
| `QDIFT` |  | 1620 | 0 | 0.0% |  |
| `DIRT` |  | 1620 | 0 | 0.0% |  |
| `QDIRT` |  | 1620 | 0 | 0.0% |  |
| `INFRART` |  | 1620 | 0 | 0.0% |  |
| `QINFRART` |  | 1620 | 0 | 0.0% |  |
| `UV` |  | 1620 | 0 | 0.0% |  |
| `QUV` |  | 1620 | 0 | 0.0% |  |
| `UV_INDICEX` |  | 1620 | 0 | 0.0% |  |
| `QUV_INDICEX` |  | 1620 | 0 | 0.0% |  |
| `SIGMA` |  | 1440 | 0 | 11.11% | `92`, `84` |
| `QSIGMA` |  | 1440 | 0 | 11.11% | `9`, `1` |
| `UN` |  | 990 | 0 | 38.89% | `58`, `51` |
| `QUN` |  | 990 | 0 | 38.89% | `1` |
| `HUN` |  | 992 | 0 | 38.77% | `1407`, `1354` |
| `QHUN` |  | 992 | 0 | 38.77% | `9`, `1` |
| `UX` |  | 990 | 0 | 38.89% | `95`, `92` |
| `QUX` |  | 990 | 0 | 38.89% | `1` |
| `HUX` |  | 992 | 0 | 38.77% | `2325`, `15` |
| `QHUX` |  | 992 | 0 | 38.77% | `9`, `1` |
| `UM` |  | 991 | 0 | 38.83% | `82`, `77` |
| `QUM` |  | 990 | 0 | 38.89% | `1` |
| `DHUMI40` |  | 997 | 0 | 38.46% | `0`, `34` |
| `QDHUMI40` |  | 997 | 0 | 38.46% | `9`, `1` |
| `DHUMI80` |  | 998 | 0 | 38.4% | `1003`, `783` |
| `QDHUMI80` |  | 998 | 0 | 38.4% | `9`, `1` |
| `TSVM` |  | 990 | 0 | 38.89% | `3.9`, `4.4` |
| `QTSVM` |  | 990 | 0 | 38.89% | `1` |
| `ETPMON` |  | 1440 | 0 | 11.11% | `0.2`, `0.4` |
| `QETPMON` |  | 990 | 0 | 38.89% | `1`, `9` |
| `ETPGRILLE` |  | 0 | 0 | 100.0% | `0.8`, `0.6` |
| `QETPGRILLE` |  | 0 | 0 | 100.0% | `9` |
| `ECOULEMENTM` |  | 1620 | 0 | 0.0% |  |
| `QECOULEMENTM` |  | 1620 | 0 | 0.0% |  |
| `HNEIGEF` |  | 1530 | 0 | 5.56% | `0`, `1` |
| `QHNEIGEF` |  | 1530 | 0 | 5.56% | `9`, `1` |
| `NEIGETOTX` |  | 1440 | 0 | 11.11% | `0`, `1` |
| `QNEIGETOTX` |  | 1440 | 0 | 11.11% | `9` |
| `NEIGETOT06` |  | 1440 | 0 | 11.11% | `0`, `1` |
| `QNEIGETOT06` |  | 1440 | 0 | 11.11% | `9`, `1` |
| `NEIG` |  | 1443 | 0 | 10.93% | `0`, `1` |
| `QNEIG` |  | 1443 | 0 | 10.93% | `9` |
| `BROU` |  | 1441 | 0 | 11.05% | `0`, `1` |
| `QBROU` |  | 1441 | 0 | 11.05% | `9` |
| `ORAG` |  | 1444 | 0 | 10.86% | `0` |
| `QORAG` |  | 1444 | 0 | 10.86% | `9` |
| `GRESIL` |  | 1530 | 0 | 5.56% | `0` |
| `QGRESIL` |  | 1530 | 0 | 5.56% | `9` |
| `GRELE` |  | 1530 | 0 | 5.56% | `0` |
| `QGRELE` |  | 1530 | 0 | 5.56% | `9` |
| `ROSEE` |  | 1530 | 0 | 5.56% | `0`, `1` |
| `QROSEE` |  | 1530 | 0 | 5.56% | `9` |
| `VERGLAS` |  | 1491 | 0 | 7.96% | `1`, `0` |
| `QVERGLAS` |  | 1491 | 0 | 7.96% | `9`, `1` |
| `SOLNEIGE` |  | 1530 | 0 | 5.56% | `0`, `1` |
| `QSOLNEIGE` |  | 1530 | 0 | 5.56% | `9` |
| `GELEE` |  | 1480 | 0 | 8.64% | `1`, `0` |
| `QGELEE` |  | 1480 | 0 | 8.64% | `9` |
| `FUMEE` |  | 1442 | 0 | 10.99% | `0` |
| `QFUMEE` |  | 1442 | 0 | 10.99% | `9` |
| `BRUME` |  | 1442 | 0 | 10.99% | `1`, `0` |
| `QBRUME` |  | 1442 | 0 | 10.99% | `9` |
| `ECLAIR` |  | 1530 | 0 | 5.56% | `0` |
| `QECLAIR` |  | 1530 | 0 | 5.56% | `9` |
| `NB300` |  | 1602 | 0 | 1.11% | `7`, `8` |
| `QNB300` |  | 1602 | 0 | 1.11% | `9` |
| `BA300` |  | 1602 | 0 | 1.11% | `130`, `210` |
| `QBA300` |  | 1602 | 0 | 1.11% | `9` |
| `TMERMIN` |  | 1620 | 0 | 0.0% |  |
| `QTMERMIN` |  | 1620 | 0 | 0.0% |  |
| `TMERMAX` |  | 1620 | 0 | 0.0% |  |
| `QTMERMAX` |  | 1620 | 0 | 0.0% |  |

## `tarifs_taxi_rhone_2026_reference`

- Lignes : **4**
- Colonnes : **7**
- Doublons exacts : **0**
- Note : Reference saisie depuis la page tarifs maximum 2026 de la Metropole de Lyon.

| Champ | Description | Vides | NA litteraux | Completude | Exemples |
|---|---|---:|---:|---:|---|
| `tarif` | Code tarif officiel A, B, C ou D. | 0 | 0 | 100.0% | `A`, `B` |
| `periode` | Periode d'application du tarif. | 0 | 0 | 100.0% | `Jour 7h-19h`, `Nuit 19h-7h / dimanches / jours feries / routes enneigees` |
| `condition_retour` | Condition aller-retour avec client ou retour a vide. | 0 | 0 | 100.0% | `Aller et retour avec un client`, `Aller avec un client et retour a vide` |
| `prix_km_eur` | Prix maximum par kilometre. | 0 | 0 | 100.0% | `1.00`, `1.50` |
| `prise_en_charge_eur` | Montant de prise en charge. | 0 | 0 | 100.0% | `3.10` |
| `course_minimum_eur` | Montant minimal d'une course. | 0 | 0 | 100.0% | `8.00` |
| `attente_marche_lente_eur_h` | Tarif horaire d'attente ou de marche lente. | 0 | 0 | 100.0% | `41.30` |

## Metadonnees complementaires

```json
{
  "rpc": {
    "raw_counts_by_month": {
      "2026-01": 937369,
      "2026-02": 915542,
      "2026-03": 1093455
    },
    "filtered_counts_by_month": {
      "2026-01": 23854,
      "2026-02": 22717,
      "2026-03": 28260
    },
    "start_in_lyon_rows": 50565,
    "end_in_lyon_rows": 51769,
    "internal_lyon_rows": 27503,
    "output_csv": "C:\\Users\\Utilisateur\\Documents\\New project\\data\\processed\\rpc_trajets_covoiturage_metropole_lyon_2026_01_03.csv"
  },
  "chantiers": {
    "output_csv": "C:\\Users\\Utilisateur\\Documents\\New project\\data\\processed\\chantiers_perturbants_jan_mar_2026.csv"
  },
  "comptage_mesures": {
    "distinct_channels": 723,
    "distinct_counters": 154,
    "rows_by_month": {
      "2026-01": 407814,
      "2026-02": 426299,
      "2026-03": 526033
    }
  },
  "meteo_rr_t_vent": {
    "stations": {
      "ANCY_SAPC": 90,
      "BRINDAS": 90,
      "LYON-BRON": 90,
      "COURS LA VILLE_SAPC": 90,
      "LIERGUES_SAPC": 90,
      "LYON TETE D'OR": 90,
      "MONSOLS": 90,
      "MORNANT": 90,
      "LES SAUVAGES": 90,
      "ST-DIDIER-BEAUJ": 90,
      "ST-GENIS-L'ARGENTIERE": 90,
      "ST-GENIS-LAVAL": 90,
      "ST-GEORGES-REN": 90,
      "ST-SYMPHORIEN-C": 90,
      "SAINT-VERAND": 90,
      "VAUXRENARD": 90,
      "VILLEFRANCHE": 90,
      "LYON-ST EXUPERY": 90
    },
    "output_csv": "C:\\Users\\Utilisateur\\Documents\\New project\\data\\processed\\meteo_rr_t_vent_jan_mar_2026.csv"
  },
  "meteo_autres": {
    "stations": {
      "ANCY_SAPC": 90,
      "BRINDAS": 90,
      "LYON-BRON": 90,
      "COURS LA VILLE_SAPC": 90,
      "LIERGUES_SAPC": 90,
      "LYON TETE D'OR": 90,
      "MONSOLS": 90,
      "MORNANT": 90,
      "LES SAUVAGES": 90,
      "ST-DIDIER-BEAUJ": 90,
      "ST-GENIS-L'ARGENTIERE": 90,
      "ST-GENIS-LAVAL": 90,
      "ST-GEORGES-REN": 90,
      "ST-SYMPHORIEN-C": 90,
      "SAINT-VERAND": 90,
      "VAUXRENARD": 90,
      "VILLEFRANCHE": 90,
      "LYON-ST EXUPERY": 90
    },
    "output_csv": "C:\\Users\\Utilisateur\\Documents\\New project\\data\\processed\\meteo_autres_jan_mar_2026.csv"
  },
  "runtime_seconds": 129.9,
  "generated_at": "2026-04-25T18:32:58"
}
```
