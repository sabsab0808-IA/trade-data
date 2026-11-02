---
title: Étude n°9 — Résultats
subtitle: Rebalancement de fin de mois SPY / IEF — exécution stricte du doc 17
num: 17b
date: 2026-11-02
---

## Verdict

**Non conforme.** L'effet existe bien sur la période du papier (Sharpe 0,64, t = 2,9 sur 2002–2023), mais **il est négatif depuis la publication** : −29 points de base par trade sur 04/2023–10/2026, et 2025–2026 sont les deux pires années depuis 2002. Même schéma que l'overnight, le pré-FOMC et la noise area : l'edge disparaît une fois connu.

## Résultats (par trade de 5 séances, coûts de 8 pb inclus)

| Période | Trades | Moyenne | Sharpe | t | Gagnants | Pire trade |
|---|---|---|---|---|---|---|
| 08/2002 – 03/2023 (papier) | 246 | **+0,63 %** | **0,64** | 2,90 | 57 % | −9,9 % |
| 04/2023 – 10/2026 (après) | 43 | **−0,29 %** | **−0,48** | −0,91 | 51 % | −5,3 % |
| Jambe actions seule, papier | 246 | +0,45 % | 0,64 | 2,92 | 57 % | −5,5 % |
| Jambe actions seule, après | 43 | −0,06 % | −0,12 | −0,24 | 40 % | −3,0 % |

Par année (somme des trades, en %) : 2008 +29,3 · 2011 +29,5 · 2020 +16,8 · 2024 +8,8 · **2025 −5,4 · 2026 −14,3**. L'essentiel du gain historique vient des années de crise (2008, 2011, 2020).

## Ce qu'on en fait

Comme prévu au pré-enregistrement, la règle entre quand même dans le suivi papier (onglet « Compte perso »), **marquée « non conforme »**. Les 2–3 semaines de papier ne donneront qu'un seul trade (fin novembre) : c'est une stratégie lente.

## Fichiers

Code `trade/code/study9.py` ; résultats `trade/study9/summary_study9.csv`, `par_annee_study9.csv`, `trades_study9.csv`.
