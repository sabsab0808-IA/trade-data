---
title: Étude n°10 — Résultats
subtitle: Suivi de tendance diversifié sur 29 ETF — exécution stricte du doc 18
num: 18b
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

## Fichiers

Code `trade/code/study10.py` ; résultats `trade/study10/summary_study10.csv`, `par_annee_study10.csv`, `par_classe_study10.csv`, `criteres_study10.csv`.
