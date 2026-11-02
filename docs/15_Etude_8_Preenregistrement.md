---
title: Étude n°8 — Pré-enregistrement
subtitle: « Le lundi acheteur » en intraday — test sur 2010–2020, période jamais regardée par l'auteur — écrit AVANT tout calcul
num: 15
date: 2026-11-02
---

## Pourquoi cette étude

La revue du doc 14 a trouvé une réplication pré-enregistrée de 50 règles intraday publiées (dépôt GitHub `NostroBenJ/intraday-strategy-replication`, 2026). Seules 4 règles passent. La plus solide statistiquement est la plus bête : **acheter le NQ à l'ouverture le lundi et revendre à la clôture**. Résultat annoncé sur NQ 2021–2026 : t = +3,36 (p corrigé 0,015), positif chaque année depuis 2019, ~46 trades par an, 60 % de gagnants, ~+2 962 $ par an pour 1 MNQ.

C'est compatible Topstep (à plat le soir). L'auteur n'a testé que 2021–2026 sur NQ. **Nos données NQ et ES 2010–2020 sont un vrai test indépendant.**

Ce document est publié dans le projet avant de lancer le code. Il n'est plus modifié ensuite.

## Règle (figée)

- Chaque lundi où la séance est complète (≥ 80 % des minutes) : achat au marché à la 1re minute de la séance (ouverture + 1 tick), revente à la clôture de l'avant-dernière minute (− 1 tick). Pas de stop, pas de filtre.
- Séances : NQ/ES 09:30–16:00, CL 09:00–14:30, GC 08:45–13:30 (heure de New York), comme les études 4 à 7.
- Coûts : 1 $ aller-retour par micro + 1 tick à l'entrée + 1 tick à la sortie.
- Unité : 1 R = moyenne des 14 dernières amplitudes de séance (plus haut − plus bas). Résultats aussi en $ par micro.
- Comparaison : la même règle appliquée aux mardis, mercredis, jeudis et vendredis.

## Critère de succès

La règle est retenue seulement si **les 4 conditions** sont remplies :

1. **NQ 2010–2020** : espérance nette > 0 avec **t ≥ 2,0**.
2. **ES 2010–2020** : espérance nette > 0.
3. **Spécifique au lundi** : sur NQ 2010–2020, l'espérance du lundi est supérieure à celle des autres jours réunis.
4. **Réplication NQ 2021–2026** : espérance nette > 0 (on doit retrouver le résultat publié avec nos données et nos coûts).

CL et GC sont publiés à titre descriptif (aucune raison économique annoncée pour eux).

## Ce qui se passe ensuite

- Elle passe → forward test automatique sur MNQ, et calcul du nombre de micros nécessaire pour viser un Topstep 50K sans dépasser la perte maximale.
- Elle échoue sur 2010–2020 → c'est probablement un artefact de la période 2019–2026, on l'écarte.
