# Publication GitHub Pages

Ce projet est destine a etre presente dans un portfolio GitHub Pages.

Je ne prevois pas de publier le rapport via Fabric. Le rapport Power BI est construit dans Power BI Desktop, puis les pages finales seront exportees en visuels statiques pour le site.

## Strategie retenue

Le site doit montrer le projet complet, pas seulement le dashboard :

- contexte metier ;
- sources de donnees ;
- controles qualite ;
- transformation Python ;
- schema du modele Power BI ;
- captures des 3 pages du rapport ;
- limites et recommandations.

## Pourquoi ne pas publier le PBIX

Le fichier `.pbix` n'est pas versionne parce qu'il est lourd, binaire et moins lisible dans Git. Le depot garde plutot les elements auditables :

- scripts Python ;
- CSV prepares ;
- documentation ;
- dictionnaire de donnees ;
- captures/export du rapport.

Le `.gitignore` exclut donc :

```text
*.pbix
*.pbit
*.pbip/
```

## Difference avec un iframe Power BI

Un site peut afficher un rapport Power BI interactif avec un iframe `Publish to web`, mais cela passe par Power BI Service. Cette option rend le rapport public et peut exposer les donnees sous-jacentes.

Pour ce projet, l'option la plus propre est :

1. finaliser les 3 pages dans Power BI Desktop ;
2. exporter chaque page en image ;
3. integrer ces images dans GitHub Pages ;
4. expliquer le modele et les decisions dans le site.

## Structure cible

```text
site/
  index.html
  styles.css
  assets/
    page-1-vue-ensemble.png
    page-2-demande-temporelle.png
    page-3-analyse-geographique.png
```

## Workflow cible

La publication GitHub Pages pourra etre automatisee avec GitHub Actions :

1. checkout du depot ;
2. upload du dossier `site/` ;
3. deploiement sur GitHub Pages.

Le principe est proche du projet precedent `train-supprimes-fabric`, mais adapte ici a un projet Power BI Desktop sans Fabric.
