"""Étude n°15 (ex-étude 10) — suivi de tendance diversifié (TSMOM 12 mois) sur 29 ETF (doc 20).
Usage : python3 -I code/study15_tendance_etf.py <dossier etf_univers> <sortie>"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
CLASSES = {"Actions": ["SPY", "QQQ", "IWM", "EFA", "EEM", "EWJ", "VGK", "EWZ", "FXI", "VNQ"],
           "Obligations": ["TLT", "IEF", "LQD", "HYG", "TIP", "EMB"],
           "Matières premières": ["GLD", "SLV", "USO", "UNG", "DBA", "DBB"],
           "Devises": ["UUP", "FXE", "FXY", "FXB", "FXA", "FXC", "FXF"]}
UNIV = [s for v in CLASSES.values() for s in v]
COST, BORROW = 0.0010, 0.02

px = pd.concat({s: pd.read_csv(SRC / f"{s}_1d.csv", parse_dates=["date"]).set_index("date").adjclose for s in UNIV + ["SHY"]}, axis=1).sort_index()
px = px[px.index >= "2002-07-30"]
r = px.pct_change()
vol = r.rolling(60).std() * np.sqrt(252)
me = px.groupby(px.index.to_period("M")).apply(lambda d: d.index[-1])  # dernier jour de bourse de chaque mois
me = pd.DatetimeIndex(me.values)
W = {}
for t in me:
    i = px.index.get_loc(t)
    if i < 252:
        continue
    t0 = px.index[i - 252]
    ex = px.loc[t] / px.loc[t0] - 1
    cash = ex["SHY"]
    ok = [s for s in UNIV if not np.isnan(ex[s]) and not np.isnan(vol.loc[t, s]) and px[s].loc[:t].notna().sum() >= 253]
    if not ok:
        continue
    w = pd.Series(0.0, index=UNIV)
    for s in ok:
        w[s] = np.sign(ex[s] - cash) * 0.40 / vol.loc[t, s] / len(ok)
    W[t] = w
W = pd.DataFrame(W).T.sort_index()
start = W.index[0]


def run(weights, label, borrow=True):
    """Rendement journalier : poids fixés à la clôture du dernier jour du mois, appliqués au mois suivant."""
    wd = weights.reindex(px.index).ffill().shift(1)  # position effective à partir du jour suivant
    wd = wd[wd.index > start]
    ret = (wd * r[UNIV].reindex(wd.index)).sum(axis=1)
    turn = weights.diff().abs().sum(axis=1).fillna(weights.abs().sum(axis=1))
    cost = pd.Series(0.0, index=wd.index)
    for t, c in turn.items():
        nxt = wd.index[wd.index > t]
        if len(nxt):
            cost[nxt[0]] += COST * c
    if borrow:
        cost += (wd.clip(upper=0).abs().sum(axis=1)) * BORROW / 252
    return (ret - cost).rename(label)


tsm = run(W, "TSMOM")
lo = run(W.abs(), "Long-only risque égal", borrow=False)
b6040 = (0.6 * r["SPY"] + 0.4 * r["IEF"]).reindex(tsm.index).rename("60/40")
spy = r["SPY"].reindex(tsm.index).rename("SPY")
D = pd.concat([tsm, lo, b6040, spy], axis=1).dropna()
D.to_csv(OUT / "rendements_jour_study10.csv")


def stats(x):
    eq = (1 + x).cumprod(); dd = (eq / eq.cummax() - 1).min()
    return dict(rend_an=100 * ((1 + x).prod() ** (252 / len(x)) - 1), vol_an=100 * x.std() * np.sqrt(252),
                sharpe=x.mean() / x.std() * np.sqrt(252), pire_dd=100 * dd)


rows = []
for lab, a, b in (("2008-2011 (avant publication)", "2008-01-01", "2011-12-31"), ("2012-2026 (après publication)", "2012-01-01", "2026-12-31"),
                  ("2020-2026", "2020-01-01", "2026-12-31"), ("Tout", "2000-01-01", "2026-12-31")):
    q = D.loc[a:b]
    for c in D.columns:
        rows.append(dict(periode=lab, strategie=c, **stats(q[c]), correl_spy=q[c].corr(q["SPY"])))
S = pd.DataFrame(rows); S.to_csv(OUT / "summary_study10.csv", index=False)
pd.set_option("display.width", 220); print(S.round(3).to_string(index=False))
Y = D.groupby(D.index.year).apply(lambda q: (1 + q).prod() - 1).mul(100).round(1); Y.index.name = "annee"
Y.to_csv(OUT / "par_annee_study10.csv"); print(Y.to_string())
# par classe d'actifs (contribution TSMOM)
wd = W.reindex(px.index).ffill().shift(1); wd = wd[wd.index > start]
contrib = (wd * r[UNIV].reindex(wd.index))
C = []
for k, v in CLASSES.items():
    x = contrib[v].sum(axis=1)
    for lab, a, b in (("2012-2026", "2012-01-01", "2026-12-31"), ("2020-2026", "2020-01-01", "2026-12-31")):
        q = x.loc[a:b]; C.append(dict(classe=k, periode=lab, rend_an_brut=100 * q.mean() * 252, sharpe_brut=q.mean() / q.std() * np.sqrt(252)))
C = pd.DataFrame(C); C.to_csv(OUT / "par_classe_study10.csv", index=False); print(C.round(2).to_string(index=False))
# krachs
for lab, a, b in (("Krach 2008 (sept-déc)", "2008-09-01", "2008-12-31"), ("Covid (fév-mars 2020)", "2020-02-19", "2020-03-23"), ("2022", "2022-01-01", "2022-12-31")):
    q = D.loc[a:b]; print(lab, ((1 + q).prod() - 1).mul(100).round(1).to_dict())
p = S[S.periode.str.startswith("2012")].set_index("strategie")
p2 = S[S.periode == "2020-2026"].set_index("strategie")
c1 = p.loc["TSMOM", "sharpe"] >= 0.4; c2 = p.loc["TSMOM", "sharpe"] > p.loc["Long-only risque égal", "sharpe"]; c3 = p2.loc["TSMOM", "rend_an"] > 0
print("critère 1", c1, "| critère 2", c2, "| critère 3", c3, "| RETENUE", c1 and c2 and c3)
pd.DataFrame([dict(sharpe_2012_26=p.loc["TSMOM", "sharpe"], sharpe_longonly_2012_26=p.loc["Long-only risque égal", "sharpe"],
                   rend_2020_26=p2.loc["TSMOM", "rend_an"], c1=c1, c2=c2, c3=c3, RETENUE=c1 and c2 and c3)]).to_csv(OUT / "criteres_study10.csv", index=False)
W.iloc[-1][W.iloc[-1] != 0].round(3).rename("poids").to_csv(OUT / "positions_actuelles_study10.csv")
print("positions au", W.index[-1].date()); print(W.iloc[-1][W.iloc[-1] != 0].round(3).to_string())
