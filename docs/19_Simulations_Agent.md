---
title: Simulations de l'agent
subtitle: Ce qu'il faut attendre des 2–3 semaines de papier et d'un challenge Topstep — toutes les fenêtres de 2010 à 2026
num: 19
date: 2026-11-02
---

## La méthode

On rejoue les 4 stratégies de l'agent, avec **le même code et les mêmes règles de compte**, sur 16 ans d'historique, puis on regarde **toutes les fenêtres possibles** : chaque jour de 2010 à 2026 sert de point de départ. C'est une simulation historique, pas un tirage aléatoire : les séries de pertes et les régimes de marché sont conservés.

- **Topstep 50K** : S1 (noise area V4) et S2 (lundi acheteur) rejouées minute par minute sur NQ (Databento), avec la perte max en temps réel, la consistance 55 %, 2 trades par jour, etc. 1 966 fenêtres de 60 séances (≈ 3 mois) et ~3 900 fenêtres de 15 séances (≈ 3 semaines). Le lundi est remis à l'échelle du risque actuel (≈ 491 $ par trade).
- **Référence « zéro edge »** : les mêmes trades, avec la même volatilité, mais une espérance ramenée à −coûts. C'est ce que ferait un trader sans aucun avantage.
- **Compte perso** : S3 (RSI 2, trades de l'étude 7) et S4 (fin de mois, trades de l'étude 9), ramenés aux tailles d'aujourd'hui (1 MNQ, 1 MES).

## Compte Topstep 50K — challenge sur 60 séances

| | Réussi | Échoué (perte max) | Toujours en cours | Séances médianes pour réussir |
|---|---|---|---|---|
| **Agent (S1 + S2), 2010–2026** | **19,5 %** | 37,4 % | 43,0 % | 14 |
| Agent, 2021–2026 | 20,7 % | 24,1 % | 55,1 % | 15 |
| Agent, 2025–2026 | 24,1 % | 28,8 % | 47,1 % | 9 |
| S1 seule | 1,5 % | 5,3 % | 93,2 % | — |
| S2 seule | 11,3 % | 28,2 % | 60,5 % | 8 |
| **Référence zéro edge** | **12,0 %** | 52,8 % | 35,2 % | 15 |

Lecture :

- L'agent réussit **1,6 fois plus souvent** que le hasard (19,5 % contre 12 %) et échoue moins (37 % contre 53 %). C'est mieux que rien, **mais on reste sous le seuil du projet (2 fois le hasard)**, et presque tout vient du lundi acheteur, dont l'edge n'est pas significatif (t = 1,1 sur 2010–2020, 2,2 sur 2021–2026).
- **S1 seule ne fait presque rien** : avec 250 $ de risque max, la plupart des signaux sont sautés après 11:00 (stop trop large pour 1 MNQ).
- 43 % des fenêtres sont « toujours en cours » après 3 mois : chez Topstep, ça veut dire **payer d'autres mois d'abonnement**.

## Les 2–3 semaines de papier (15 séances)

| Compte | 5 % pire | 25 % | Médiane | 75 % | 5 % meilleur | Fenêtres perdantes | Trades en moyenne |
|---|---|---|---|---|---|---|---|
| Topstep (S1 + S2) | −1 473 $ | −628 $ | +64 $ | +789 $ | +2 100 $ | 47 % | 6,3 |
| Référence zéro edge | −1 664 $ | −855 $ | −163 $ | +599 $ | +1 882 $ | 56 % | 6,2 |
| Perso (S3 + S4) | −2 034 $ | −248 $ | +134 $ | +1 083 $ | +2 618 $ | 32 % | 1,7 |
| Garder 1 MNQ + 1 MES en permanence | −5 829 $ | −975 $ | +1 361 $ | +3 185 $ | +6 339 $ | 34 % | 0 |

**Ce qu'il faut retenir pour le papier :**

- Sur 3 semaines, **un résultat entre −1 500 $ et +2 100 $ est normal** côté Topstep, que la stratégie ait un edge ou non. Les deux distributions (agent et zéro edge) se recouvrent presque entièrement.
- **Il est donc impossible de juger les stratégies sur 2–3 semaines.** Un bon résultat ne prouvera rien, un mauvais non plus.
- Côté perso, il n'y aura en moyenne que **1 à 2 trades** en 3 semaines.

## Backtests par stratégie (aux tailles d'aujourd'hui)

| Stratégie | Période | Trades | Gagnants | Moyenne | P&L moyen | Pire trade |
|---|---|---|---|---|---|---|
| S1 · Noise area V4 | 2010–2020 | 710 | 34 % | +0,01 R | +2 $ | −304 $ |
| | 2021–2026 | 342 | 40 % | +0,10 R | +19 $ | −255 $ |
| S2 · Lundi acheteur (stop 0,5 ATR) | 2010–2020 | 458 | 49 % | +0,06 R | +28 $ | −533 $ |
| | 2021–2026 | 270 | 51 % | +0,15 R | +71 $ | −497 $ |
| S3 · RSI 2 achat (NQ + ES) | 2010–2020 | 167 | 69 % | +0,22 R | +152 $ | −3 850 $ |
| | 2021–2026 | 104 | 74 % | +0,54 R | +303 $ | −4 071 $ |
| S4 · Fin de mois | 2010–2020 | 132 | 58 % | +0,62 % | +238 $ | −3 803 $ |
| | 2021–2026 | 70 | 51 % | −0,06 % | −24 $ | −2 034 $ |

Le détail par année est dans `trade/sim/backtests_par_annee.csv` et dans l'onglet « Agent · Backtests » de la Google Sheet.

## Conclusion

Toutes les stratégies font mieux sur 2021–2026 que sur 2010–2020 : c'est la marque d'une période favorable (marché haussier, volatilité élevée), pas d'un edge stable. Le suivi papier sert surtout à **vérifier que l'agent fonctionne** et à t'entraîner à exécuter. Il ne validera aucune stratégie.

## Fichiers

`trade/sim/simulations.py`, `simulations_topstep.csv`, `simulations_perso.csv`, `backtests_resume.csv`, `backtests_par_annee.csv`.
