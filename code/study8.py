"""Étude n°8 — « lundi acheteur » intraday (doc 15). Usage : python3 -I code/study8.py <dossier pkl> <sortie>"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

DATA, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
SPECS = {"NQ": dict(s=570, e=960, pv=2.0, tick=0.25), "ES": dict(s=570, e=960, pv=5.0, tick=0.25),
         "CL": dict(s=540, e=870, pv=100.0, tick=0.01), "GC": dict(s=525, e=810, pv=10.0, tick=0.10)}
COMM = 1.0
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]

rows = []
for mkt, sp in SPECS.items():
    df = pd.read_pickle(DATA / f"{mkt.lower()}_full.pkl")
    L = sp["e"] - sp["s"]
    tod = df.ts.dt.hour * 60 + df.ts.dt.minute
    x = df[(tod >= sp["s"]) & (tod < sp["e"])].copy()
    x["k"] = tod[x.index] - sp["s"]; x["d"] = x.ts.dt.date
    for d, g in x.groupby("d"):
        if len(g) < 0.8 * L:
            continue
        g = g.sort_values("k")
        last = g[g.k <= L - 2].iloc[-1]  # clôture de l'avant-dernière minute (ou la dernière minute traitée avant)
        rows.append(dict(market=mkt, date=pd.Timestamp(d), O=g.open.iloc[0], X=last.close, H=g.high.max(), Lo=g.low.min()))
D = pd.DataFrame(rows).sort_values(["market", "date"])
D["rng"] = D.H - D.Lo
D["ATR14"] = D.groupby("market").rng.transform(lambda s: s.rolling(14).mean().shift())
D["tick"] = D.market.map({m: s["tick"] for m, s in SPECS.items()}); D["pv"] = D.market.map({m: s["pv"] for m, s in SPECS.items()})
D["pts_net"] = (D.X - D.tick) - (D.O + D.tick) - COMM / D.pv
D["usd_micro"] = D.pts_net * D.pv
D["r_net"] = D.pts_net / D.ATR14
D["jour"] = D.date.dt.dayofweek.map(dict(enumerate(JOURS + ["samedi", "dimanche"])))
D = D.dropna(subset=["ATR14"])
D["periode"] = np.where(D.date <= "2020-12-31", "2010-2020", "2021-2026")
D.to_csv(OUT / "jours_study8.csv", index=False)


def tstat(s):
    return s.mean() / s.std() * np.sqrt(len(s)) if len(s) > 1 and s.std() > 0 else np.nan


S = (D.groupby(["market", "periode", "jour"]).agg(n=("r_net", "size"), R_moy=("r_net", "mean"), t=("r_net", tstat),
                                                  gagnants=("r_net", lambda s: (s > 0).mean()), usd_par_an=("usd_micro", "sum"))
     .reset_index())
yrs = D.groupby(["market", "periode"]).date.agg(lambda s: (s.max() - s.min()).days / 365.25)
S["usd_par_an"] = S.apply(lambda r: r.usd_par_an / yrs[(r.market, r.periode)], axis=1)
S["jour"] = pd.Categorical(S.jour, JOURS); S = S.sort_values(["market", "periode", "jour"])
S.to_csv(OUT / "summary_study8.csv", index=False)
pd.set_option("display.width", 200)
print(S.round(3).to_string(index=False))

nq = D[(D.market == "NQ") & (D.periode == "2010-2020")]
es = D[(D.market == "ES") & (D.periode == "2010-2020")]
nq2 = D[(D.market == "NQ") & (D.periode == "2021-2026")]
mon, oth = nq[nq.jour == "lundi"].r_net, nq[nq.jour != "lundi"].r_net
diff_t = (mon.mean() - oth.mean()) / np.sqrt(mon.var() / len(mon) + oth.var() / len(oth))
c = {"1_NQ_2010_20_t>=2": (mon.mean() > 0) and tstat(mon) >= 2.0,
     "2_ES_2010_20_>0": es[es.jour == "lundi"].r_net.mean() > 0,
     "3_lundi>autres_NQ_2010_20": mon.mean() > oth.mean(),
     "4_NQ_2021_26_>0": nq2[nq2.jour == "lundi"].r_net.mean() > 0}
K = pd.DataFrame([dict(NQ_1020_R=mon.mean(), NQ_1020_t=tstat(mon), NQ_1020_autres_R=oth.mean(), t_difference=diff_t,
                       ES_1020_R=es[es.jour == "lundi"].r_net.mean(), NQ_2126_R=nq2[nq2.jour == "lundi"].r_net.mean(),
                       NQ_2126_t=tstat(nq2[nq2.jour == "lundi"].r_net), **c, RETENUE=all(c.values()))])
K.to_csv(OUT / "criteres_study8.csv", index=False); print(K.T.to_string())
Y = D[D.jour == "lundi"].groupby(["market", D.date.dt.year]).r_net.sum().unstack(0).round(2)
Y.index.name = "annee"; Y.to_csv(OUT / "par_annee_lundi_study8.csv"); print(Y.to_string())
