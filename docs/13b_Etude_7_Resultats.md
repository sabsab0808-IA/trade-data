---
title: Étude n°7 — Résultats
subtitle: Swing RSI 2, dérive overnight, momentum 12 mois — exécution stricte du doc 13
num: 13b
date: 2026-11-02
---

## Verdict

**Aucune des 3 stratégies n'est retenue.** Aucune ne fait mieux que le simple buy & hold des 4 marchés en IS, et aucune n'atteint un Sharpe IS de 0,5.

Les coûts ne sont plus le problème (0,01 à 0,03 R par trade au lieu de ~0,09 R en intraday). Le problème, c'est qu'il n'y a pas d'edge au-delà de la hausse naturelle des indices.

## Critères (4 marchés combinés)

| Stratégie | Sharpe IS | IC bas IS | Sharpe OOS | Marchés + en IS | Mieux que B&H ? | Retenue |
|---|---|---|---|---|---|---|
| H1 · Swing RSI 2 | 0,20 ✗ | −0,42 ✗ | 0,48 ✓ | 3/4 ✓ | ✗ | **Non** |
| H2 · Overnight | −0,44 ✗ | −1,90 ✗ | 1,08 ✓ | 1/4 ✗ | ✗ (IS) | **Non** |
| H3 · Momentum 12 mois | 0,49 ✗ | −0,12 ✗ | 0,77 ✓ | 4/4 ✓ | ✗ | **Non** |
| *Buy & hold (référence)* | *0,45* | *−0,34* | *1,08* | *3/4* | — | — |

IS = 2010–2020, OOS = 2021–2026. Coûts : 1 $ par micro + 1 tick par ordre + coût de roll.

## Détail

| Stratégie | Trades | R / trade | Gagnants | Durée moy. | R / an (tout) | Pire drawdown |
|---|---|---|---|---|---|---|
| H1 · RSI 2 | 649 | +0,10 | 63 % | 4,1 séances | +4,0 | −41 R |
| H2 · Overnight | 16 385 | +0,002 | 52 % | 1 nuit | +2,3 | −167 R |
| H3 · TSMOM 12 m | 737 mois | +0,42 | 56 % | 21 séances | +18,3 | −84 R |
| Buy & hold | 737 mois | +0,52 | 60 % | 21 séances | +23,1 | −78 R |

R net cumulé en IS, par marché :

| | NQ | ES | CL | GC |
|---|---|---|---|---|
| H1 · RSI 2 | +26 | +17 | +0 | −12 |
| H2 · Overnight | +41 | −25 | −99 | −18 |
| H3 · TSMOM | +98 | +48 | +10 | +4 |
| Buy & hold | +120 | +91 | −61 | +17 |

## Ce qu'on apprend

1. **Overnight** : la dérive brute existe (+0,025 à +0,03 R par nuit sur NQ, ES, GC), mais le coût d'un aller-retour chaque nuit (0,014 à 0,027 R) en mange de 45 % (NQ) à plus de 100 % (ES). Sur 2010–2020, c'est perdant. Sur 2021–2026, ça fait exactement le Sharpe du buy & hold (1,080 contre 1,080) : on capte la hausse du marché, rien de plus.
2. **Momentum 12 mois** : long 71 % du temps. Les positions longues sur indices gagnent, les ventes à découvert sur indices perdent (−20 R sur ES, −18 R sur NQ). C'est un buy & hold dégradé sur ces 4 marchés. Avec seulement 4 marchés, il manque la diversification (taux, devises, 50+ futures) qui fait marcher la stratégie dans la littérature.
3. **RSI 2** : le côté achat sur indices est bon (ES +0,34 R/trade sur 136 trades, NQ +0,35 R sur 135). Les ventes à découvert et l'or perdent (GC à la vente : −0,52 R/trade).

## Observation exploratoire (hors pré-enregistrement — ne prouve rien)

La règle d'origine de Connors (2008) n'achète que sur indices. En isolant **RSI 2, achat seulement, NQ + ES** :

| | Sharpe | R / an | Pire drawdown | Temps en position |
|---|---|---|---|---|
| IS 2010–2020 | 0,29 | +3,6 | −31 R | ~15 % |
| OOS 2021–2026 | 1,04 | +9,8 | −9 R | ~15 % |
| *Buy & hold NQ + ES, IS* | *0,77* | *+20,2* | *−48 R* | *100 %* |
| *Buy & hold NQ + ES, OOS* | *0,73* | *+18,2* | *−35 R* | *100 %* |

Isolée **après** avoir vu les résultats, elle ne compte pas comme une découverte. L'IS est faible (Sharpe 0,29, moins bien que le buy & hold) et seul l'OOS est bon : c'est le profil classique d'une sélection a posteriori. À tester seulement en forward test, si on veut continuer.

## Conclusion du projet sur ces données

- Intraday (études 1 à 6) : l'edge ne passe pas les coûts.
- Swing multi-jours (étude 7) : les coûts passent, mais il n'y a pas d'edge au-delà du buy & hold.
- **Sur NQ, ES, CL et GC avec des données 1 minute, rien de simple ne bat « acheter et attendre ».**

## Fichiers

- Code : `trade/code/study7.py`
- Résultats : `trade/study7/summary_study7.csv`, `criteres_study7.csv`, `par_annee_study7.csv`
