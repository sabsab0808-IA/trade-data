---
title: Synthèse du projet TRADE
subtitle: Où on en est au 02/11/2026 au soir (15 études, agent papier en route) — à lire en premier
num: 12
date: 2026-11-02
---

## En une phrase

**Après 15 études pré-enregistrées (~85 variantes, 16 ans de données), rien de fiable pour Topstep. Le seul effet qui survit est le suivi de tendance sur 40 futures (Sharpe ~0,5), hors Topstep et hors de portée avec 50 000 $. On n'achète pas de challenge ; l'agent tourne en papier.**

## Les études (numérotation unique)

| N° | Docs | Piste | Topstep ? | Meilleur résultat net | Verdict |
|---|---|---|---|---|---|
| 1 | 05 | Sweep + FVG, Silver Bullet, ORB, momentum (MNQ 2021–26) | Oui | +0,007 R | Pas d'edge |
| 2–3 | 06 / 06b | Filtres ICT : biais, premium/discount, partiels | Oui | +0,058 R | Non significatif |
| — | 08 | Validation des règles ICT sur NQ 2010–20 (données vierges) | Oui | +0,06 R | ICT abandonné |
| 4 | 09 / 09b | Noise area, momentum fin de séance, ORB + volume, fade de gap (NQ, ES, CL, GC) | Oui | +0,01 R | Rien ne passe |
| 5 | 10 / 10b | 6 variantes de la noise area | Oui | +0,03 R | Rien ne passe |
| 6 | 11 / 11b | Entrée à cours limité | Oui | +0,016 R | Rien ne passe |
| 7 | 13 / 13b | Swing RSI 2, overnight, momentum 12 mois (4 marchés) | Non | Sharpe 0,49 contre 0,45 buy & hold | Rien ne bat le buy & hold |
| 8 | 15 / 15b | Lundi acheteur intraday | Oui | t = 0,76 sur 2010–20 | Effet de période |
| 9 | 17 / 17b | Rebalancement de fin de mois actions / obligations (SPY/IEF) | Non | Sharpe 0,64 avant 2023, −0,48 après | Disparu après publication |
| 10 | 18 / 18b | Adjudications du T-Note 10 ans (ZN, intraday) | Oui | −37 $ par trade, t = −4,2 | Échec net |
| 11 | 18 / 18b | Veille de jour férié (ES, NQ) | Oui | +0,11 R, t = 1,3 | Non significatif |
| 12 | 18 / 18b | Tournant du mois (SPY) | Non | t = 0,24 après 2006 | Disparu |
| 13 | 18 / 18b | Régime VIX / VIX3M (SPY) | Non | +0,1 de Sharpe sur le buy & hold | Filtre de risque, pas un edge |
| **14** | 18 / 18b | **Suivi de tendance sur 40 futures** | Non | **Sharpe 0,47 après 2013** | **Conforme, mais irréalisable avec 50 000 $** |
| 15 | 20 / 20b | Suivi de tendance sur 29 ETF (version particulier) | Non | Sharpe −0,06 après 2013 | Non retenue |
| — | 14 | Revue des stratégies publiées et des réplications 2024–26 | — | — | Les réplications confirment nos résultats |
| — | 19 | Simulations de l'agent sur toutes les fenêtres 2010–26 | Oui | Challenge réussi 19,5 % contre 12 % au hasard | Sous le seuil (2 × hasard) |
| — | 16 | Agent de trading papier (comptes Topstep 50K + perso, Google Sheet) | — | — | En route depuis le 02/11/2026 |

**Note de numérotation** : deux sessions ont travaillé en parallèle le 02/11. La série « études 10 à 14 » (doc 18) garde ses numéros ; mon étude sur 29 ETF, publiée d'abord comme « étude 10 / doc 18 », est devenue l'**étude 15 / doc 20**.

## Études 14 et 15 : pourquoi deux verdicts opposés sur la même idée

Les deux sont justes (j'ai relancé le code de l'étude 14 : mêmes chiffres). Le pont sur 2013–2026 : ETF pré-enregistrée −0,06 → ETF avec les coûts des futures 0,23 → futures sans agricoles ni viandes 0,38 → 40 futures 0,47. L'écart vient surtout du **coût de la vente à découvert des ETF** (~0,3 de Sharpe) et des **marchés agricoles et des viandes** (~0,1), sans équivalent en ETF. Détail dans le doc 20b.

