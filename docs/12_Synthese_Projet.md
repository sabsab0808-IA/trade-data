---
title: Synthèse du projet TRADE
subtitle: Où on en est au 02/11/2026 (après l'étude 7) — à lire en premier
num: 12
date: 2026-11-02
---

## En une phrase

**Après 9 études pré-enregistrées (~65 variantes, 4 marchés, 16 ans de données 1 minute), aucune stratégie intraday simple ne bat les coûts, et aucune stratégie swing multi-jours ne bat le buy & hold. On n'achète pas de challenge Topstep.**

## Les études

| Doc | Étude | Marchés / période | Meilleur résultat net | Verdict |
|---|---|---|---|---|
| 05 | n°1 · Sweep + FVG, Silver Bullet, ORB, momentum | MNQ 2021–26 | +0,007 R (A) | Pas d'edge |
| 06 / 06b | n°3 · Filtres ICT (premium/discount, biais, partiels) | MNQ 2021–26 | +0,058 R (S2) | Non significatif |
| 08 | Validation sur données vierges | NQ 2010–20 | +0,06 R ; S5 → 0 | ICT pur abandonné |
| 09 / 09b | n°4 · Noise area, momentum fin de séance, ORB + volume, fade de gap | NQ, ES, CL, GC 2010–26 | +0,01 R (noise area) | Rien ne passe |
| 10 / 10b | n°5 · 6 variantes de la noise area (stops, filtres) | idem | +0,03 R | Rien ne passe |
| 11 / 11b | n°6 · Entrée à cours limité | idem | +0,016 R | Rien ne passe |
| 13 / 13b | n°7 · Swing RSI 2, overnight, momentum 12 mois (multi-jours) | NQ, ES, CL, GC 2010–26 | Sharpe IS 0,49 (TSMOM) vs 0,45 buy & hold | Rien ne bat le buy & hold |
| 14 | Revue des stratégies publiées et des réplications 2024–26 | — | — | Les réplications indépendantes confirment nos résultats |
| 15 / 15b | n°8 · Lundi acheteur intraday (t = 3,36 publié sur 2021–26) | NQ, ES, CL, GC 2010–26 | NQ 2010–20 : +0,02 R (t = 0,76) | Effet de période, écarté |
| 17 / 17b | n°9 · Rebalancement de fin de mois SPY / IEF | 2002–2026 | Sharpe 0,64 jusqu'en 2023, −0,48 après | Disparu après publication |
| 16 | Agent de trading papier (4 stratégies, comptes Topstep 50K et perso, Google Sheet) | depuis le 02/11/2026 | — | Suivi papier 2–3 semaines |

Critère intraday (études 4 à 6) : ≥ +0,08 R par trade en IS et en OOS, IC positif, ≥ 3 marchés sur 4, et Monte Carlo Topstep ≥ 2 × le hasard. Critère swing (étude 7) : Sharpe IS ≥ 0,5, IC positif, Sharpe OOS ≥ 0,3, ≥ 3 marchés sur 4, et Sharpe supérieur au buy & hold en IS et en OOS.

## Ce qu'on a appris (définitif)

1. **Les concepts ICT de manuel** (sweep, FVG, Silver Bullet, biais journalier) n'ont pas d'edge mesurable sur le Nasdaq.
2. **Les edges académiques connus** (momentum de fin de séance, ORB, fade de gap) ont disparu ou ne passent pas les coûts sur les futures 2010–2026.
3. **Le meilleur edge brut trouvé** (noise area, ~+0,10 R par trade) est du même ordre que le coût d'un aller-retour (~0,09 R). Élargir le stop ou entrer à cours limité ne change rien : l'edge baisse autant que le coût.
4. **2025–2026 est négatif pour toutes les variantes** de la noise area : l'effet s'érode.
5. **La fréquence compte autant que l'espérance** : il faut ~+12 R en 1 à 2 mois pour un Topstep 50K.
6. **En swing, les coûts ne sont plus un problème** (0,01 à 0,03 R par trade), mais l'overnight, le momentum 12 mois et le RSI 2 ne font pas mieux que d'acheter et attendre (Sharpe IS ≤ 0,49 contre 0,45 pour le buy & hold ; aucune ne passe les 5 critères). Seule piste exploratoire : RSI 2 achat seulement sur NQ + ES (Sharpe IS 0,29, OOS 1,04), trouvée a posteriori, donc à forward-tester uniquement.
7. **Une règle trouvée sur 5 ans peut être un effet de période** : le lundi acheteur (t = 3,36 sur 2021–26) ne marche pas sur 2010–2020.

## Ressources disponibles

- **Données** : dépôt GitHub privé `sabsab0808-IA/trade-data` (NQ, ES, CL, GC, 1 minute, 06/2010 → 10/2026, Databento, ~83 $ de crédits utilisés). Lecture avec le token GitHub de Saber (à redonner en début de session ; non stocké). Archive de secours : `trade-data.zip` chez Saber. Depuis le 02/11/2026 : dossier `data_ext/` (branche `ajout-donnees-publiques-2026-11`) avec 42 futures journaliers depuis 2000, 21 futures en 1 h, indices/ETF, VIX CBOE, COT CFTC, Fama-French, taux US, articles.
- **Code** : `trade/code/` (moteurs `engine.py` et `study4.py`, études 1 à 6, `study7.py` pour le swing, Monte Carlo, chargeurs).
- **Forward test automatique** (doc 07) et **agent de trading papier** (doc 16) : même tâche planifiée du mardi au samedi à 08:33 (Paris).
- **Google Sheet « TRADE »** : https://docs.google.com/spreadsheets/d/1onXNuDqVmvT-DzMwfJhnlZiV6b2M7kOzTcElKGx3v-0 — onglets Journal / Stats / Paramètres (journal manuel de Saber, créé dans une session précédente) + 7 onglets « Agent · … » remplis chaque matin par l'agent. Identifiant aussi dans `trade/agent/sheet_id.txt`.

## Pistes restantes

1. ~~Swing trading sur plusieurs jours~~ : testé dans l'étude 7, rien ne bat le buy & hold. Option restante : forward test de RSI 2 achat seulement sur NQ + ES (hors Topstep).
2. **Candidats issus de la revue (doc 14)** : rebalancement de fin de mois S&P vs T-Note (hors Topstep), adjudications du T-Note 10 ans en intraday sur ZN (Topstep, il faut ZN en 1 minute), suivi de tendance sur 42 futures (hors Topstep).
2b. **Données plus fines** (tick par tick, carnet d'ordres) pour des stratégies de microstructure : payantes, complexes, avec une concurrence professionnelle.
3. **Valoriser le travail** : un vrai projet quant (9 études pré-enregistrées, 16 ans de données, Monte Carlo) à mettre sur le CV pour des candidatures en finance.
4. **Forward test gratuit** de la noise area V4 sur NQ, en sachant qu'il faut s'attendre à zéro.

## Règles de travail du projet

- Toujours **pré-enregistrer** (hypothèses et critère publiés avant le calcul).
- Coûts réalistes : 1 $ par micro + 1 tick de glissement par ordre au marché ; stop et cible dans la même bougie = perte.
- Tout est ajouté au projet (docs, code, résultats, décisions) — consigne permanente de Saber.
