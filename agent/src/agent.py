"""Agent de trading PAPIER — propositions de positions + gestion globale de 2 comptes (doc 16 du projet TRADE).

Chaque matin (avant l'ouverture US) :
  1. télécharge les données (Yahoo Finance : futures 1 minute sur ~29 jours, indices et ETF journaliers) ;
  2. rejoue, depuis le 02/11/2026, les 4 stratégies figées avec les règles de risque de chaque compte ;
  3. écrit l'état des comptes, les positions ouvertes, le journal et les propositions pour la prochaine séance.

Rien n'est envoyé à un broker. Les règles ne sont JAMAIS modifiées par l'agent.
Usage : python3 -I src/agent.py <dossier config> <dossier sortie> [dossier état]
  Le dossier état (facultatif) contient la mémoire des runs précédents (seances.csv, candidats_intraday.csv) :
  elle permet de dépasser la limite de ~30 jours de Yahoo. Les fichiers mis à jour sont réécrits dans <sortie>/etat/.
"""
import json, sys, time, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import numpy as np, pandas as pd

CFG, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
ETAT = Path(sys.argv[3]) if len(sys.argv) > 3 else None
(OUT / "etat").mkdir(exist_ok=True)
START = date(2026, 11, 2)          # premier jour du suivi papier
NY = "America/New_York"
SPEC = {"NQ": dict(sym="NQ=F", micro="MNQ", pv=2.0, tick=0.25, comm=1.0),
        "ES": dict(sym="ES=F", micro="MES", pv=5.0, tick=0.25, comm=1.0),
        "ZN": dict(sym="ZN=F", micro="ZN", pv=1000.0, tick=1 / 64, comm=2.0)}  # pas de micro ZN : contrat standard
S0, S1 = 570, 960                  # séance 09:30-16:00 ET (comme les études 4 à 8)
L = S1 - S0
FOMC = {pd.Timestamp(d).date(): int(t[:2]) * 60 + int(t[3:]) for d, t in pd.read_csv(CFG / "fomc_2026_2027.csv")[["date", "time_et"]].values}
HOL = set(pd.to_datetime(pd.read_csv(CFG / "nyse_feries_2026_2027.csv").date).dt.date)

# règles des comptes (figées)
TOP = dict(capital=50_000.0, mll=2_000.0, objectif=3_000.0, consistance=0.55, dll=1_000.0, max_trades_jour=2,
           risque_max_trade=250.0, risque_max_lundi=600.0, risque_ouvert_max=850.0)
PERSO = dict(capital=50_000.0, risque_ouvert_max_pct=0.06)

STATUTS = {
    "S1 · Noise area V4 (NQ)": "Edge ≈ 0 après coûts (études 4–5), négatif en 2025–26",
    "S2 · Lundi acheteur (NQ)": "Écarté par l'étude 8 (nul sur 2010–20) ; stop ajouté non backtesté",
    "S3 · RSI 2 achat (NQ + ES)": "Exploratoire (étude 7) : Sharpe 0,29 en 2010–20, 1,04 en 2021–26",
    "S4 · Fin de mois actions/oblig.": "Non conforme (étude 9) : négatif depuis la publication",
}


# ---------------------------------------------------------------- données
def yahoo(sym, interval, p1, p2):
    q = f"interval={interval}&period1={int(p1)}&period2={int(p2)}&includeAdjustedClose=true"
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?{q}"
    for a in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
            res = r["chart"]["result"][0]
            if not res.get("timestamp"):
                return pd.DataFrame()
            qq = res["indicators"]["quote"][0]
            adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose") or qq["close"]
            df = pd.DataFrame(dict(ts=pd.to_datetime(res["timestamp"], unit="s", utc=True).tz_convert(NY), open=qq["open"],
                                   high=qq["high"], low=qq["low"], close=qq["close"], adj=adj, volume=qq["volume"]))
            return df.dropna(subset=["open", "high", "low", "close"])
        except Exception as e:  # noqa: BLE001
            err = e; time.sleep(5)
    raise RuntimeError(f"Yahoo indisponible pour {sym} : {err}")


def minute(sym):
    now = time.time(); parts = []
    for k in range(4):  # 4 fenêtres de 7 jours = 28 jours (limite Yahoo : ~30 jours en 1 minute)
        p2 = now - k * 7 * 86400; parts.append(yahoo(sym, "1m", p2 - 7 * 86400, p2))
    df = pd.concat(parts).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    df["volume"] = df.volume.fillna(0)
    return df


def daily(sym, years=2):
    now = time.time(); d = yahoo(sym, "1d", now - years * 366 * 86400, now)
    d["date"] = d.ts.dt.date
    return d.set_index("date")


def sessions(df):
    """Grille minute 09:30-16:00 par séance. complete = ≥ 80 % des minutes (règle des études)."""
    tod = df.ts.dt.hour * 60 + df.ts.dt.minute
    x = df[(tod >= S0) & (tod < S1)].copy(); x["k"] = (tod[x.index] - S0).astype(int); x["d"] = x.ts.dt.date
    out = []
    for d, g in x.groupby("d"):
        if len(g) < 30:
            continue
        o = np.full(L, np.nan); h = o.copy(); l = o.copy(); c = o.copy(); v = np.zeros(L); k = g.k.to_numpy()
        o[k], h[k], l[k], c[k], v[k] = g.open, g.high, g.low, g.close, g.volume
        first = np.flatnonzero(~np.isnan(c))[0]
        o[:first] = h[:first] = l[:first] = c[:first] = o[first]
        c = pd.Series(c).ffill().to_numpy(); m = np.isnan(o); o[m] = h[m] = l[m] = c[m]
        out.append(dict(date=d, o=o, h=h, l=l, c=c, v=v, n=len(g), complete=len(g) >= 0.8 * L,
                        close=g[g.k <= L - 2].close.iloc[-1] if (g.k <= L - 2).any() else g.close.iloc[-1]))
    for i in range(1, len(out)):
        out[i]["pc"] = out[i - 1]["close"]
    if out:
        out[0]["pc"] = np.nan
    return out


