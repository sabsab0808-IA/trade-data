---
title: Étude n°8 — Résultats
subtitle: « Le lundi acheteur » intraday — exécution stricte du doc 15
num: 15b
date: 2026-11-02
---

## Verdict

**Non retenue.** Sur 2010–2020, période que l'auteur de la règle n'avait jamais regardée, le lundi acheteur ne marche pas : NQ +0,02 R par trade (t = 0,76), ES −0,03 R. On retrouve bien le résultat publié sur 2021–2026 (NQ t = 2,96, ~2 670 $ par an pour 1 MNQ contre ~2 962 $ annoncés), mais c'est un effet de la période récente, pas une règle stable.

## Critères

| Condition | Résultat | OK ? |
|---|---|---|
| 1 · NQ 2010–2020 : espérance > 0 et t ≥ 2 | +0,023 R, t = 0,76 | ✗ |
| 2 · ES 2010–2020 : espérance > 0 | −0,030 R | ✗ |
| 3 · Lundi > autres jours (NQ 2010–2020) | +0,023 contre −0,014 R (t de l'écart 1,10) | ✓ |
| 4 · Réplication NQ 2021–2026 > 0 | +0,110 R, t = 2,96 | ✓ |

## Lundi, achat à l'ouverture, vente à la clôture, coûts compris

| Marché | 2010–2020 R / trade (t) | 2021–2026 R / trade (t) | $ / an / micro 2021–26 |
|---|---|---|---|
| NQ | +0,023 (0,76) | +0,110 (2,96) | +2 670 |
| ES | −0,030 (−1,00) | +0,085 (2,38) | +1 127 |
| CL | −0,004 (−0,16) | +0,028 (0,70) | +394 |
| GC | −0,022 (−0,87) | −0,040 (−1,13) | −765 |

Années NQ (R cumulés le lundi) : jusqu'en 2018, bonnes et mauvaises années alternent (2012 +5,4 · 2013 −5,2 · 2014 −6,1 · 2016 +4,1 · 2018 −5,4). Depuis 2019, toutes les années sont positives (2020 +13,5 · 2023 +11,6 · 2025 +7,8 · 2026 +7,2). L'effet est propre à la période récente.

## Ce qu'on apprend

- Une règle trouvée sur 5 ans, même pré-enregistrée et avec un t de 3,4, peut être un effet de période. Seul un test sur d'autres années le révèle.
- Même sur 2021–2026, ~2 700 $ par an et par MNQ, c'est trop lent pour un Topstep 50K (objectif 3 000 $ en 1 à 2 mois) sans prendre 5 à 10 micros.

## Fichiers

Code `trade/code/study8.py` ; résultats `trade/study8/summary_study8.csv`, `criteres_study8.csv`, `par_annee_lundi_study8.csv`.
