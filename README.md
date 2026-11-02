# trade-data

Données et code du projet claude.ai **TRADE** (backtests pour un challenge Topstep 50K).
Ce dépôt contient le code, les calendriers et les données de marché.

## Données — `data/<SYM>/<SYM>_<année>.csv`

Source : **Databento**, dataset `GLBX.MDP3` (CME), schéma `ohlcv-1m`, contrat continu roulé au volume (`<SYM>.v.0`).
Horodatage UTC (`ts_event` = ouverture de la minute). Seules les minutes avec au moins une transaction existent.
Les versions lisibles directement en CSV sont fournies avec leurs copies compressées `.csv.zst` pour le chargement compact.

| Symbole | Marché | Période | Tick | Micro chez Topstep |
|---|---|---|---|---|
| NQ | Nasdaq-100 | 06/2010 → 10/2026 | 0,25 | MNQ = 2 $/pt |
| ES | S&P 500 | 06/2010 → 10/2026 | 0,25 | MES = 5 $/pt |
| CL | Pétrole WTI | 06/2010 → 10/2026 | 0,01 | MCL = 100 $/pt (1 $/tick) |
| GC | Or | 06/2010 → 10/2026 | 0,10 | MGC = 10 $/pt (1 $/tick) |

`instrument_id` change à chaque roll : exclure les journées où la veille et le jour ne portent pas sur le même contrat (niveaux de la veille faux).

## Charger
```bash
python3 -I load_databento.py data/NQ nq_1m.pkl
```
Le chargeur lit les fichiers `.csv.zst`; pour les autres outils, les mêmes données sont disponibles en `.csv`.

## Calendriers
- `news_nq_2010_2020.csv` : FOMC programmés 2010-2020 (site de la Fed ; 14:15 en 2010-12, 12:30 les jours de conférence de presse 2011-12, 14:00 dès 2013).
- Le calendrier 2021-2027 (CPI, NFP, FOMC) est dans le projet claude.ai : `trade/code/news_calendar.csv`.

## Code
- `engine.py` : moteur de backtest 1 minute (règles gelées de l'étude n°3 ; constantes MNQ).
- `load_databento.py` : chargeur générique. `load_nq_databento.py`, `run_study_nq.py` : doc 08 (validation NQ 2010-2020).