## Ce qu'on a appris (définitif)

1. **Les concepts ICT de manuel** (sweep, FVG, Silver Bullet, biais journalier) n'ont pas d'edge mesurable sur le Nasdaq.
2. **Les edges intraday publiés** (momentum de fin de séance, ORB, fade de gap, noise area, lundi, veilles de fériés, adjudications) ont disparu ou ne passent pas les coûts sur les futures 2010–2026.
3. **Le meilleur edge brut intraday** (noise area, ~+0,10 R) est du même ordre que le coût d'un aller-retour (~0,09 R). Il est négatif en 2025–2026.
4. **Une règle trouvée sur 5 ans peut être un effet de période** (lundi acheteur : t = 3,4 sur 2021–26, rien sur 2010–20).
5. **En multi-jours, les coûts ne sont plus le problème**, mais presque rien ne bat le buy & hold ou un 60/40 (Sharpe 0,99 sur 2012–26).
6. **Les effets publiés s'effacent après publication** : overnight, pré-FOMC, fin de mois, tournant du mois. Conforme à la littérature (−58 % de rendement dans les 5 ans après publication).
7. **Le seul effet robuste est le suivi de tendance diversifié en futures** (Sharpe ~0,5), décorrélé des actions, mais lent, et il demande plusieurs centaines de milliers de dollars.
8. **Passer un challenge ne prouve rien** : sans edge, on passe un Topstep 50K 12 à 16 % du temps (nos simulations), quasiment le taux officiel (16,8 %).

## Ressources

- **Données** : dépôt GitHub privé `sabsab0808-IA/trade-data`. Sur `main` : NQ, ES, CL, GC en 1 minute 06/2010 → 10/2026 (Databento). Sur la branche `ajout-donnees-publiques-2026-11` (à fusionner) : `data_ext/` (42 futures journaliers depuis 2000, 21 futures en 1 h, 44 ETF, VIX CBOE, COT CFTC, Fama-French, taux US, articles), `data_live/` (collecte automatique chaque soir du 1 minute de 21 futures Topstep, active après fusion), `agent/`, `sim/`, `results/`, `docs/`. Lecture avec le token GitHub de Saber (non stocké).
- **Code** : `trade/code/` (études 1 à 15), `trade/agent/` (agent), `trade/sim/` (simulations).
- **Tâche planifiée** du mardi au samedi à 08:33 (Paris) : forward test des modèles ICT (doc 07) + agent papier (doc 16), qui remplit la Google Sheet.
- **Google Sheet « TRADE »** : https://docs.google.com/spreadsheets/d/1onXNuDqVmvT-DzMwfJhnlZiV6b2M7kOzTcElKGx3v-0 — onglets Journal / Stats / Paramètres (journal manuel de Saber) + onglets « Agent · … » (tableau de bord, propositions, positions, journal, compte Topstep, refus, stratégies, backtests, simulations, études, tendance 40 futures).

## Pistes restantes

1. **Suivi papier de l'agent** (2–3 semaines à partir du 02/11) : sert à vérifier le fonctionnement et à s'entraîner à exécuter ; ne validera aucune stratégie.
2. **Suivi de tendance (étude 14)** : suivi théorique mensuel dans l'onglet « Agent · Tendance 40 futures ». Pour un particulier, l'équivalent réaliste est un ETF/fonds « managed futures ».
3. **Données plus fines** (tick, carnet d'ordres) pour de la microstructure : payantes, complexes, concurrence professionnelle.
4. **Valoriser le travail** : un vrai projet quant (15 études pré-enregistrées, 16 ans de données, simulations, agent automatisé) pour les candidatures en finance.

## Règles de travail du projet

- Toujours **pré-enregistrer** (hypothèses et critère publiés avant le calcul).
- Coûts réalistes : 1 $ par micro + 1 tick de glissement par ordre au marché ; stop et cible dans la même bougie = perte.
- **Un seul numéro par étude** : vérifier la synthèse avant d'attribuer un numéro (deux sessions peuvent travailler en parallèle).
- Tout est ajouté au projet (docs, code, résultats, décisions) — consigne permanente de Saber.
