"""Étude n°7 — exécution stricte du pré-enregistrement (doc 13).
3 stratégies multi-jours (RSI2 swing, overnight, TSMOM 12 mois) + référence buy & hold, 4 marchés, IS 2010-20 / OOS 2021-26.
Usage : python3 -I code/study7.py <dossier contenant nq_full.pkl ...> <dossier de sortie>
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

DATA, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
SPECS = {  # séance (minutes depuis minuit, ET), valeur du point du micro, tick — identiques aux études 4 à 6
    "NQ": dict(s=570, e=960, pv=2.0, tick=0.25),
    "ES": dict(s=570, e=960, pv=5.0, tick=0.25),
    "CL": dict(s=540, e=870, pv=100.0, tick=0.01),
    "GC": dict(s=525, e=810, pv=10.0, tick=0.10),
}
COMM = 1.0
IS_END = pd.Timestamp("2020-12-31")


def daily_bars(df, sp):
    """Barres journalières de la séance régulière, sur la série continue ajustée (Panama)."""
    df = df.sort_values("ts").reset_index(drop=True)
    sw = np.flatnonzero(df.instrument_id.to_numpy()[1:] != df.instrument_id.to_numpy()[:-1]) + 1  # 1re barre du nouveau contrat
    off = df.open.to_numpy()[sw] - df.close.to_numpy()[sw - 1]
    adj = np.zeros(len(df))
    for i, o in zip(sw, off):  # on décale tout ce qui précède le roll
        adj[:i] += o
    for c in ("open", "high", "low", "close"):
        df[c] = df[c] + adj
    sw_ts = df.ts.to_numpy()[sw]
    tod = df.ts.dt.hour * 60 + df.ts.dt.minute
    x = df[(tod >= sp["s"]) & (tod < sp["e"])].copy()
    x["d"] = x.ts.dt.date
    g = x.groupby("d")
    D = pd.DataFrame(dict(O=g.open.first(), H=g.high.max(), L=g.low.min(), C=g.close.last(), n=g.size(),
                          t_open=g.ts.first(), t_close=g.ts.last()))
    D = D[D.n >= 0.8 * (sp["e"] - sp["s"])].copy()
    D.index = pd.to_datetime(D.index)
    # roll pendant la nuit précédente (entre la clôture de la veille et l'ouverture du jour)
    tc_prev = D.t_close.shift().to_numpy()
    to = D.t_open.to_numpy()
    rolls = np.zeros(len(D), bool)
    for k in range(1, len(D)):
        rolls[k] = ((sw_ts > tc_prev[k]) & (sw_ts <= to[k])).any()
    D["roll_night"] = rolls
    pc = D.C.shift()
    tr = np.maximum(D.H, pc) - np.minimum(D.L, pc)
    D["ATR20"] = tr.rolling(20).mean().shift()  # 20 derniers TR, sans le jour du signal
    return D.drop(columns=["t_open", "t_close"])


def mtm(D, sp, segs, mkt, strat):
    """P&L journalier en R. Chaque segment : d, (i_in, 'O'|'C'), (i_out, 'O'|'C'), R (points), slip_in, slip_out, comm.
    Le coût de roll est payé chaque nuit de roll pendant laquelle la position est ouverte."""
    O, C, roll = D.O.to_numpy(), D.C.to_numpy(), D.roll_night.to_numpy()
    tick, cpt = sp["tick"], COMM / sp["pv"]
    pnl = np.zeros(len(D)); trades = []
    for s in segs:
        d, (ia, ta), (ib, tb), R = s["d"], s["in"], s["out"], s["R"]
        E = (O[ia] if ta == "O" else C[ia]) + (d * tick if s["slip_in"] else 0)
        X = (O[ib] if tb == "O" else C[ib]) - (d * tick if s["slip_out"] else 0)
        cost_pts = cpt if s["comm"] else 0.0
        p = np.zeros(len(D))
        last = E  # dernier prix de valorisation
        for t in range(ia, ib + 1):
            if t == ia:
                if ta == "C":
                    continue
                if t == ib:  # entrée et sortie le même jour (ne se produit pas ici)
                    p[t] += d * (X - E); last = X; continue
                p[t] += d * (C[t] - E); last = C[t]; continue
            if roll[t]:  # nuit de roll avec la position ouverte
                p[t] -= cpt + 2 * tick
            if t == ib:
                p[t] += d * (X - last)
            else:
                p[t] += d * (C[t] - last); last = C[t]
        p[ib] -= cost_pts
        pnl += p / R
        trades.append(dict(market=mkt, strat=strat, dir=d, date_in=D.index[ia], date_out=D.index[ib],
                           sessions=ib - ia, R_pts=R, r_net=p.sum() / R, r_brut=d * (X - E) / R))
    return pd.Series(pnl, index=D.index), trades


def rsi2(c):
    d = np.diff(c, prepend=np.nan)
    up, dn = np.clip(d, 0, None), np.clip(-d, 0, None)
    au, ad = np.full(len(c), np.nan), np.full(len(c), np.nan)
    au[2], ad[2] = up[1:3].mean(), dn[1:3].mean()
    for t in range(3, len(c)):
        au[t] = (au[t - 1] + up[t]) / 2; ad[t] = (ad[t - 1] + dn[t]) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 - 100 / (1 + au / ad)
    r[(ad == 0) & (au > 0)] = 100
    return r


def h1_rsi2(D, sp):
    C, atr = D.C.to_numpy(), D.ATR20.to_numpy()
    sma200 = D.C.rolling(200).mean().to_numpy(); sma5 = D.C.rolling(5).mean().to_numpy()
    r = rsi2(C)
    segs, t, n = [], 0, len(D)
    while t < n - 1:
        if np.isnan(sma200[t]) or np.isnan(atr[t]) or np.isnan(r[t]):
            t += 1; continue
        d = 1 if (C[t] > sma200[t] and r[t] < 10) else (-1 if (C[t] < sma200[t] and r[t] > 90) else 0)
        if not d:
            t += 1; continue
        a = t + 1  # entrée à l'ouverture de J+1
        u = a
        while u < n - 1:
            out = (C[u] > sma5[u]) if d > 0 else (C[u] < sma5[u])
            if out or (u - a + 1) >= 10:
                break
            u += 1
        b = min(u + 1, n - 1)
        segs.append(dict(d=d, **{"in": (a, "O"), "out": (b, "O")}, R=atr[t], slip_in=True, slip_out=True, comm=True))
        t = b  # à plat à partir de l'ouverture de b : premier signal possible à la clôture de b
    return segs


def h2_overnight(D, sp):
    atr = D.ATR20.to_numpy()
    return [dict(d=1, **{"in": (t, "C"), "out": (t + 1, "O")}, R=atr[t], slip_in=True, slip_out=True, comm=True)
            for t in range(len(D) - 1) if not np.isnan(atr[t])]


def monthly(D, sign_fn):
    """Segments mensuels : signal le dernier jour du mois, position du 1er jour du mois suivant au 1er jour du mois d'après."""
    C, atr = D.C.to_numpy(), D.ATR20.to_numpy()
    ym = D.index.to_period("M")
    last = np.flatnonzero(ym[:-1] != ym[1:])  # dernier jour de chaque mois (sauf le dernier mois)
    segs, prev = [], 0
    for j, t in enumerate(last):
        d = sign_fn(C, t)
        if d is None or np.isnan(atr[t]):
            prev = 0; continue
        a = t + 1
        b = last[j + 1] + 1 if j + 1 < len(last) else len(D) - 1
        nxt = sign_fn(C, last[j + 1]) if j + 1 < len(last) else None
        segs.append(dict(d=d, **{"in": (a, "O"), "out": (b, "O")}, R=atr[t],
                         slip_in=(d != prev), slip_out=(nxt != d), comm=(nxt != d)))
        prev = d
    return segs


