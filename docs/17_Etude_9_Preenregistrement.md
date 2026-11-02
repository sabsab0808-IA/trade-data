---
title: Étude n°9 — Pré-enregistrement
subtitle: Rebalancement de fin de mois, actions contre obligations — écrit AVANT tout calcul
num: 17
date: 2026-11-02
---

## Pourquoi cette étude

La revue (doc 14) classe ce dossier comme le plus solide : les fonds 60/40 doivent revendre ce qui a monté et racheter ce qui a baissé en fin de mois, et ces flux sont prévisibles. Un papier EDHEC (SSRN 5122748) annonce un Sharpe de 1,11 (≈ 1 après coûts) sur 1997–2023 pour un long/short S&P contre T-Note 10 ans. Saber veut l'inclure dans le suivi papier : on fige d'abord une règle simple et on la teste.

Ce document est publié dans le projet avant de lancer le code. Il n'est plus modifié ensuite.

## Données

- Yahoo Finance, clôtures ajustées (dividendes inclus) de **SPY** (S&P 500) et **IEF** (Trésor US 7–10 ans), 08/2002 → 10/2026 (dépôt `trade-data`, `data_ext/yahoo/indices_etf/`).
- Les ETF servent d'historique propre (pas de roll). En réel, on traderait MES et ZN.
- **Période du papier : jusqu'en 03/2023. Période après publication : 04/2023 → 10/2026** (≈ 43 mois, jamais vus par les auteurs).

## Règle (figée)

- Jour N = dernière séance du mois. Signal à la **clôture de N−5** (il reste 5 séances).
- Rendements depuis la dernière clôture du mois précédent : r_a (SPY) et r_o (IEF). Poids actions d'un 60/40 non rebalancé : w = 0,6(1+r_a) / [0,6(1+r_a) + 0,4(1+r_o)].
- Si **w > 0,6** (les actions ont surperformé) → les fonds vont vendre des actions : **vente SPY / achat IEF**. Si **w < 0,6** → **achat SPY / vente IEF**.
- Position prise à la clôture de N−5, fermée à la clôture de N (5 séances).
- Pondération à risque égal : jambe obligataire = k × jambe actions, avec k = écart-type des rendements journaliers de SPY / celui d'IEF sur les 60 séances précédentes.
- Coûts : **8 points de base par trade** (aller-retour sur les deux jambes, sur le nominal de la jambe actions).

## Critère

La règle est jugée « conforme au papier » si :

1. **08/2002 – 03/2023** : Sharpe annualisé net ≥ 0,5.
2. **04/2023 – 10/2026** : rendement moyen net par trade > 0.

Publié aussi, à titre descriptif : la jambe actions seule (SPY), le taux de réussite, le pire trade, et les résultats par année.

## Ensuite

Quel que soit le résultat, la règle entre dans le suivi papier demandé par Saber (onglet « Compte perso »), avec ses chiffres affichés. Si le critère 1 ou 2 échoue, elle y est marquée « non conforme ».
