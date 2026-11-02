---
title: Agent de trading papier
subtitle: L'IA propose les positions et gère les deux comptes — suivi papier à partir du 02/11/2026
num: 16
date: 2026-11-02
---

## Ce que fait l'agent

Chaque matin du mardi au samedi à 08:33 (heure de Paris), avant l'ouverture américaine, une tâche planifiée :

1. télécharge les données (Yahoo Finance : NQ, ES et ZN en 1 minute sur ~29 jours ; Nasdaq-100, S&P 500, SPY et IEF en journalier) ;
2. rejoue toutes les séances depuis le 02/11/2026 avec les **4 stratégies figées** et les **règles de risque de chaque compte** ;
3. remplit la Google Sheet « TRADE » de Saber (https://docs.google.com/spreadsheets/d/1onXNuDqVmvT-DzMwfJhnlZiV6b2M7kOzTcElKGx3v-0) : 7 onglets « Agent · … » (tableau de bord, propositions pour la prochaine séance, positions ouvertes, journal, compte Topstep, trades refusés, stratégies). Les onglets Journal, Stats et Paramètres (journal manuel de Saber) ne sont jamais touchés. Trois onglets statiques complètent la feuille : « Agent · Backtests » (résultats par stratégie et par année), « Agent · Simulations » (doc 19) et « Agent · Études » (bilan des 10 études).

**Mode papier** : aucun ordre n'est envoyé. Les entrées et sorties sont calculées sur les vrais prix, avec les mêmes coûts que dans les études (1 tick de glissement par ordre, 1 $ par micro). L'agent ne modifie jamais les règles.

## Les deux comptes

| | Topstep 50K (papier) | Perso (papier) |
|---|---|---|
| Type | Intraday uniquement, à plat le soir | Positions sur plusieurs jours autorisées |
| Capital | 50 000 $ | 50 000 $ |
| Stratégies | S1 Noise area V4 · S2 Lundi acheteur | S3 RSI 2 achat · S4 Fin de mois |
| Risque par trade | ≤ 250 $ (600 $ pour le lundi) | 1 micro par signal (1 R = ATR20) |
| Limites globales | Perte max 2 000 $ en temps réel (plancher qui suit le solde de fin de journée, bloqué à 50 000 $) · objectif 3 000 $ · meilleur jour ≤ 55 % de l'objectif · 2 trades max par jour · perte journalière max 1 000 $ · risque ouvert ≤ 850 $ | Risque ouvert total ≤ 6 % du capital |

Si le compte Topstep touche sa perte max, il est marqué « ÉCHOUÉ » et l'agent ne propose plus rien dessus.

## Les 4 stratégies (règles figées)

| Stratégie | Règle | Statut honnête |
|---|---|---|
| S1 · Noise area V4 (NQ) | Bandes = max/min(ouverture, clôture veille) × (1 ± 1,5 σ(t)). Contrôle toutes les 30 min dès 10:00 ET. Stop 1 σ. Sortie au retour sous la bande/VWAP, sinon 15:58. 3 entrées max | Edge ≈ 0 après coûts ; négatif en 2025–26 |
| S2 · Lundi acheteur (NQ) | Lundi : achat 1 MNQ à 09:30, stop 0,5 × ATR14, vente 15:58 | Écarté par l'étude 8 ; le stop est un ajout (+0,16 R sur 2021–26, non testé avant) |
| S3 · RSI 2 achat (NQ + ES) | Clôture de l'indice > MM200 et RSI 2 < 10 → achat à l'ouverture ; sortie après une clôture > MM5 ou 10 séances | Exploratoire : Sharpe 0,29 (2010–20), 1,04 (2021–26) |
| S4 · Fin de mois actions / obligations | 5 séances avant la fin du mois : actions en avance sur les obligations → vente MES / achat ZN, sinon l'inverse ; sortie à la clôture du dernier jour | Non conforme (étude 9) : négatif depuis la publication |

Contrôle effectué le 02/11/2026 : rejouée sur NQ 2021–2026 (données Databento), S1 donne 342 trades à +0,10 R (2025 et 2026 négatifs), cohérent avec l'étude 5. Les règles Topstep (consistance, perte max en temps réel, 2 trades par jour) ont été vérifiées sur des cas tests.

## Comment s'en servir pendant les 2–3 semaines de papier

1. Avant 15:30 (heure de Paris), ouvre l'onglet **Agent · Propositions** : l'action à faire pour chaque stratégie (ACHAT, VENTE, Conserver, Conditionnel, Rien).
2. Si tu veux t'entraîner, passe les ordres en **démo** et compare avec le journal de l'agent le lendemain.
3. L'onglet **Agent · Tableau de bord** donne le solde, la marge avant la perte max et le reste à faire pour l'objectif.

## Limites

- **Pas de temps réel** : l'agent tourne une fois par jour. Les stratégies intraday (S1) sont données comme des **ordres conditionnels** (niveaux à surveiller), et leur résultat papier est calculé le lendemain matin.
- **Mémoire (version 2, 02/11/2026)** : Yahoo ne garde que ~30 jours en 1 minute. L'agent enregistre donc chaque jour les séances (ouverture, clôture) et les trades intraday dans le projet (`trade/agent/etat/`) et les réutilise le lendemain : le suivi peut durer au-delà de 30 jours.
- Roll de décembre (vers le 10/12) : NQ et ES changent de contrat chez Yahoo. L'agent compare chaque jour le future et l'indice au comptant et affiche une **alerte** dans le tableau de bord si l'écart dépasse 0,35 % (P&L papier possiblement faussé ce jour-là).
- **2–3 semaines, c'est 5 à 15 trades par stratégie : statistiquement, ça ne prouve rien.** Il faut 50+ trades par stratégie avant de conclure.

## Fichiers

`trade/agent/agent.py`, `trade/agent/config/` (calendriers FOMC et jours fériés NYSE 2026–2027). Copie dans le dépôt GitHub, dossier `agent/`.
