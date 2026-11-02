---
title: Étude n°10 — Pré-enregistrement
subtitle: Suivi de tendance diversifié sur 29 ETF multi-actifs — écrit AVANT tout calcul
num: 18
date: 2026-11-02
---

## Pourquoi cette étude

L'étude 7 a testé le momentum 12 mois sur seulement 4 marchés : il manquait la diversification (taux, devises, matières premières) qui fait marcher le suivi de tendance dans la littérature (Moskowitz, Ooi & Pedersen 2012). La revue (doc 14) le classait candidat n°3. On le teste sur un univers large, avec des ETF : historique propre (pas de roll) et produits accessibles à un particulier (en Europe, via leurs équivalents UCITS).

Ce document est publié dans le projet avant de lancer le code. Il n'est plus modifié ensuite.

## Données

Yahoo Finance, clôtures ajustées (dividendes inclus), dépôt `trade-data`, `data_ext/yahoo/etf_univers/`. **29 ETF** :

- Actions : SPY, QQQ, IWM, EFA, EEM, EWJ, VGK, EWZ, FXI, VNQ
- Obligations : TLT, IEF, LQD, HYG, TIP, EMB
- Matières premières : GLD, SLV, USO, UNG, DBA, DBB
- Devises : UUP, FXE, FXY, FXB, FXA, FXC, FXF

SHY sert de taux sans risque. Un ETF entre dans l'univers dès qu'il a 12 mois d'historique.

## Règle (figée)

- Dernier jour de chaque mois, à la clôture : signal = signe du rendement sur 12 mois de l'ETF **moins** celui de SHY.
- Taille : chaque position vise 40 % de volatilité annualisée (écart-type des 60 dernières séances), puis on divise par le nombre d'ETF disponibles (méthode du papier).
- Achats **et** ventes à découvert. Position tenue un mois.
- Coûts : **10 points de base** par unité de rotation (|variation de poids|), plus 2 % par an sur la partie vendue à découvert (coût d'emprunt approximatif).

## Références

1. **60/40** : 60 % SPY, 40 % IEF, rebalancé chaque mois.
2. **Long-only à risque égal** : mêmes poids que la stratégie, mais toujours à l'achat. Il dit si le **signal** ajoute quelque chose, au-delà de la simple diversification.

## Périodes

- **2008–2011** : avant la publication du papier.
- **2012–2026** : après publication (vrai test).
- Sous-période **2020–2026** : la plus récente.

## Critère

La stratégie est retenue si **les 3 conditions** sont remplies :

1. Sharpe net **2012–2026 ≥ 0,4**.
2. Sharpe net **2012–2026 supérieur** à celui du long-only à risque égal.
3. Rendement net **2020–2026 > 0**.

Publié aussi : corrélation avec SPY, pire drawdown, résultats par année, par classe d'actifs, et comportement pendant les krachs (2008, 2020, 2022).

## Ensuite

Retenue → elle est ajoutée au suivi papier du compte perso (signal mensuel, 1 fois par mois). Sinon → la piste « suivi de tendance pour particulier » est fermée.
