---
title: Étude n°15 — Résultats
subtitle: Suivi de tendance diversifié sur 29 ETF — exécution stricte du doc 20 (ex-étude 10 / doc 18)
num: 20b
date: 2026-11-02
---

## Verdict

**Non retenue.** Après publication (2012–2026), le suivi de tendance sur 29 ETF fait un **Sharpe de −0,02** net (−1,5 % par an). Même sans aucun coût, il ne fait que 0,31. Sur la même période, un simple 60/40 fait **0,99** et le S&P 500 seul **0,92**.

Son seul vrai atout : il protège pendant les krachs (+13,7 % fin 2008, −1,1 % au Covid, +3,8 % en 2022 quand le 60/40 perd 16 %). Mais cette assurance coûte trop cher le reste du temps.

## Critères

| Condition | Résultat | OK ? |
|---|---|---|
| 1 · Sharpe net 2012–2026 ≥ 0,4 | −0,02 | ✗ |
| 2 · Mieux que le long-only à risque égal (2012–2026) | −0,02 contre 0,45 | ✗ |
| 3 · Rendement net 2020–2026 > 0 | −2,7 % par an | ✗ |

## Résultats nets

| Période | Stratégie | Rendement / an | Volatilité | Sharpe | Pire drawdown | Corrélation SPY |
|---|---|---|---|---|---|---|
| 2008–2011 | Suivi de tendance | −2,3 % | 23 % | 0,01 | −39 % | −0,27 |
| 2012–2026 | Suivi de tendance | **−1,5 %** | 16 % | **−0,02** | −54 % | 0,13 |
| 2012–2026 | Long-only risque égal | +8,0 % | 23 % | 0,45 | −55 % | 0,71 |
| 2012–2026 | 60/40 | +9,7 % | 10 % | **0,99** | −21 % | 0,97 |
| 2012–2026 | SPY | +14,9 % | 16 % | 0,92 | −34 % | 1,00 |
| 2020–2026 | Suivi de tendance | −2,7 % | 17 % | −0,08 | −40 % | 0,13 |

Sans coût d'emprunt : Sharpe 0,20 (2012–2026). Sans aucun coût : 0,31. Le verdict ne dépend pas des hypothèses de coûts.

Par classe d'actifs (brut, 2012–2026) : actions +3,4 %/an, matières premières +1,6 %, obligations +0,4 %, devises −0,6 %. Les devises et les taux, cœur du suivi de tendance des CTA, ne rapportent rien ici.

Par année : 2008 +16 % · 2013 +18 % · 2017 +27 % · mais 2016 −24 % · 2018 −21 % · 2023 −15 %.

## Ce qu'on apprend

- Le résultat colle aux chiffres publics : l'indice SG CTA Trend a fait un **Sharpe de 0,14 sur 2010–2025** (arXiv 2507.15876). Le suivi de tendance « vend de l'assurance krach », il ne bat pas un portefeuille classique.
- **Pour un particulier qui veut faire fructifier son argent sur plusieurs années, le 60/40 ou un ETF monde reste imbattable** sur cette période, sans aucun travail.

## Pourquoi l'étude 14 (40 futures) trouve l'inverse

L'étude 14 (doc 18b, autre série) teste la même idée sur 40 futures et la trouve **conforme** (Sharpe 0,47 après 2013). J'ai relancé son code sur les mêmes données : je retrouve exactement ses chiffres (0,55 / 0,47 / 0,70). **Les deux résultats sont justes : ils ne mesurent pas la même chose.** Le pont, étape par étape, sur 2013–2026 :

| Version | Sharpe 2013–2026 | Sharpe 2021–2026 |
|---|---|---|
| ETF, règle pré-enregistrée (10 pb de coûts + 2 %/an d'emprunt sur les ventes) | −0,06 | −0,03 |
| ETF, mêmes coûts que les futures (3 pb, pas de coût d'emprunt) | 0,23 | 0,22 |
| Futures, sans grains, softs ni viandes (univers comparable aux ETF) | 0,38 | 0,28 |
| **Futures, 40 marchés (étude 14)** | **0,47** | **0,70** |

Ce qui explique l'écart :

1. **Les coûts de vente à découvert (~0,3 de Sharpe).** Vendre un ETF coûte un emprunt ; vendre un future ne coûte rien de plus que l'acheter. Le suivi de tendance est vendeur la moitié du temps.
2. **Les marchés agricoles et les viandes (~0,1 de Sharpe).** Dans l'étude 14, les meilleurs secteurs depuis 2013 sont les indices (Sharpe 0,60), les viandes (0,56), les métaux (0,32) et les softs (0,22). Les devises perdent (−0,06), comme dans mon étude. Ces marchés agricoles n'ont presque pas d'équivalent en ETF.

**Conclusion commune** : le suivi de tendance a un vrai edge modeste **en futures, sur un univers très large**. Il disparaît dans une version ETF accessible à un particulier. Dans les deux cas, ce n'est pas faisable pour Saber : hors Topstep (positions d'un mois), et il faudrait plusieurs centaines de milliers de dollars pour le faire en futures.

## Fichiers

Code `trade/code/study15_tendance_etf.py` ; résultats `trade/study15/summary_study15.csv`, `par_annee_study15.csv`, `par_classe_study15.csv`, `criteres_study15.csv`.
