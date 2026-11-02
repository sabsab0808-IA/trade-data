"""Simulations historiques glissantes des 4 stratégies de l'agent (doc 19).
Question posée : si les prochaines semaines ressemblent à une période tirée de 2010–2026, que donne l'agent ?
- Compte Topstep : S1 + S2 rejouées minute par minute (NQ Databento 2010–2026), avec les règles exactes du compte (fonction topstep_ledger de l'agent),
  sur TOUTES les fenêtres de 60 séances (une par jour de départ) -> taux de réussite / échec, contre une référence « zéro edge ».
- Compte perso : S3 (trades de l'étude 7) et S4 (trades de l'étude 9), ramenés à la taille d'aujourd'hui, sur toutes les fenêtres de 15 séances.
Usage : python3 -I simulations.py <agent.py> <nq_full.pkl> <fomc.csv> <trades_study7.csv> <trades_study9.csv> <sortie>
"""
import sys, importlib.util
from datetime import date
from pathlib import Path
import numpy as np, pandas as pd

AG, NQ, FOMC_CSV, T7, T9, OUT = sys.argv[1:7]; OUT = Path(OUT); OUT.mkdir(parents=True, exist_ok=True)
sys.argv = ["agent", str(Path(AG).parents[1] / "config"), str(OUT / "_agent_out")]
spec = importlib.util.spec_from_file_location("agent", AG); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
A.START = date(2010, 6, 1)
A.FOMC = {pd.Timestamp(d).date(): int(t[:2]) * 60 + int(t[3:]) for d, t in pd.read_csv(FOMC_CSV)[["date", "time_et"]].values}
RISK_LUNDI_AUJ = 491.0   # risque du lundi aux prix de novembre 2026 (0,5 × ATR14 × 2 $)
ATR_USD = {"MNQ": 872.0, "MES": 331.0}  # 1 R du compte perso aux prix de novembre 2026 (ATR20 × valeur du point)
NOTIONNEL_MES = 7650 * 5.0

# ------------------------------------------------------------------ candidats intraday 2010-2026
df = pd.read_pickle(NQ)
days = A.sessions(df)
ids = df.groupby(df.ts.dt.date).instrument_id.agg(lambda s: set(s))
for i in range(1, len(days)):  # jours de roll exclus, comme dans les études
    if len(ids[days[i]["date"]] | ids[days[i - 1]["date"]]) > 1:
        days[i]["complete"] = False
s1 = A.s1_noise(days, A.SPEC["NQ"])
A.TOP["risque_max_lundi"] = 1e9  # en 2010 le NQ valait 2 000 : on garde tous les lundis puis on remet à l'échelle d'aujourd'hui
s2 = A.s2_monday(days, A.SPEC["NQ"])
for t in s2:  # remise à l'échelle du risque actuel (1 MNQ, stop 0,5 ATR ≈ 491 $)
    k = RISK_LUNDI_AUJ / t["risque_usd"]
    t["pnl_usd"] *= k; t["mae_usd"] *= k; t["risque_usd"] = RISK_LUNDI_AUJ
C = pd.DataFrame(s1 + s2)
C["R"] = C.pnl_usd / C.risque_usd
C.to_csv(OUT / "candidats_topstep_2010_2026.csv", index=False)
sess = [d["date"] for d in days if d["complete"]]
print("S1", len(s1), "trades, R moyen", round(C[C.strat.str.startswith("S1")].R.mean(), 3), "| S2", len(s2), "trades, R moyen", round(C[C.strat.str.startswith("S2")].R.mean(), 3))

# référence zéro edge : même profil, espérance ramenée à -coûts (on retire la moyenne brute de chaque stratégie)
Z = C.copy()
for s in Z.strat.unique():
    m = Z.strat == s
    cost = (A.SPEC["NQ"]["comm"] + 2 * A.SPEC["NQ"]["tick"] * A.SPEC["NQ"]["pv"]) * Z.loc[m, "n"]
    gross = Z.loc[m, "pnl_usd"] + cost
    Z.loc[m, "pnl_usd"] = gross - gross.mean() - cost


def windows(cands, n_sess, step=1):
    by = {}
    for r in cands.to_dict("records"):
        by.setdefault(r["date"], []).append(r)
    out = []
    for i in range(0, len(sess) - n_sess, step):
        w = [t for d in sess[i:i + n_sess] for t in by.get(d, [])]
        taken, refused, eod, bal, status = A.topstep_ledger(w)
        jours = len(eod)
        out.append(dict(debut=sess[i], statut=status, pnl=bal - A.TOP["capital"], trades=len(taken),
                        jours_reussite=next((k + 1 for k, e in enumerate(eod) if e["statut"].startswith("RÉUSSI")), np.nan)))
    return pd.DataFrame(out)


res = {}
for lab, cc in (("Agent (S1 + S2)", C), ("S1 seule", C[C.strat.str.startswith("S1")]), ("S2 seule", C[C.strat.str.startswith("S2")]),
                ("Référence zéro edge", Z)):
    w60 = windows(cc, 60, step=2); w15 = windows(cc, 15, step=1)
    res[lab] = (w60, w15)
    print(lab, "réussite 60 s.", round(100 * w60.statut.str.startswith("RÉUSSI").mean(), 1), "% | échec", round(100 * w60.statut.str.startswith("ÉCHOUÉ").mean(), 1), "%")

