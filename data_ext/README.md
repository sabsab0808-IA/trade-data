# data_ext — données complémentaires (ajout du 02/11/2026)

Données publiques gratuites ajoutées pour élargir les tests au-delà de NQ, ES, CL et GC en 1 minute (dossier `data/`).
Tout est daté au **30/10/2026** (dernière séance complète) sauf mention contraire.

## yahoo/ — Yahoo Finance (gratuit)

| Dossier | Contenu | Période |
|---|---|---|
| `futures/` | 42 futures, **barres journalières**, contrat continu « front » (`ES=F`, `ZN=F`…) : indices (ES, NQ, YM, RTY), énergie (CL, BZ, NG, RB, HO), métaux (GC, SI, HG, PL, PA), taux (ZT, ZF, ZN, ZB), devises (6E, 6J, 6B, 6A, 6C, 6S, 6M, 6N), grains (ZC, ZS, ZW, KE, ZL, ZM), softs (KC, SB, CC, CT, OJ), viandes (LE, HE, GF), crypto (BTC, ETH) | 2000 → 10/2026 |
| `futures_1h/` | 21 futures autorisés chez Topstep, **barres de 1 heure** | 06/2024 → 10/2026 |
| `indices_etf/` | 30 indices et ETF : S&P 500, Nasdaq-100, Dow, Russell, VIX, VIX3M, VIX9D, VVIX, SKEW, taux US (^IRX, ^FVX, ^TNX, ^TYX), dollar index, SPY, QQQ, IWM, TLT, IEF, GLD, USO, HYG, LQD, EEM, EFA, Euro Stoxx 50, DAX, FTSE, Nikkei, Hang Seng | jusqu'à 1970 → 10/2026 |
| `inventaire_yahoo.csv` | Liste des fichiers avec dates et nombre de barres | |

Colonnes : `ts_utc, open, high, low, close, adjclose, volume`.
**Attention** : les futures Yahoo ne sont **pas ajustés** aux rolls (saut de prix à chaque changement d'échéance). Pour une stratégie tenue plusieurs jours, il faut détecter et neutraliser ces sauts. Le volume Yahoo des futures est peu fiable.

## cboe/ — indices de volatilité officiels CBOE

`VIX, VIX1D, VIX9D, VIX3M, VIX6M, VVIX, SKEW, OVX (pétrole), GVZ (or)` — OHLC journaliers, format `DATE (MM/JJ/AAAA), OPEN, HIGH, LOW, CLOSE`.
Usage typique : filtre de régime (VIX9D/VIX ou VIX/VIX3M > 1 = stress).

## cftc_cot/ — positions des traders (CFTC, Commitments of Traders), 2010 → 2026

- `fut_fin_txt_AAAA.zip` : Traders in Financial Futures (indices, taux, devises) — dealers, asset managers, hedge funds.
- `fut_disagg_txt_AAAA.zip` : Disaggregated (matières premières) — producteurs, swap dealers, managed money.
- `deacotAAAA.zip` : rapport « legacy » (commerciaux / non-commerciaux).
Hebdomadaire (positions du mardi, publiées le vendredi).

## fama_french/ — bibliothèque Kenneth French

Facteurs journaliers (marché, taille, value, momentum, 5 facteurs) et 48 portefeuilles sectoriels journaliers.

## treasury/ — courbe des taux US (Trésor américain)

`par_yield_AAAA.csv` : taux par maturité (1 mois → 30 ans), journalier, 2010 → 2026.

## papers/ — articles en accès libre utilisés pour la revue (doc 14 du projet)

- Boyarchenko, Larsen & Whelan — *The Overnight Drift* (NY Fed Staff Report 917)
- Baltussen, Da, Lammers & Martens — *Hedging Demand and Market Intraday Momentum*
- Mesfin (2026) — *Structural Limits of OHLCV-Based Intraday Momentum Signals* (arXiv 2605.04004)
- *Re-evaluating Short- and Long-Term Trend Factors in CTA Replication* (arXiv 2507.15876)
- EDHEC / SSRN 5122748 — rebalancement des fonds de pension et rendements prévisibles en fin de mois
- EFMA 2020 — rendements des futures du Trésor autour des adjudications

## Non récupéré

- FRED (Réserve fédérale de St. Louis) : bloqué depuis l'environnement de Claude. Les taux sont couverts par `treasury/` et `yahoo/indices_etf/`, le VIX par `cboe/`.
- SSRN : bloqué (403).

## Scripts

`code/download_yahoo.py` et `code/download_public.sh` re-téléchargent tout (sans clé).