def next_session(d):
    n = d + timedelta(days=1)
    while n.weekday() >= 5 or n in HOL:
        n += timedelta(days=1)
    return n


def trading_days(y, m):
    d = date(y, m, 1); out = []
    while d.month == m:
        if d.weekday() < 5 and d not in HOL:
            out.append(d)
        d += timedelta(days=1)
    return out


# ---------------------------------------------------------------- simulation intraday (logique des études 4-5)
def run_trade(day, i0, d, entry, stop, i_exit, sp, check=None):
    o, h, l, c, tick = day["o"], day["h"], day["l"], day["c"], sp["tick"]
    mae = 0.0
    for j in range(i0, L):
        mae = max(mae, (entry - l[j]) if d > 0 else (h[j] - entry))
        if (l[j] <= stop) if d > 0 else (h[j] >= stop):
            px = o[j] if ((d > 0 and o[j] < stop) or (d < 0 and o[j] > stop)) else stop
            return px - d * tick, "stop", j, mae
        if j >= i_exit:
            return c[j] - d * tick, "fin de séance", j, mae
        if check is not None and check(j, d):
            return o[j + 1] - d * tick, "règle (repasse la bande/VWAP)", j + 1, mae
    return c[L - 1] - d * tick, "fin de séance", L - 1, mae


def exit_index(dd):
    i = L - 2; t = FOMC.get(dd)
    if t is not None:
        flat = min(13 * 60 + 55, t - 5) - S0
        i = min(i, flat - 1)
    return i


def hhmm(i):
    m = S0 + i
    return f"{m // 60:02d}:{m % 60:02d}"


def noise_profile(days, k):
    return np.mean([np.abs(days[k - m]["c"] / days[k - m]["o"][0] - 1) for m in range(1, 15)], axis=0)


