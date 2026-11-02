---
title: Revue des stratégies publiées
subtitle: Ce que disent les papiers, les réplications indépendantes 2024–2026 et nos propres tests
num: 14
date: 2026-11-02
---

## En une phrase

**Les réplications indépendantes publiées en 2025–2026 arrivent à la même conclusion que nous : les edges intraday publiés sur les futures d'indices se sont effacés après publication, ou ne passent pas les coûts.** Les pistes encore vivantes sont surtout multi-jours, donc hors Topstep.

## Ce qu'on a cherché

Papiers académiques, rapports de la Fed de New York, préprints arXiv, et surtout **les réplications indépendantes avec code public** (dépôts GitHub), qui sont plus honnêtes que les papiers d'origine. Les articles en accès libre sont dans le dépôt `trade-data`, dossier `data_ext/papers/`.

## Comparatif

| Stratégie | Type | Topstep ? | Résultat publié | Après publication / réplications | Nos tests | Verdict |
|---|---|---|---|---|---|---|
| Noise area (Zarattini, Aziz & Barbon 2024) | Intraday | Oui | SPY 2007–2024 : Sharpe 1,33 net, 19,6 %/an | NQ : Sharpe 1,49 → 0,88 depuis mai 2024 ; ES : 1,78 → −0,19 (NostroBenJ). NQ t = 2,74 sur 2010–26 mais ES −0,20 (VigorTas). 71 % du gain sur les 14 meilleurs jours | Études 4–6 : +0,01 à +0,03 R, rien ne passe | **Mort sur ES, fragile sur NQ** |
| Momentum intraday (Gao et al. 2018 ; Baltussen et al. 2021) | Intraday | Oui | 1re demi-heure → dernière demi-heure | Échoue sur NQ après coûts (NostroBenJ) ; −0,8 pb par trade (nqedgelab) | Étude 4 H2 : échoue | **Mort** |
| Opening range breakout (Zarattini & Aziz 2023) | Intraday | Oui | QQQ 2016–2023 : +1 484 % contre +169 % pour QQQ | −0,014 R (nqedgelab) ; étude pré-enregistrée de 225 variantes sur 16 ans : « ne survit pas aux coûts » | Études 1 et 4 : échoue | **Mort** |
| 14 familles de signaux 5 min sur MNQ (Mesfin 2026) | Intraday | Oui | — | Aucune ne passe ; 11 familles ont un edge brut de 0,07 à 1,5 pt, sous le coût de 2 pts | — | **Mort** |
| Lundi acheteur (NostroBenJ 2026) | Intraday | Oui | NQ 2021–26 : t = +3,36, ~2 962 $/an/MNQ | — | **Étude 8** : 2010–2020 NQ t = 0,76, ES négatif | **Effet de période, écarté** |
| Dérive overnight 02:00–03:00 (Boyarchenko, Larsen & Whelan, NY Fed) | Overnight | Non | ES 1998–2020 : 3,7 %/an dans cette seule heure | **≈ 0 depuis 2021** (NY Fed, juillet 2026) ; les ETF NightShares ont fermé | Étude 7 H2 : échoue | **Mort** |
| Dérive pré-FOMC (Lucca & Moench 2015) | Intraday / overnight | En partie | +49 pb dans les 24 h avant le FOMC (1994–2011) | ≈ +0,05 % après 2011, disparue après 2016 (Kurov, Wolfe & Gilbert) | — | **Mort** |
| Tournant du mois (McConnell & Xu) | Multi-jours | Non | Sharpe 1,04 sur 1926–2005 | La partie « journée » seule échoue (NostroBenJ) | — | Non testé en multi-jours |
| Rebalancement des fonds de pension en fin de mois (EDHEC, SSRN 5122748) | Multi-jours (5 derniers jours du mois) | Non | Long/short S&P vs T-Note 10 ans : Sharpe 1,11 (≈ 1 net) sur 1997–2023, alpha ~9,5 %/an | Les auteurs disent la prévisibilité « encore plus forte » jusqu'en 2025 | — | **Candidat n°1** |
| Adjudications du Trésor (Lou, Yan & Zhang ; Robeco 2025) | Intraday possible | Oui (ZN) | Le T-Note 10 ans baisse ~6 pb avant l'adjudication puis remonte (1983–2024) | Pas de chiffre net de coûts publié | — | **Candidat n°2** (il faut ZN en 1 minute) |
| Suivi de tendance diversifié (Moskowitz, Ooi & Pedersen 2012) | Multi-semaines | Non | Fonctionne sur 50+ futures | Indice SG CTA Trend : Sharpe 0,14 sur 2010–2025 ; réplications 0,7–0,8 brut (arXiv 2507.15876) | Étude 7 H3 (4 marchés) : 0,49 | **Candidat n°3** (42 marchés maintenant disponibles) |
| RSI 2 (Connors 2008) | Multi-jours | Non | Achat sur indices | — | Étude 7 : échoue en général ; achat seulement NQ + ES : Sharpe 0,29 puis 1,04 (exploratoire) | À suivre en forward test seulement |

