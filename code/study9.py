"""Étude n°9 — rebalancement de fin de mois SPY / IEF (doc 17). Usage : python3 -I code/study9.py <dossier indices_etf> <sortie>"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
COST = 0.0008
PUB_END = pd.Timestamp("2023-03-31")


def load(sym):
    d = pd.read_csv(SRC / f"{sym}_1d.csv")
    d["date"] = pd.to_datetime(d.ts_utc.str[:10])
    return d.set_index("date").adjclose


px = pd.concat([load("SPY").rename("a"), load("IEF").rename("o")], axis=1).dropna()
r = px.pct_change()
sd = r.rolling(60).std()
ym = px.index.to_period("M")
rows = []
months = sorted(set(ym))
for m in months[1:]:
    idx = np.flatnonzero(ym == m)
    prev = np.flatnonzero(ym == m - 1)
    if len(idx) < 8 or len(prev) == 0:
        continue
    N, S = idx[-1], idx[-1] - 5  # signal à la clôture de N-5
    base = prev[-1]
    ra = px.a.iloc[S] / px.a.iloc[base] - 1; ro = px.o.iloc[S] / px.o.iloc[base] - 1
    w = 0.6 * (1 + ra) / (0.6 * (1 + ra) + 0.4 * (1 + ro))
    if np.isnan(sd.a.iloc[S]) or np.isnan(sd.o.iloc[S]):
        continue
    k = sd.a.iloc[S] / sd.o.iloc[S]
    s = -1 if w > 0.6 else 1  # s = sens de la jambe actions
    Ra = px.a.iloc[N] / px.a.iloc[S] - 1; Ro = px.o.iloc[N] / px.o.iloc[S] - 1
    pnl = s * (Ra - k * Ro) - COST
    rows.append(dict(mois=str(m), signal=px.index[S].date(), sortie=px.index[N].date(), w_actions=w, sens_actions=s, k=k,
                     r_actions=Ra, r_oblig=Ro, pnl_net=pnl, pnl_actions_seule=s * Ra - COST / 2))
T = pd.DataFrame(rows); T["date"] = pd.to_datetime(T.sortie)
T.to_csv(OUT / "trades_study9.csv", index=False)


def st(x, col):
    v = x[col]
    return dict(trades=len(v), moy_bp=1e4 * v.mean(), sharpe=v.mean() / v.std() * np.sqrt(12), t=v.mean() / v.std() * np.sqrt(len(v)),
                gagnants=(v > 0).mean(), pire_pct=100 * v.min(), total_pct=100 * v.sum())


out = []
for lab, x in (("2002-03/2023 (papier)", T[T.date <= PUB_END]), ("04/2023-10/2026 (après)", T[T.date > PUB_END]), ("tout", T)):
    for col in ("pnl_net", "pnl_actions_seule"):
        out.append(dict(periode=lab, version=col, **st(x, col)))
S = pd.DataFrame(out); S.to_csv(OUT / "summary_study9.csv", index=False)
pd.set_option("display.width", 200); print(S.round(3).to_string(index=False))
c1 = S[(S.periode.str.startswith("2002")) & (S.version == "pnl_net")].sharpe.iloc[0] >= 0.5
c2 = S[(S.periode.str.startswith("04/2023")) & (S.version == "pnl_net")].moy_bp.iloc[0] > 0
print("critère 1 (Sharpe papier >= 0,5):", c1, "| critère 2 (après publication > 0):", c2, "| CONFORME:", c1 and c2)
Y = T.groupby(T.date.dt.year).pnl_net.sum().mul(100).round(2); Y.index.name = "annee"; Y.to_csv(OUT / "par_annee_study9.csv"); print(Y.to_string())
print(T.tail(6)[["mois", "signal", "w_actions", "sens_actions", "pnl_net"]].to_string(index=False))