def s1_noise(days, sp):
    """Noise area V4 : bandes 1,5 σ, stop 1 σ, contrôles toutes les 30 min, 3 entrées max (étude 5)."""
    cand = []
    for k in range(14, len(days)):
        day = days[k]
        if day["date"] < START or not day["complete"]:
            continue
        if any(not days[k - m]["complete"] for m in range(1, 15)):
            continue
        O, PC = day["o"][0], day["pc"]
        sig = noise_profile(days, k)
        ub, lb = max(O, PC) * (1 + 1.5 * sig), min(O, PC) * (1 - 1.5 * sig)
        o, h, l, c, v = day["o"], day["h"], day["l"], day["c"], day["v"]
        cv = np.cumsum(v); vwap = np.where(cv > 0, np.cumsum((h + l + c) / 3 * v) / np.maximum(cv, 1e-9), c)
        ie = exit_index(day["date"])
        checks = set(range(29, L - 30, 30)); last_entry = max([t for t in checks if t < ie] + [-1])

        def check(j, d):
            return j in checks and (c[j] < max(ub[j], vwap[j]) if d > 0 else c[j] > min(lb[j], vwap[j]))

        n_ent, t, forbid = 0, 29, (None, 0)
        while t <= last_entry and n_ent < 3:
            if t in checks:
                d = 1 if c[t] > ub[t] else (-1 if c[t] < lb[t] else 0)
                if forbid[0] == t and d == forbid[1]:
                    d = 0
                if d:
                    entry = o[t + 1] + d * sp["tick"]; risk = sig[t] * O
                    n = int(TOP["risque_max_trade"] // (risk * sp["pv"]))
                    if risk >= 4 * sp["tick"] and n >= 1:
                        x, why, jx, mae = run_trade(day, t + 1, d, entry, entry - d * risk, ie, sp, check)
                        cand.append(dict(date=day["date"], heure=hhmm(t + 1), i=t + 1, strat="S1 · Noise area V4 (NQ)", marche="MNQ",
                                         sens=d, n=n, entree=entry, stop=entry - d * risk, sortie=x, heure_sortie=hhmm(jx), j_out=jx, raison=why,
                                         risque_usd=n * risk * sp["pv"], mae_usd=n * mae * sp["pv"],
                                         pnl_usd=n * ((x - entry) * d * sp["pv"] - sp["comm"])))
                        n_ent += 1
                        if why.startswith("règle"):
                            t = jx - 1; forbid = (t, d); continue
                        t = jx
            t += 1
    return cand


def s2_monday(days, sp):
    """Lundi acheteur : achat à 09:30, sortie 15:58 ; stop de protection 0,5 × ATR14 (exigé par la MLL Topstep)."""
    cand = []
    for k in range(14, len(days)):
        day = days[k]
        if day["date"] < START or day["date"].weekday() != 0 or not day["complete"]:
            continue
        atr = np.mean([days[k - m]["h"].max() - days[k - m]["l"].min() for m in range(1, 15)])
        entry = day["o"][0] + sp["tick"]; risk = 0.5 * atr
        if risk * sp["pv"] > TOP["risque_max_lundi"]:
            continue
        x, why, jx, mae = run_trade(day, 0, 1, entry, entry - risk, L - 2, sp)
        cand.append(dict(date=day["date"], heure="09:30", i=0, strat="S2 · Lundi acheteur (NQ)", marche="MNQ", sens=1, n=1,
                         entree=entry, stop=entry - risk, sortie=x, heure_sortie=hhmm(jx), j_out=jx, raison=why, risque_usd=risk * sp["pv"],
                         mae_usd=mae * sp["pv"], pnl_usd=(x - entry) * sp["pv"] - sp["comm"]))
    return cand


def topstep_ledger(cands):
    """Applique les règles du compte Topstep 50K (papier) dans l'ordre chronologique."""
    bal, peak_eod, best_day, status = TOP["capital"], TOP["capital"], 0.0, "En cours"
    taken, refused, eod = [], [], []
    by_day = {}
    for t in sorted(cands, key=lambda r: (r["date"], r["i"])):
        by_day.setdefault(t["date"], []).append(t)
    for dd in sorted(by_day):
        if status != "En cours":
            refused += [dict(t, refus="compte clôturé") for t in by_day[dd]]; continue
        floor = min(peak_eod - TOP["mll"], TOP["capital"]); day_pnl, n, worst, open_until = 0.0, 0, bal, []
        for t in by_day[dd]:
            open_risk = sum(r["risque_usd"] for r in open_until if r["_fin"] > t["i"])
            if n >= TOP["max_trades_jour"]:
                refused.append(dict(t, refus="2 trades max par jour")); continue
            if day_pnl <= -TOP["dll"]:
                refused.append(dict(t, refus="perte journalière max atteinte")); continue
            if open_risk + t["risque_usd"] > TOP["risque_ouvert_max"]:
                refused.append(dict(t, refus="risque ouvert total > 850 $")); continue
            worst = min(worst, bal + day_pnl - t["mae_usd"])
            day_pnl += t["pnl_usd"]; n += 1
            t2 = dict(t); t2["_fin"] = t["j_out"]
            open_until.append(t2); taken.append(t)
        bal += day_pnl; best_day = max(best_day, day_pnl)
        if worst <= floor or bal <= floor:
            status = "ÉCHOUÉ (perte max touchée)"
        peak_eod = max(peak_eod, bal)
        target = max(TOP["objectif"], best_day / TOP["consistance"])
        if status == "En cours" and bal - TOP["capital"] >= target:
            status = "RÉUSSI (objectif atteint)"
        eod.append(dict(date=dd, pnl_jour=round(day_pnl, 2), solde=round(bal, 2), plancher_mll=round(min(peak_eod - TOP["mll"], TOP["capital"]), 2),
                        objectif=round(target, 2), meilleur_jour=round(best_day, 2), trades=n, statut=status))
    return taken, refused, eod, bal, status


# ---------------------------------------------------------------- stratégies multi-jours (compte perso)
def rsi2(c):
    d = np.diff(c, prepend=np.nan); up, dn = np.clip(d, 0, None), np.clip(-d, 0, None)
    au, ad = np.full(len(c), np.nan), np.full(len(c), np.nan); au[2], ad[2] = up[1:3].mean(), dn[1:3].mean()
    for t in range(3, len(c)):
        au[t] = (au[t - 1] + up[t]) / 2; ad[t] = (ad[t - 1] + dn[t]) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 - 100 / (1 + au / ad)
    r[(ad == 0) & (au > 0)] = 100
    return r


def s3_rsi2(idx_daily, fut_days, mkt):
    """Signal sur l'indice au comptant (clôture), exécution sur le micro à l'ouverture suivante."""
    sp = SPEC[mkt]; C = idx_daily.close.to_numpy(); dates = list(idx_daily.index)
    if isinstance(fut_days, dict):
        fo = fut_days
    else:
        fo = {d["date"]: d for d in fut_days}
    sma200 = pd.Series(C).rolling(200).mean().to_numpy(); sma5 = pd.Series(C).rolling(5).mean().to_numpy(); r = rsi2(C)
    trades, pos, t = [], None, 0
    i0 = next(i for i, d in enumerate(dates) if d >= START - timedelta(days=7))
    for t in range(i0, len(dates)):
        d0 = dates[t]
        if pos is None:
            if C[t] > sma200[t] and r[t] < 10:
                ent_day = next_session(d0)
                if ent_day < START:
                    continue
                pos = dict(strat="S3 · RSI 2 achat (NQ + ES)", marche=sp["micro"], sens=1, n=1, signal=d0, date=ent_day,
                           entree=fo[ent_day]["o"][0] + sp["tick"] if ent_day in fo else np.nan, seances=0,
                           R_usd=None, info=f"RSI2 {r[t]:.1f}, clôture {C[t]:,.2f} > MM200 {sma200[t]:,.2f}")
        else:
            if d0 < pos["date"]:
                continue
            pos["seances"] += 1
            if C[t] > sma5[t] or pos["seances"] >= 10:
                ex = next_session(d0)
                pos.update(sortie_prevue=ex, raison="clôture > MM5" if C[t] > sma5[t] else "10 séances")
                if ex in fo:
                    pos.update(date_sortie=ex, sortie=fo[ex]["o"][0] - sp["tick"]); trades.append(pos); pos = None
    state = dict(close=C[-1], sma200=sma200[-1], sma5=sma5[-1], rsi=r[-1], date=dates[-1])
    return trades, pos, state


def s4_month_end(spy, ief, fut):
    """Signal à la clôture de N-5 (SPY/IEF ajustés) ; exécution MES contre ZN à la clôture de N-5, sortie à la clôture de N."""
    px = pd.concat([spy.adj.rename("a"), ief.adj.rename("o")], axis=1).dropna(); r = px.pct_change(); sd = r.rolling(60).std()
    trades, pos, info = [], None, {}
    months = sorted({(d.year, d.month) for d in px.index if d >= START - timedelta(days=40)} | {(START.year, START.month)})
    for (y, m) in months:
        td = trading_days(y, m)
        if len(td) < 8:
            continue
        S, N = td[-6], td[-1]
        prev = [d for d in px.index if (d.year, d.month) < (y, m)]
        if S < START or not prev:
            info = dict(N_moins_5=S, N=N); continue
        info = dict(N_moins_5=S, N=N)
        if S not in px.index:
            continue
        base = prev[-1]
        ra, ro = px.a[S] / px.a[base] - 1, px.o[S] / px.o[base] - 1
        w = 0.6 * (1 + ra) / (0.6 * (1 + ra) + 0.4 * (1 + ro)); k = sd.a[S] / sd.o[S]; s = -1 if w > 0.6 else 1
        es, zn = fut["ES"].get(S), fut["ZN"].get(S)
        if es is None or zn is None:
            continue
        n_zn = max(1, round(k * es * SPEC["ES"]["pv"] / (zn * SPEC["ZN"]["pv"])))
        pos = dict(strat="S4 · Fin de mois actions/oblig.", marche=f"1 MES {'achat' if s > 0 else 'vente'} / {n_zn} ZN {'vente' if s > 0 else 'achat'}",
                   sens=s, n=1, n_zn=n_zn, signal=S, date=S, entree_es=es + s * SPEC["ES"]["tick"], entree_zn=zn - s * SPEC["ZN"]["tick"],
                   info=f"poids actions {w:.3f} ({'> 0,6 : vente actions' if s < 0 else '< 0,6 : achat actions'}), k {k:.2f}", sortie_prevue=N)
        if N in fut["ES"] and N in fut["ZN"]:
            xe, xz = fut["ES"][N] - s * SPEC["ES"]["tick"], fut["ZN"][N] + s * SPEC["ZN"]["tick"]
            pnl = s * (xe - pos["entree_es"]) * SPEC["ES"]["pv"] - s * n_zn * (xz - pos["entree_zn"]) * SPEC["ZN"]["pv"] - SPEC["ES"]["comm"] - n_zn * SPEC["ZN"]["comm"]
            pos.update(date_sortie=N, sortie_es=xe, sortie_zn=xz, pnl_usd=pnl); trades.append(pos); pos = None
    return trades, pos, info


# ---------------------------------------------------------------- programme principal
def fmt(x, n=2):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:,.{n}f}".replace(",", " ").replace(".", ",")


