# Note de cadrage - Analyse Mobilite Rhone

Nom publie : **Analyse Mobilite Rhone**

## Cadrage

Le projet etudie le potentiel de mobilite dans le Rhone a partir de donnees ouvertes.

La question de fond est operationnelle : comprendre ou et quand les deplacements se concentrent pour aider a prioriser des zones, des horaires et des niveaux de service.

En l'absence de donnees commerciales ouvertes suffisamment detaillees, l'analyse repose sur des jeux publics capables de donner une lecture indirecte mais exploitable du territoire.

## Sujet retenu

**Analyse du potentiel de mobilite dans le Rhone a partir de donnees publiques ouvertes, janvier-mars 2026.**

## Problematique

**Comment transformer des donnees ouvertes de mobilite en outil d'aide a la decision pour identifier les zones, periodes et conditions favorables au deploiement d'une offre de transport dans le Rhone ?**

## Hypothese de travail

Les trajets de covoiturage, les comptages de mobilite, les stations taxi, les chantiers, la meteo et les tarifs publics peuvent donner une lecture suffisamment solide de la demande potentielle, meme sans disposer de donnees commerciales detaillees.

Le covoiturage est utilise comme proxy principal parce qu'il contient des trajets individuels avec heure, commune, distance, duree et coordonnees.

## Periode retenue

**Janvier a mars 2026.**

Le trimestre permet de comparer :

- les mois entre eux ;
- les jours de semaine et les week-ends ;
- les plages horaires ;
- les zones de depart et d'arrivee ;
- les effets possibles de la meteo et des travaux.

## Livrables

- scripts Python de profiling et transformation ;
- dictionnaire de donnees ;
- tables CSV Power BI ;
- modele en constellation ;
- dashboard Power BI en 3 pages ;
- publication portfolio GitHub Pages.

## Limites

- Les donnees ne sont pas des courses professionnelles reelles.
- Les coordonnees RPC sont arrondies.
- Le revenu est une estimation theorique basee sur des tarifs publics 2026.
- Le dashboard sert a raisonner une strategie, pas a mesurer un chiffre d'affaires reel.
