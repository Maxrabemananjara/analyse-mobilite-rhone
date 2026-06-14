# Pages Power BI

Le rapport Power BI est construit comme un livrable portfolio court : trois pages, chacune rattachee directement a la problematique.

Je n'ai pas cherche a multiplier les onglets. L'objectif est que le lecteur comprenne rapidement le modele, les resultats et les decisions possibles autour du deploiement territorial.

## Page 1 - Vue d'ensemble

**Role :** donner une lecture immediate du niveau de demande.

Visuels construits :

- cartes KPI : nombre de trajets, distance moyenne, duree moyenne, revenu moyen, revenu total ;
- evolution mensuelle des trajets ;
- top communes ;
- repartition par tranche horaire.

Ce que cette page apporte :

- volume global sur la periode ;
- communes les plus presentes ;
- premiere lecture des heures fortes ;
- indicateurs simples pour entrer dans le sujet.

## Page 2 - Demande temporelle

**Role :** comprendre quand la demande se concentre.

Visuels construits :

- heatmap jour de semaine x tranche horaire ;
- volume par jour de semaine ;
- repartition par tranche horaire ;
- part semaine vs week-end ;
- evolution quotidienne des trajets.

Ce que cette page apporte :

- identification des pics recurrents ;
- comparaison jours ouvres / week-end ;
- lecture des plages horaires utiles pour pre-positionner une flotte ;
- analyse par semaine du mois quand le filtre est utile.

## Page 3 - Analyse geographique

**Role :** comprendre ou la demande se concentre.

Visuels construits ou prevus :

- carte des points de depart ;
- classement des communes ;
- lecture par region, departement ou arrondissement ;
- secteurs geographiques issus du geocodage ;
- comparaison avec les points d'offre stationnaire.

Ce que cette page apporte :

- zones fortes de depart ;
- secteurs ou la demande se regroupe ;
- territoires bien ou mal couverts ;
- base de recommandations geographiques.

## Mesures Power BI

Le modele limite volontairement le DAX. Les transformations structurelles sont faites en Python et dans les tables CSV.

Mesures utiles :

```DAX
Nb trajets = DISTINCTCOUNT(fact_trajets[journey_id])
```

```DAX
Distance moyenne km = AVERAGE(fact_trajets[distance_km])
```

```DAX
Duree moyenne min = AVERAGE(fact_trajets[duree_min])
```

```DAX
Revenu estime moyen = AVERAGE(fact_trajets[revenu_estime_eur])
```

```DAX
Revenu estime total = SUM(fact_trajets[revenu_estime_eur])
```

Les libelles, ordres de tri, semaines du mois, tranches horaires et secteurs ont ete prepares dans les dimensions pour eviter de reconstruire la logique dans Power BI.

## Choix de publication

Le fichier `.pbix` reste hors GitHub. Pour le portfolio, les pages seront exportees sous forme d'images ou integrees dans un site GitHub Pages.
