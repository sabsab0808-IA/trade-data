# data_live — collecte automatique quotidienne

Rempli chaque soir (22:17 UTC, lundi–vendredi) par `.github/workflows/collecte.yml` avec `code/collecte_quotidienne.py`.

- `1m/<SYM>/<SYM>_<AAAA-MM>.csv` : barres 1 minute (Yahoo, contrat continu non ajusté) de 21 futures autorisés chez Topstep : ES, NQ, YM, RTY, CL, NG, GC, SI, HG, ZN, ZB, ZF, 6E, 6J, 6B, 6A, ZC, ZS, ZW, LE, HE.
- `1d/<SYM>.csv` : VIX, VIX3M, VIX9D, VVIX, SKEW, indices, ETF, futures en journalier.

Yahoo ne garde que ~30 jours de données 1 minute : la collecte quotidienne construit, jour après jour, un historique 1 minute gratuit à partir du 02/11/2026.
Horodatage UTC (`ts_utc` = ouverture de la minute). Lancement manuel possible : onglet **Actions** du dépôt → « Collecte quotidienne » → **Run workflow**.