## Décroissance après publication

McLean & Pontiff (97 anomalies) : rendements **−26 % hors échantillon et −58 % dans les 5 ans après publication** (repris par Quantpedia). Nos 8 études et les réplications de 2025–2026 confirment ce schéma sur les futures intraday.

## La réalité des prop firms

Chiffres 2025 attribués à Topstep par un site tiers (non vérifiés à la source) : **16,8 % des Combines réussis**, et **un tiers des comptes financés** ont touché au moins un paiement.

## Prochaines études possibles (à pré-enregistrer)

1. **Rebalancement de fin de mois S&P vs T-Note** : le meilleur dossier publié (Sharpe ~1 net, récent). Test possible tout de suite avec les données journalières ajoutées (ES, ZN, SPY, IEF). Période 2023–2026 = vrai test après publication. Hors Topstep (positions sur 5 jours).
2. **Adjudications du T-Note 10 ans** en intraday sur ZN : compatible Topstep. Il faut acheter ZN en 1 minute chez Databento (quelques dollars de crédits) et le calendrier des adjudications (public, TreasuryDirect).
3. **Suivi de tendance sur 42 futures** : corrige le défaut de l'étude 7 (4 marchés seulement). Hors Topstep. Attendu : Sharpe 0,5–0,8 brut, faible sur 2010–2020.

## Données ajoutées au dépôt (branche `ajout-donnees-publiques-2026-11`)

42 futures journaliers depuis 2000, 21 futures en 1 heure (06/2024 → 10/2026), 30 indices et ETF, indices de volatilité CBOE, positions CFTC 2010–2026, facteurs Fama-French, courbe des taux US 2010–2026, 6 articles. Détail dans `data_ext/README.md`.

## Sources

- [NostroBenJ — 50 règles intraday publiées, pré-enregistrement + White reality check](https://github.com/NostroBenJ/intraday-strategy-replication)
- [VigorTas — réplication de « Beat the Market » sur 16 ans de NQ/ES](https://github.com/VigorTas/beat-the-market-replication)
- [nqedgelab — recherche NQ pré-enregistrée](https://github.com/nqedgelab/nq-research)
- [Mesfin 2026 — Structural Limits of OHLCV-Based Intraday Momentum Signals (arXiv)](https://arxiv.org/pdf/2605.04004)
- [Zarattini, Aziz & Barbon — Beat the Market (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172) et [liste Concretum](https://concretumgroup.com/papers/)
- [ORB : étude pré-enregistrée de 225 variantes (ResearchGate)](https://www.researchgate.net/publication/414294507_Opening-Range_Breakout_Does_Not_Survive_Trading_Costs_A_Pre-Registered_225-Cell_Study_on_Sixteen_Years_of_Futures_Data)
- [NY Fed — The Disappearing Overnight Drift (juillet 2026)](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/) et [Staff Report 917](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf)
- [Kurov, Wolfe & Gilbert — The Disappearing Pre-FOMC Announcement Drift](https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf)
- [EDHEC — rebalancement et rendements prévisibles (SSRN 5122748)](https://www.edhec.edu/sites/default/files/2026-03/Scientific%20paper.%20ssrn-5122748.pdf)
- [Robeco — Treasuries up for auction (2025)](https://www.robeco.com/en-hk/insights/2025/03/quant-chart-us-treasuries-up-for-auction)
- [CTA replication, short vs long-term trend (arXiv 2507.15876)](https://arxiv.org/pdf/2507.15876)
- [Quantpedia — performance après publication](https://quantpedia.com/how-do-investment-strategies-perform-after-publication/) et [tournant du mois](https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes)
- [Baltussen et al. — Hedging Demand and Market Intraday Momentum](https://www3.nd.edu/~zda/intramom.pdf)
- [Tradecovex — chiffres Topstep 2025 (source tierce)](https://tradecovex.com/guides/how-many-combines-passed-express-topstep-2025)