def main():
    warn = []
    mins = {m: minute(SPEC[m]["sym"]) for m in SPEC}
    now_ny = pd.Timestamp.now(tz=NY); today = now_ny.date()
    finished = lambda dd: dd < today or now_ny.hour * 60 + now_ny.minute >= S1 + 5  # séance du jour pas encore terminée -> exclue
    days = {m: [d for d in sessions(mins[m]) if finished(d["date"]) or d["date"] == today] for m in SPEC}
    for m in SPEC:  # la séance en cours ne sert qu'à lire l'ouverture (entrées RSI 2) : jamais simulée, jamais clôture
        for d in days[m]:
            if not finished(d["date"]):
                d["complete"] = False; d["en_cours"] = True
    # ---- mémoire : séances (ouverture/clôture) des runs précédents, pour dépasser la fenêtre Yahoo
    SE = pd.DataFrame([dict(date=d["date"], marche=m, open=d["o"][0], close=d["close"], high=float(np.nanmax(d["h"])), low=float(np.nanmin(d["l"])),
                            complete=bool(d["complete"])) for m in SPEC for d in days[m] if not d.get("en_cours")])
    if ETAT is not None and (ETAT / "seances.csv").exists():
        old = pd.read_csv(ETAT / "seances.csv"); old["date"] = pd.to_datetime(old.date).dt.date
        key = set(zip(SE.date, SE.marche)); old = old[[(d, m) not in key for d, m in zip(old.date, old.marche)]]
        SE = pd.concat([old, SE], ignore_index=True)
    SE = SE.sort_values(["marche", "date"]).reset_index(drop=True); SE.to_csv(OUT / "etat" / "seances.csv", index=False)
    closes = {m: dict(zip(SE[SE.marche == m].date, SE[SE.marche == m].close)) for m in SPEC}
    opens = {m: {d: {"o": [o]} for d, o in zip(SE[SE.marche == m].date, SE[SE.marche == m].open)} for m in SPEC}
    for m in SPEC:  # ouverture de la séance en cours (pour les entrées RSI 2 du jour)
        for d in days[m]:
            if d.get("en_cours"):
                opens[m][d["date"]] = {"o": [d["o"][0]]}
    # alerte roll : écart entre le future (Yahoo, non ajusté) et l'indice au comptant sur une séance
    def roll_check(mk, idx):
        c = pd.Series(closes[mk]); c.index = pd.to_datetime(c.index); ii = idx.close.copy(); ii.index = pd.to_datetime(ii.index)
        j = pd.concat([c.pct_change(), ii.pct_change()], axis=1, join="inner").dropna(); dev = (j.iloc[:, 0] - j.iloc[:, 1]).abs()
        return [d.date() for d in dev[dev > 0.0035].index if d.date() >= START]
    last_session = max(d["date"] for d in days["NQ"] if d["complete"])
    nxt = next_session(last_session)
    run_ts = datetime.now(timezone.utc).astimezone(pd.Timestamp.now(tz=NY).tz)
    ndx, spx, spy, ief = [x[[finished(d) for d in x.index]] for x in (daily("^NDX"), daily("^GSPC"), daily("SPY", 3), daily("IEF", 3))]
    if ndx.index[-1] < last_session:
        warn.append(f"Clôture ^NDX du {last_session:%d/%m} absente chez Yahoo : signal RSI 2 NQ calculé sur la veille.")

    # ---- compte Topstep (intraday)
    cands = s1_noise(days["NQ"], SPEC["NQ"]) + s2_monday(days["NQ"], SPEC["NQ"])
    dnq_all = [d for d in days["NQ"] if not d.get("en_cours")]
    evaluable = {dnq_all[k]["date"] for k in range(14, len(dnq_all)) if all(dnq_all[k - m]["complete"] for m in range(0, 15))}
    if ETAT is not None and (ETAT / "candidats_intraday.csv").exists():
        oc = pd.read_csv(ETAT / "candidats_intraday.csv")
        if len(oc):
            oc["date"] = pd.to_datetime(oc.date).dt.date
            cands += [r for r in oc.to_dict("records") if r["date"] not in evaluable]
    pd.DataFrame(cands, columns=["date", "heure", "i", "strat", "marche", "sens", "n", "entree", "stop", "sortie", "heure_sortie", "j_out", "raison",
                                 "risque_usd", "mae_usd", "pnl_usd"]).to_csv(OUT / "etat" / "candidats_intraday.csv", index=False)
    taken, refused, eod, bal, status = topstep_ledger(cands)

    # ---- compte perso (multi-jours)
    t_nq, p_nq, st_nq = s3_rsi2(ndx, opens["NQ"], "NQ")
    t_es, p_es, st_es = s3_rsi2(spx, opens["ES"], "ES")
    for mk, idx in (("NQ", ndx), ("ES", spx)):
        rr = roll_check(mk, idx)
        if rr:
            warn.append(f"{mk} : écart future/indice > 0,35 % le {', '.join(f'{d:%d/%m}' for d in rr)} — probable changement de contrat (roll) chez Yahoo ; "
                        f"le P&L papier des positions tenues ce jour-là peut être faussé.")
    t_me, p_me, me_info = s4_month_end(spy, ief, closes)
    closed_perso, open_perso = [], []
    for tr, mk in ((t_nq, "NQ"), (t_es, "ES")):
        for t in tr:
            closed_perso.append(dict(t, pnl_usd=(t["sortie"] - t["entree"]) * SPEC[mk]["pv"] - SPEC[mk]["comm"]))
    closed_perso += t_me
    for p, mk in ((p_nq, "NQ"), (p_es, "ES")):
        if p is not None:
            last_c = closes[mk][max(closes[mk])]
            if p["date"] > max(closes[mk]):
                last_c = np.nan
            p = dict(p, cours=last_c, latent_usd=(last_c - p["entree"]) * SPEC[mk]["pv"] if not np.isnan(p["entree"]) else np.nan)
            open_perso.append(p)
    if p_me is not None:
        le, lz = closes["ES"][max(closes["ES"])], closes["ZN"][max(closes["ZN"])]
        s = p_me["sens"]; lat = s * (le - p_me["entree_es"]) * SPEC["ES"]["pv"] - s * p_me["n_zn"] * (lz - p_me["entree_zn"]) * SPEC["ZN"]["pv"]
        open_perso.append(dict(p_me, latent_usd=lat))
    perso_real = sum(t["pnl_usd"] for t in closed_perso)
    perso_lat = sum(p.get("latent_usd", 0) or 0 for p in open_perso if not np.isnan(p.get("latent_usd", 0) or 0))
    perso_eq = PERSO["capital"] + perso_real + perso_lat

    # risque ouvert du compte perso (1 R = ATR20 journalier du micro)
    def atr20(mk):
        dd = [d for d in days[mk] if d["complete"]][-20:]
        return np.mean([d["h"].max() - d["l"].min() for d in dd]) * SPEC[mk]["pv"]
    risk_open = sum(atr20("NQ" if p["marche"] == "MNQ" else "ES") for p in open_perso if p["strat"].startswith("S3"))
    if p_me is not None:
        risk_open += atr20("ES") + p_me["n_zn"] * atr20("ZN")

    # ---- propositions pour la prochaine séance
    props = []
    k = len(days["NQ"])
    dnq = [d for d in days["NQ"] if not d.get("en_cours")]
    if len(dnq) >= 14 and all(d["complete"] for d in dnq[-14:]):
        sig = np.mean([np.abs(dnq[-m]["c"] / dnq[-m]["o"][0] - 1) for m in range(1, 15)], axis=0)
        pc = dnq[-1]["close"]
        lv = " ; ".join(f"{hhmm(t + 1)} ±{fmt(1.5 * sig[t] * 100)} % (stop {sig[t] * pc:.0f} pts, {int(TOP['risque_max_trade'] // (sig[t] * pc * 2))} MNQ)"
                       for t in (29, 59, 89, 149, 209, 269, 329))
        props.append(dict(compte="Topstep 50K", strategie="S1 · Noise area V4 (NQ)", marche="MNQ", action="Conditionnel",
                          detail=f"Toutes les 30 min dès 10:00 ET (16:00 Paris) : ACHAT si la clôture de la bougie 1 min dépasse max(ouverture, {fmt(pc)}) × (1 + x) ; "
                                 f"VENTE si elle passe sous min(ouverture, {fmt(pc)}) × (1 − x). x et stop par heure : {lv}. "
                                 f"Sortie si le prix repasse la bande ou le VWAP à un contrôle, sinon à 15:58. 3 entrées max."
                                 + (" FOMC : à plat à 13:55." if nxt in FOMC else ""),
                          risque=f"≤ {TOP['risque_max_trade']:.0f} $ par trade", statut=STATUTS["S1 · Noise area V4 (NQ)"]))
    if nxt.weekday() == 0:
        atr = np.mean([d["h"].max() - d["l"].min() for d in dnq[-14:]])
        if 0.5 * atr * 2 <= TOP["risque_max_lundi"]:
          props.append(dict(compte="Topstep 50K", strategie="S2 · Lundi acheteur (NQ)", marche="MNQ", action="ACHAT 1 MNQ",
                          detail=f"Au marché à 09:30 ET (15:30 Paris). Stop = entrée − {0.5 * atr:.0f} pts. Vente au marché à 15:58 ET.",
                          risque=f"{0.5 * atr * 2:.0f} $", statut=STATUTS["S2 · Lundi acheteur (NQ)"]))
        else:
          props.append(dict(compte="Topstep 50K", strategie="S2 · Lundi acheteur (NQ)", marche="MNQ", action="Rien",
                            detail=f"Stop nécessaire {0.5 * atr * 2:.0f} $ > {TOP['risque_max_lundi']:.0f} $ : trade sauté.", risque="", statut=STATUTS["S2 · Lundi acheteur (NQ)"]))
    for mk, p, stt, idxname in (("NQ", p_nq, st_nq, "Nasdaq-100"), ("ES", p_es, st_es, "S&P 500")):
        mic = SPEC[mk]["micro"]
        if p is None:
            if stt["close"] > stt["sma200"] and stt["rsi"] < 10:
                props.append(dict(compte="Perso", strategie="S3 · RSI 2 achat (NQ + ES)", marche=mic, action=f"ACHAT 1 {mic}",
                                  detail=f"Au marché à l'ouverture 09:30 ET. Signal : {idxname} RSI2 {stt['rsi']:.1f} < 10 et clôture au-dessus de la MM200. Pas de stop (règle d'origine).",
                                  risque=f"1 R ≈ {atr20(mk):.0f} $", statut=STATUTS["S3 · RSI 2 achat (NQ + ES)"]))
            else:
                props.append(dict(compte="Perso", strategie="S3 · RSI 2 achat (NQ + ES)", marche=mic, action="Rien",
                                  detail=f"{idxname} : RSI2 {stt['rsi']:.1f} (signal si < 10), clôture {'au-dessus' if stt['close'] > stt['sma200'] else 'SOUS'} la MM200.",
                                  risque="", statut=STATUTS["S3 · RSI 2 achat (NQ + ES)"]))
        else:
            if np.isnan(p["entree"]) and p["date"] == nxt:
                act, det = f"ACHAT 1 {mic}", f"Au marché à l'ouverture 09:30 ET. {p['info']}. Pas de stop (règle d'origine)."
            elif p.get("sortie_prevue") == nxt:
                act, det = f"VENTE 1 {mic} (sortie)", f"Au marché à l'ouverture 09:30 ET ({p['raison']})."
            else:
                act, det = "Conserver", f"Sortie dès qu'une clôture du {idxname} passe au-dessus de la MM5 ({fmt(stt['sma5'])}), ou au plus tard après 10 séances (séance n°{p['seances']})."
            props.append(dict(compte="Perso", strategie="S3 · RSI 2 achat (NQ + ES)", marche=mic, action=act, detail=det,
                              risque=f"1 R ≈ {atr20(mk):.0f} $", statut=STATUTS["S3 · RSI 2 achat (NQ + ES)"]))
    if p_me is not None:
        props.append(dict(compte="Perso", strategie="S4 · Fin de mois actions/oblig.", marche=p_me["marche"],
                          action="Conserver" if p_me["sortie_prevue"] != nxt else "CLÔTURER à 15:59 ET",
                          detail=f"Sortie à la clôture du {p_me['sortie_prevue']:%d/%m}.", risque="", statut=STATUTS["S4 · Fin de mois actions/oblig."]))
    elif me_info and me_info.get("N_moins_5") == nxt:
        props.append(dict(compte="Perso", strategie="S4 · Fin de mois actions/oblig.", marche="MES / ZN", action="Conditionnel à 15:55 ET",
                          detail="Aujourd'hui = 5 séances avant la fin du mois. À 15:55 ET : si les actions ont surperformé les obligations depuis le début du mois "
                                 "(poids actions d'un 60/40 > 0,6) → vente 1 MES / achat ZN ; sinon achat 1 MES / vente ZN. Sortie à la clôture du dernier jour du mois.",
                          risque="", statut=STATUTS["S4 · Fin de mois actions/oblig."]))
    else:
        props.append(dict(compte="Perso", strategie="S4 · Fin de mois actions/oblig.", marche="MES / ZN", action="Rien",
                          detail=f"Prochain signal à la clôture du {me_info.get('N_moins_5'):%d/%m} (5 séances avant la fin du mois)." if me_info else "",
                          risque="", statut=STATUTS["S4 · Fin de mois actions/oblig."]))
    # contrôle global du compte perso
    if risk_open > PERSO["risque_ouvert_max_pct"] * PERSO["capital"]:
        warn.append(f"Compte perso : risque ouvert {risk_open:,.0f} $ > 6 % du capital. Aucune nouvelle entrée tant que ce n'est pas résorbé.")
        for p in props:
            if p["compte"] == "Perso" and p["action"].startswith("ACHAT"):
                p["action"] = "BLOQUÉ (risque global)"
    if status != "En cours":
        for p in props:
            if p["compte"] == "Topstep 50K":
                p["action"] = "BLOQUÉ (compte clôturé)"

    # ---- sorties
    J = []
    for t in taken:
        J.append(dict(compte="Topstep 50K", strategie=t["strat"], marche=t["marche"], date_entree=f"{t['date']:%d/%m/%Y} {t['heure']}",
                      sens="Achat" if t["sens"] > 0 else "Vente", contrats=t["n"], entree=round(t["entree"], 2), stop=round(t["stop"], 2),
                      date_sortie=f"{t['date']:%d/%m/%Y} {t['heure_sortie']}", sortie=round(t["sortie"], 2), raison=t["raison"],
                      pnl_usd=round(t["pnl_usd"], 2), r=round(t["pnl_usd"] / t["risque_usd"], 2)))
    for t in closed_perso:
        if t["strat"].startswith("S3"):
            J.append(dict(compte="Perso", strategie=t["strat"], marche=t["marche"], date_entree=f"{t['date']:%d/%m/%Y} 09:30", sens="Achat",
                          contrats=1, entree=round(t["entree"], 2), stop="", date_sortie=f"{t['date_sortie']:%d/%m/%Y} 09:30",
                          sortie=round(t["sortie"], 2), raison=t["raison"], pnl_usd=round(t["pnl_usd"], 2), r=""))
        else:
            J.append(dict(compte="Perso", strategie=t["strat"], marche=t["marche"], date_entree=f"{t['date']:%d/%m/%Y} 15:59",
                          sens="Achat actions" if t["sens"] > 0 else "Vente actions", contrats=f"1 / {t['n_zn']}",
                          entree=f"{t['entree_es']:.2f} / {t['entree_zn']:.4f}", stop="", date_sortie=f"{t['date_sortie']:%d/%m/%Y} 15:59",
                          sortie=f"{t['sortie_es']:.2f} / {t['sortie_zn']:.4f}", raison="fin de mois", pnl_usd=round(t["pnl_usd"], 2), r=""))
    J = pd.DataFrame(J, columns=["compte", "strategie", "marche", "date_entree", "sens", "contrats", "entree", "stop", "date_sortie",
                                 "sortie", "raison", "pnl_usd", "r"])
    J.to_csv(OUT / "journal.csv", index=False)
    pd.DataFrame([dict(compte="Topstep 50K", strategie=t["strat"], date=f"{t['date']:%d/%m/%Y} {t['heure']}", sens=t["sens"],
                       pnl_si_pris=round(t["pnl_usd"], 2), refus=t["refus"]) for t in refused],
                 columns=["compte", "strategie", "date", "sens", "pnl_si_pris", "refus"]).to_csv(OUT / "refus.csv", index=False)
    pd.DataFrame(eod, columns=["date", "pnl_jour", "solde", "plancher_mll", "objectif", "meilleur_jour", "trades", "statut"]).to_csv(OUT / "compte_topstep.csv", index=False)
    O = []
    for p in open_perso:
        if p["strat"].startswith("S3"):
            O.append(dict(compte="Perso", strategie=p["strat"], marche=p["marche"], depuis=f"{p['date']:%d/%m/%Y}", sens="Achat", contrats=1,
                          entree=round(p["entree"], 2) if not np.isnan(p["entree"]) else "en attente d'ouverture",
                          cours=round(p.get("cours", np.nan), 2), latent_usd=round(p.get("latent_usd", np.nan), 2) if not np.isnan(p.get("latent_usd", np.nan)) else "",
                          sortie_prevue=f"{p['sortie_prevue']:%d/%m/%Y}" if p.get("sortie_prevue") else "MM5 ou 10 séances", info=p["info"]))
        else:
            O.append(dict(compte="Perso", strategie=p["strat"], marche=p["marche"], depuis=f"{p['date']:%d/%m/%Y}", sens="Achat actions" if p["sens"] > 0 else "Vente actions",
                          contrats=f"1 / {p['n_zn']}", entree=f"{p['entree_es']:.2f} / {p['entree_zn']:.4f}", cours="", latent_usd=round(p["latent_usd"], 2),
                          sortie_prevue=f"{p['sortie_prevue']:%d/%m/%Y}", info=p["info"]))
    pd.DataFrame(O, columns=["compte", "strategie", "marche", "depuis", "sens", "contrats", "entree", "cours", "latent_usd", "sortie_prevue", "info"]).to_csv(OUT / "positions_ouvertes.csv", index=False)
    P = pd.DataFrame(props, columns=["compte", "strategie", "marche", "action", "detail", "risque", "statut"]); P.insert(0, "seance", f"{nxt:%d/%m/%Y}")
    P.to_csv(OUT / "propositions.csv", index=False)
    top_pnl = bal - TOP["capital"]; target = eod[-1]["objectif"] if eod else TOP["objectif"]
    floor = eod[-1]["plancher_mll"] if eod else TOP["capital"] - TOP["mll"]
    D = [["Mise à jour", f"{run_ts:%d/%m/%Y %H:%M} ET — dernière séance : {last_session:%d/%m/%Y} — prochaine : {nxt:%d/%m/%Y}"],
         ["Mode", "PAPIER (aucun ordre réel). Suivi depuis le 02/11/2026."],
         ["", ""],
         ["COMPTE TOPSTEP 50K (papier)", status],
         ["Solde", f"{fmt(bal)} $"], ["P&L total", f"{"" if top_pnl >= 0 else "−"}{fmt(abs(top_pnl))} $"], ["Objectif (consistance 55 % incluse)", f"{fmt(target)} $"],
         ["Reste à faire", f"{fmt(max(0, target - top_pnl))} $"], ["Plancher MLL (perte max)", f"{fmt(floor)} $"],
         ["Marge avant le plancher", f"{fmt(bal - floor)} $"], ["Trades pris / refusés", f"{len(taken)} / {len(refused)}"],
         ["", ""],
         ["COMPTE PERSO (papier, 50 000 $)", ""],
         ["Valeur (réalisé + latent)", f"{fmt(perso_eq)} $"], ["P&L réalisé", f"{"" if perso_real >= 0 else "−"}{fmt(abs(perso_real))} $"], ["P&L latent", f"{"" if perso_lat >= 0 else "−"}{fmt(abs(perso_lat))} $"],
         ["Positions ouvertes", str(len(open_perso))], ["Risque ouvert (1 ATR20)", f"{fmt(risk_open, 0)} $ ({fmt(100 * risk_open / PERSO['capital'], 1)} % ; max 6 %)"],
         ["", ""], ["STATUT DES STRATÉGIES", ""]] + [[k, v] for k, v in STATUTS.items()] + \
        [["", ""], ["Rappel", "Aucune stratégie n'a d'edge prouvé. Il faut 50+ trades par stratégie avant de conclure. Ne pas passer en réel sur la base de 2–3 semaines."]] + \
        [["Alerte", w] for w in warn]
    pd.DataFrame(D, columns=["indicateur", "valeur"]).to_csv(OUT / "tableau_de_bord.csv", index=False)
    # ---- charge utile pour Google Sheets : {onglet: tableau de valeurs}
    REGLES = [["Stratégie", "Compte", "Règle figée", "Statut"],
              ["S1 · Noise area V4 (NQ)", "Topstep 50K", "Bandes = max/min(ouverture, clôture veille) × (1 ± 1,5 σ(t)), σ(t) = moyenne 14 séances de |prix/ouverture − 1|. "
               "Contrôle toutes les 30 min dès 10:00 ET. Stop 1 σ. Sortie si retour sous la bande/VWAP à un contrôle, sinon 15:58. 3 entrées max.", STATUTS["S1 · Noise area V4 (NQ)"]],
              ["S2 · Lundi acheteur (NQ)", "Topstep 50K", "Lundi : achat 1 MNQ à 09:30, stop 0,5 × ATR14 (sauté si > 600 $), vente 15:58.", STATUTS["S2 · Lundi acheteur (NQ)"]],
              ["S3 · RSI 2 achat (NQ + ES)", "Perso", "Clôture de l'indice > MM200 et RSI2 < 10 → achat 1 micro à l'ouverture suivante. Sortie à l'ouverture après une clôture > MM5, ou après 10 séances. Pas de stop.", STATUTS["S3 · RSI 2 achat (NQ + ES)"]],
              ["S4 · Fin de mois actions/oblig.", "Perso", "Clôture de N−5 : poids actions d'un 60/40 (SPY/IEF depuis le début du mois) > 0,6 → vente MES / achat ZN, sinon l'inverse. Sortie à la clôture de N.", STATUTS["S4 · Fin de mois actions/oblig."]],
              ["", "", "", ""],
              ["Règles du compte", "Topstep 50K", "Perte max 2 000 $ en temps réel (plancher qui suit le solde de fin de journée, bloqué à 50 000 $) ; objectif 3 000 $ ; meilleur jour ≤ 55 % de l'objectif ; "
               "2 trades max par jour ; perte journalière max 1 000 $ ; ≤ 250 $ de risque par trade (600 $ pour le lundi) ; risque ouvert total ≤ 850 $.", ""],
              ["Règles du compte", "Perso", "Capital papier 50 000 $ ; 1 micro par signal (ZN : contrat standard) ; risque ouvert total ≤ 6 % du capital (1 R = ATR20 journalier).", ""]]
    NOMS = dict(seance="Séance", compte="Compte", strategie="Stratégie", marche="Marché", action="Action", detail="Détail", risque="Risque",
                statut="Statut", depuis="Depuis", sens="Sens", contrats="Contrats", entree="Entrée", cours="Cours", latent_usd="Latent ($)",
                sortie_prevue="Sortie prévue", info="Info", date_entree="Entrée le", stop="Stop", date_sortie="Sortie le", sortie="Sortie",
                raison="Raison", pnl_usd="P&L net ($)", r="R", date="Date", pnl_jour="P&L du jour ($)", solde="Solde ($)",
                plancher_mll="Plancher MLL ($)", objectif="Objectif ($)", meilleur_jour="Meilleur jour ($)", trades="Trades",
                pnl_si_pris="P&L si pris ($)", refus="Motif du refus")
    def tab(df):
        return [[NOMS.get(c, c) for c in df.columns]] + [["" if (isinstance(x, float) and np.isnan(x)) else (x if isinstance(x, (int, float, str)) else str(x)) for x in r] for r in df.itertuples(index=False)]
    # onglets préfixés « Agent · » : la feuille contient déjà Journal / Stats / Paramètres (journal manuel de Saber), à ne jamais toucher
    payload = {"Agent · Tableau de bord": [["Indicateur", "Valeur"]] + D, "Agent · Propositions": tab(P),
               "Agent · Positions": tab(pd.read_csv(OUT / "positions_ouvertes.csv").fillna("")), "Agent · Journal": tab(J),
               "Agent · Compte Topstep": tab(pd.read_csv(OUT / "compte_topstep.csv")), "Agent · Refus": tab(pd.read_csv(OUT / "refus.csv")),
               "Agent · Stratégies": REGLES}
    for rows in payload.values():
        for r in rows:
            for i, x in enumerate(r):
                if isinstance(x, str) and x[:1] in "+=":
                    r[i] = "\u2009" + x
    (OUT / "sheet_payload.json").write_text(json.dumps(payload, ensure_ascii=False, default=str))
    print("\n".join(f"{a} : {b}" for a, b in D))
    print("\nPROPOSITIONS", nxt); print(P.to_string(index=False))
    print("\nJOURNAL"); print(J.to_string(index=False))


if __name__ == "__main__":
    main()