rows = []
for lab, (w60, w15) in res.items():
    for per, a, b in (("2010-2026", "2010-01-01", "2027-01-01"), ("2021-2026", "2021-01-01", "2027-01-01"), ("2025-2026", "2025-01-01", "2027-01-01")):
        q = w60[(pd.to_datetime(w60.debut) >= a) & (pd.to_datetime(w60.debut) < b)]
        p = w15[(pd.to_datetime(w15.debut) >= a) & (pd.to_datetime(w15.debut) < b)]
        rows.append(dict(compte="Topstep 50K", strategie=lab, periode=per, fenetres_60=len(q),
                         reussite_60_pct=100 * q.statut.str.startswith("RÉUSSI").mean(), echec_60_pct=100 * q.statut.str.startswith("ÉCHOUÉ").mean(),
                         en_cours_60_pct=100 * (q.statut == "En cours").mean(), jours_median_reussite=q.jours_reussite.median(),
                         pnl15_p5=p.pnl.quantile(.05), pnl15_p25=p.pnl.quantile(.25), pnl15_med=p.pnl.median(), pnl15_p75=p.pnl.quantile(.75),
                         pnl15_p95=p.pnl.quantile(.95), pnl15_perte_pct=100 * (p.pnl < 0).mean(), trades15_moy=p.trades.mean()))
TOPS = pd.DataFrame(rows)

# ------------------------------------------------------------------ compte perso : S3 et S4 sur fenêtres de 15 séances
t7 = pd.read_csv(T7, parse_dates=["date_in", "date_out"])
s3 = t7[(t7.strat == "H1_RSI2_swing") & (t7.dir > 0) & (t7.market.isin(["NQ", "ES"]))].copy()
s3["micro"] = s3.market.map({"NQ": "MNQ", "ES": "MES"}); s3["pnl_usd"] = s3.r_net * s3.micro.map(ATR_USD); s3["sortie"] = s3.date_out
t9 = pd.read_csv(T9, parse_dates=["date"])
s4 = t9.assign(pnl_usd=t9.pnl_net * NOTIONNEL_MES, sortie=t9.date)
cal = pd.DatetimeIndex(sorted(set(pd.to_datetime(sess))))
prow = []
for lab, tt in (("S3 · RSI 2 (NQ + ES)", s3), ("S4 · Fin de mois", s4), ("Compte perso (S3 + S4)", pd.concat([s3[["sortie", "pnl_usd"]], s4[["sortie", "pnl_usd"]]]))):
    ex = tt.groupby(tt.sortie.dt.normalize()).pnl_usd.sum().reindex(cal, fill_value=0.0)
    nb = tt.groupby(tt.sortie.dt.normalize()).size().reindex(cal, fill_value=0)
    w = ex.rolling(15).sum().dropna(); n = nb.rolling(15).sum().dropna()
    for per, a in (("2010-2026", "2010"), ("2021-2026", "2021"), ("2025-2026", "2025")):
        q = w[w.index >= a]; m = n[n.index >= a]
        prow.append(dict(compte="Perso", strategie=lab, periode=per, fenetres_15=len(q), pnl15_p5=q.quantile(.05), pnl15_p25=q.quantile(.25),
                         pnl15_med=q.median(), pnl15_p75=q.quantile(.75), pnl15_p95=q.quantile(.95), pnl15_perte_pct=100 * (q < 0).mean(),
                         pnl15_zero_pct=100 * (q == 0).mean(), trades15_moy=m.mean(), pnl_an_moy=tt[tt.sortie >= a].pnl_usd.sum() / max(1, (cal[-1] - pd.Timestamp(a)).days / 365.25)))
PERS = pd.DataFrame(prow)
TOPS.to_csv(OUT / "simulations_topstep.csv", index=False); PERS.to_csv(OUT / "simulations_perso.csv", index=False)
pd.set_option("display.width", 250); print(TOPS.round(1).to_string(index=False)); print(PERS.round(1).to_string(index=False))

# ------------------------------------------------------------------ backtests par année (pour l'onglet Backtests), en $ aux tailles d'aujourd'hui
C["annee"] = pd.to_datetime(C.date).dt.year
Y1 = C.groupby(["annee", "strat"]).pnl_usd.sum().unstack().round(0)
s3["annee"] = s3.sortie.dt.year; s4["annee"] = s4.sortie.dt.year
Y = pd.concat([Y1, s3.groupby("annee").pnl_usd.sum().round(0).rename("S3 · RSI 2 achat (NQ + ES)"),
               s4.groupby("annee").pnl_usd.sum().round(0).rename("S4 · Fin de mois actions/oblig.")], axis=1).fillna(0)
Y.to_csv(OUT / "backtests_par_annee.csv"); print(Y.to_string())
B = []
for lab, x, unit in (("S1 · Noise area V4 (NQ)", C[C.strat.str.startswith("S1")], "R"), ("S2 · Lundi acheteur (NQ)", C[C.strat.str.startswith("S2")], "R"),
                     ("S3 · RSI 2 achat (NQ + ES)", s3.assign(R=s3.r_net), "R"), ("S4 · Fin de mois actions/oblig.", s4.assign(R=s4.pnl_net * 100), "%")):
    d = pd.to_datetime(x["date"]) if "date" in x.columns else x.sortie
    for per, a, b in (("2010-2020", "2010", "2020-12-31"), ("2021-2026", "2021", "2026-12-31")):
        q = x[(d >= a) & (d <= b)]
        B.append(dict(strategie=lab, periode=per, trades=len(q), gagnants_pct=100 * (q.pnl_usd > 0).mean(), moyenne=q.R.mean(), unite=unit,
                      pnl_moyen_usd=q.pnl_usd.mean(), pnl_total_usd=q.pnl_usd.sum(), pire_usd=q.pnl_usd.min(), meilleur_usd=q.pnl_usd.max()))
B = pd.DataFrame(B); B.to_csv(OUT / "backtests_resume.csv", index=False); print(B.round(2).to_string(index=False))