def h3_tsmom(D, sp):
    def sgn(C, t):
        if t < 252:
            return None
        x = C[t] - C[t - 252]
        return 1 if x > 0 else (-1 if x < 0 else None)
    return monthly(D, sgn)


def bh(D, sp):
    return monthly(D, lambda C, t: 1 if t >= 252 else None)  # même date de départ que H3


def stats(p, label):
    """p : DataFrame des P&L journaliers en R (colonnes = marchés)."""
    tot = p.sum(axis=1)
    m = tot.groupby(tot.index.to_period("M")).sum()
    eq = tot.cumsum(); dd = (eq - eq.cummax()).min()
    sh = tot.mean() / tot.std() * np.sqrt(252) if tot.std() > 0 else np.nan
    ci = (m.mean() - 1.96 * m.std() / np.sqrt(len(m)), m.mean() + 1.96 * m.std() / np.sqrt(len(m)))
    yrs = len(tot) / 252
    return dict(periode=label, sharpe=sh, R_par_an=tot.sum() / yrs, R_mois=m.mean(), ic_bas=ci[0], ic_haut=ci[1],
                max_dd_R=dd, **{f"R_{k}": v for k, v in p.sum().items()})


if __name__ == "__main__":
    STRATS = {"H1_RSI2_swing": h1_rsi2, "H2_overnight": h2_overnight, "H3_TSMOM_12m": h3_tsmom, "BH_buy_hold": bh}
    P = {s: {} for s in STRATS}; TR = []
    for mkt, sp in SPECS.items():
        D = daily_bars(pd.read_pickle(DATA / f"{mkt.lower()}_full.pkl"), sp)
        D.to_csv(OUT / f"daily_{mkt}.csv")
        print(mkt, "séances", len(D), "| nuits de roll", int(D.roll_night.sum()), D.index[0].date(), "->", D.index[-1].date(), flush=True)
        for s, fn in STRATS.items():
            pnl, tr = mtm(D, sp, fn(D, sp), mkt, s)
            P[s][mkt] = pnl; TR += tr
    T = pd.DataFrame(TR); T.to_csv(OUT / "trades_study7.csv", index=False)
    rows, yearly = [], []
    for s in STRATS:
        p = pd.DataFrame(P[s]).fillna(0.0).sort_index()
        p.to_csv(OUT / f"pnl_jour_{s}.csv")
        for lab, q in (("IS 2010-20", p[p.index <= IS_END]), ("OOS 2021-26", p[p.index > IS_END]), ("Tout", p)):
            rows.append(dict(strat=s, **stats(q, lab)))
        y = p.sum(axis=1).groupby(p.index.year).sum()
        yearly.append(y.rename(s))
        t = T[T.strat == s]
        print(f"{s}: {len(t)} trades, {t.r_net.mean():+.3f} R/trade, gagnants {100*(t.r_net>0).mean():.0f} %, durée moy. {t.sessions.mean():.1f} séances")
    S = pd.DataFrame(rows); S.to_csv(OUT / "summary_study7.csv", index=False)
    Y = pd.concat(yearly, axis=1); Y.index.name = "annee"; Y.to_csv(OUT / "par_annee_study7.csv")
    pd.set_option("display.width", 200); pd.set_option("display.precision", 3)
    print(S.to_string(index=False)); print(Y.round(1).to_string())
    # critères
    crit = []
    bhS = S[S.strat == "BH_buy_hold"].set_index("periode").sharpe
    for s in ["H1_RSI2_swing", "H2_overnight", "H3_TSMOM_12m"]:
        x = S[S.strat == s].set_index("periode")
        ism, oos = x.loc["IS 2010-20"], x.loc["OOS 2021-26"]
        npos = sum(ism[f"R_{m}"] > 0 for m in SPECS)
        c = {"1_IS_sharpe>=0.5": ism.sharpe >= 0.5, "2_IS_IC_bas>0": ism.ic_bas > 0, "3_OOS_sharpe>=0.3": oos.sharpe >= 0.3,
             "4_IS_marches_pos>=3": npos >= 3,
             "5_mieux_que_BH": (ism.sharpe > bhS["IS 2010-20"]) and (oos.sharpe > bhS["OOS 2021-26"])}
        crit.append(dict(strat=s, IS_sharpe=ism.sharpe, OOS_sharpe=oos.sharpe, IS_ic_bas=ism.ic_bas, IS_marches_pos=npos,
                         BH_IS=bhS["IS 2010-20"], BH_OOS=bhS["OOS 2021-26"], **c, RETENUE=all(c.values())))
    K = pd.DataFrame(crit); K.to_csv(OUT / "criteres_study7.csv", index=False); print(K.to_string(index=False))
