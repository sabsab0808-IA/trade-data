"""Validation sur données vierges NQ 2010-2020 (Databento) des variantes de l'étude n°3. Moteur et règles INCHANGÉS.

Deux lectures :
  * BRUT     : prix NQ tels quels. Les paramètres en points (FVG min 1 pt, buffer 1 pt, commission, 1 tick de glissement)
               pèsent jusqu'à 8x plus lourd qu'aujourd'hui quand le NQ valait 2 000.
  * NORMALISÉ: chaque contrat trimestriel est ramené au niveau de prix 2021-26 (x 15 000 / prix moyen du contrat),
               arrondi au tick. Les règles « en points » ont alors le même poids relatif qu'aujourd'hui.
Les journées de roll (contrat différent entre la veille et le jour) sont exclues : niveaux PDH/ONH faux.
"""
import sys
from dataclasses import replace
from datetime import time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from engine import Params, prepare_days, run_backtest, stats, load_news, TICK
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "results/nq"; OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_pickle(ROOT / "data/nq_1m.pkl")
news = load_news(ROOT / "config/news_nq_2010_2020.csv")

# journées propres : un seul contrat entre 09:30 la veille et 16:00 le jour
df["d"] = df.ts.dt.date
rth = df[(df.ts.dt.hour * 60 + df.ts.dt.minute).between(570, 959)]
dates = sorted(rth.d.unique()); ids = df.groupby("d").instrument_id.agg(lambda s: set(s))
roll = {dates[k] for k in range(1, len(dates)) if len(ids[dates[k]] | ids[dates[k - 1]]) > 1}

def normalise(df):
    x = df.copy()
    f = 15000.0 / x.groupby("instrument_id").close.transform("mean")
    for c in ["open", "high", "low", "close"]:
        x[c] = (x[c] * f / TICK).round() * TICK
    x["high"] = x[["open", "high", "close"]].max(axis=1); x["low"] = x[["open", "low", "close"]].min(axis=1)
    return x

A = Params(name="A_base")
VARIANTS = [A,
    replace(A, name="S1_premium_discount", pd_filter=True),
    replace(A, name="S2_biais_journalier", bias_filter=True),
    replace(A, name="S3_S1+S2", pd_filter=True, bias_filter=True),
    replace(A, name="S4_partiel_1R_puis_BE", partial_at_r=1.0),
    replace(A, name="S5_veille_11h-14h", use_on_levels=False, entry_start=time(11, 0), entry_end=time(14, 0))]
rows = []
for mode, data in [("BRUT", df), ("NORMALISE", normalise(df))]:
    days = [d for d in prepare_days(data[["ts", "open", "high", "low", "close", "volume"]]) if d["date"] not in roll]
    print(mode, "journées:", len(days), "| roll exclues:", len(roll))
    for p in VARIANTS:
        t = run_backtest(days, p, news)
        t.to_csv(OUT / f"trades_{mode}_{p.name}.csv", index=False)
        for lab, x in [("2010-15", t[t.date.dt.year <= 2015]), ("2016-20", t[t.date.dt.year >= 2016]), ("TOTAL", t)]:
            rows.append(dict(mode=mode, variante=p.name, periode=lab, **stats(x)))
out = pd.DataFrame(rows); out.to_csv(OUT / "summary_nq.csv", index=False)
pd.set_option("display.width", 250)
print(out[["mode", "variante", "periode", "trades", "win_rate", "expectancy_r", "ci95_low", "ci95_high", "profit_factor", "total_r", "max_dd_r", "avg_risk_pts", "trades_per_month"]].to_string(index=False))
