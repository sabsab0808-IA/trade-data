"""Moteur de backtest 1 minute — modèle « Sweep de liquidité + FVG M1 » sur MNQ.

Toutes les heures sont en heure de New York (ET).
Principes anti-triche :
  * une décision prise à la clôture de la bougie i n'agit qu'à partir de la bougie i+1 ;
  * si une bougie touche le stop ET la cible, on compte une PERTE ;
  * sur la bougie de remplissage, seul le stop est vérifié (la cible attend la bougie suivante) ;
  * coûts inclus : commission par contrat + 1 tick de glissement sur les sorties au marché (stop, fin de journée).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import time

import numpy as np
import pandas as pd

TICK = 0.25
POINT_VALUE = 2.0  # MNQ : 2 $ par point


@dataclass
class Params:
    name: str = "base"
    # --- liquidité utilisée pour les sweeps
    use_pd_levels: bool = True        # plus haut / plus bas de la séance régulière précédente
    use_on_levels: bool = True        # plus haut / plus bas de l'overnight (16:00 veille -> 09:29)
    require_sweep: bool = True        # False = placebo : n'importe quel FVG, stop sur le swing des 10 dernières bougies
    # --- fenêtres horaires (ET)
    entry_start: time = time(9, 30)
    entry_end: time = time(15, 0)     # plus de nouvel ordre après
    flat_time: time = time(15, 55)    # clôture forcée
    # --- FVG / ordre
    sweep_lookahead: int = 30         # bougies max entre le sweep et le FVG
    min_gap_pts: float = 1.0          # taille minimale du FVG
    require_displacement: bool = True # bougie du milieu dans le sens du trade
    entry_mode: str = "proximal"      # "proximal" (1er contact) ou "ce" (milieu du FVG)
    stop_buffer_pts: float = 1.0      # au-delà de l'extrême du sweep
    min_risk_bps: float = 3.0         # risque min = 0,03 % du prix (~5 pts à 16 000)
    max_risk_bps: float = 25.0        # risque max = 0,25 % du prix (~40 pts à 16 000)
    order_expiry: int = 30            # bougies avant annulation de l'ordre limite
    r_target: float = 2.0
    fill_through_ticks: int = 0       # 1 = le prix doit dépasser l'ordre d'1 tick pour être rempli (plus réaliste)
    partial_at_r: float = 0.0         # >0 : moitié sortie à ce multiple de R, stop du reste remonté à l'entrée
    # --- filtres de contexte (étude n°3)
    pd_filter: bool = False           # short seulement au-dessus du milieu du range overnight, long en dessous
    bias_filter: bool = False         # long seulement si la veille a clôturé dans sa moitié haute (short sinon)
    # --- gestion du risque journalière
    max_trades_day: int = 2
    max_losses_day: int = 2
    # --- coûts
    commission_per_contract: float = 1.00  # $ aller-retour par MNQ (approx. Topstep/Tradovate)
    slippage_ticks: int = 1                # sur sorties stop et fin de journée
    risk_dollars: float = 250.0            # pour la taille de position (sert au calcul des coûts en R)
    # --- news
    news_blackout_min: int = 5


def _tod(ts: pd.Series) -> np.ndarray:
    return (ts.dt.hour * 60 + ts.dt.minute).to_numpy()


def _hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _m(t: time) -> int:
    return t.hour * 60 + t.minute


def prepare_days(df: pd.DataFrame) -> list[dict]:
    """Découpe les données en journées : niveaux connus avant 09:30 + barres de la séance régulière."""
    df = df.copy()
    df["date"] = df.ts.dt.date
    df["tod"] = _tod(df.ts)
    rth = df[(df.tod >= 570) & (df.tod < 960)]
    dates = sorted(rth.date.unique())
    rth_groups = {d: g for d, g in rth.groupby("date")}
    ts_ns = df.ts.dt.as_unit("ns").astype("int64").to_numpy()
    highs, lows = df.high.to_numpy(), df.low.to_numpy()
    days = []
    for k in range(1, len(dates)):
        d, p = dates[k], dates[k - 1]
        g = rth_groups[d]
        if len(g) < 200:
            continue
        pg = rth_groups[p]
        # overnight : de 16:00 la veille (exclu) à 09:30 (exclu)
        start = pd.Timestamp(f"{p} 16:00", tz="America/New_York").value
        end = pd.Timestamp(f"{d} 09:30", tz="America/New_York").value
        a, b = np.searchsorted(ts_ns, start, "right"), np.searchsorted(ts_ns, end, "left")
        if b - a < 60:
            continue
        onh, onl = highs[a:b].max(), lows[a:b].min()
        pdh, pdl, pdc = pg.high.max(), pg.low.min(), pg.close.iloc[-1]
        days.append(
            dict(
                date=d,
                tod=g.tod.to_numpy(),
                o=g.open.to_numpy(), h=g.high.to_numpy(), l=g.low.to_numpy(), c=g.close.to_numpy(),
                pdh=pdh, pdl=pdl, pdc=pdc, onh=onh, onl=onl,
            )
        )
    return days


def load_news(path: str) -> dict:
    cal = pd.read_csv(path)
    out: dict = {}
    for _, r in cal.iterrows():
        hh, mm = map(int, r.time_et.split(":"))
        out.setdefault(pd.Timestamp(r.date).date(), []).append((hh * 60 + mm, r.event))
    return out


def _levels(day: dict, p: Params) -> list[list]:
    """[prix, côté, nom, actif]. côté +1 = liquidité au-dessus (buy-side) -> setup VENTE."""
    lv = []
    if p.use_on_levels:
        lv += [[day["onh"], +1, "ONH", True], [day["onl"], -1, "ONL", True]]
    if p.use_pd_levels:
        # un plus haut de la veille déjà dépassé pendant la nuit n'est plus de la liquidité intacte
        lv += [[day["pdh"], +1, "PDH", day["onh"] <= day["pdh"]],
               [day["pdl"], -1, "PDL", day["onl"] >= day["pdl"]]]
    return lv


def run_day(day: dict, p: Params, news_events: list) -> list[dict]:
    o, h, l, c, tod = day["o"], day["h"], day["l"], day["c"], day["tod"]
    n = len(c)
    e_start, e_end, flat = _m(p.entry_start), _m(p.entry_end), _m(p.flat_time)
    fomc = [t for t, ev in news_events if ev == "FOMC"]
    blackout = [(t - p.news_blackout_min, t + 3 * p.news_blackout_min) for t, _ in news_events]
    if fomc:  # on est à plat avant la Fed
        flat = min(flat, fomc[0] - p.news_blackout_min)

    def in_blackout(m):
        return any(a <= m <= b for a, b in blackout)

    levels = _levels(day, p)
    sweeps = []        # dicts: dir (-1 vente/+1 achat), s, ext, lvl
    pending = None     # dict ordre limite
    pos = None         # dict position
    trades = []
    n_trades = n_losses = 0
    day_stopped = False
    slip = p.slippage_ticks * TICK

    def close_pos(i, price, reason):
        nonlocal pos, n_losses, day_stopped
        pts = (price - pos["entry"]) * pos["dir"]
        if pos.get("half_done"):
            pts = 0.5 * p.partial_at_r * pos["risk"] + 0.5 * pts
        contracts = max(1, int(p.risk_dollars // (pos["risk"] * POINT_VALUE)))
        cost_pts = p.commission_per_contract / POINT_VALUE  # par contrat, en points
        r_gross = pts / pos["risk"]
        r_net = (pts - cost_pts) / pos["risk"]
        trades.append(dict(
            date=day["date"], dir="long" if pos["dir"] > 0 else "short", level=pos["lvl"],
            signal_time=str(pos["sig_t"]), entry_time=_hhmm(tod[pos["fill_i"]]),
            exit_time=_hhmm(tod[i]), entry=pos["entry"], stop=pos["stop"], target=pos["target"],
            exit=price, risk_pts=pos["risk"], contracts=contracts, reason=reason,
            r_gross=r_gross, r_net=r_net,
            mfe_r=pos["mfe"] / pos["risk"], mae_r=pos["mae"] / pos["risk"],
            pnl_usd=contracts * (pts * POINT_VALUE - p.commission_per_contract),
        ))
        if r_net < 0:
            n_losses += 1
        if n_losses >= p.max_losses_day or sum(t["r_net"] for t in trades) <= -2:
            day_stopped = True
        pos = None

    for i in range(n):
        m = tod[i]
        # 1) gestion de la position ouverte
        if pos is not None and i > pos["fill_i"]:
            d = pos["dir"]
            fav = (h[i] - pos["entry"]) if d > 0 else (pos["entry"] - l[i])
            adv = (pos["entry"] - l[i]) if d > 0 else (h[i] - pos["entry"])
            pos["mfe"] = max(pos["mfe"], fav)
            pos["mae"] = max(pos["mae"], adv)
            hit_stop = (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"])
            hit_tgt = (h[i] >= pos["target"]) if d > 0 else (l[i] <= pos["target"])
            if p.partial_at_r > 0 and not pos.get("half_done") and not hit_stop:
                lvl1 = pos["entry"] + d * p.partial_at_r * pos["risk"]
                if (h[i] >= lvl1) if d > 0 else (l[i] <= lvl1):
                    pos["half_done"] = True
                    pos["stop"] = pos["entry"]  # le reste passe à break-even
                    # hypothèse pessimiste : si la même bougie revient à l'entrée, le reste sort à BE
                    hit_stop = (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"])
            if hit_stop:  # prioritaire, même si la cible est touchée dans la même bougie
                gap_px = o[i] if ((d > 0 and o[i] < pos["stop"]) or (d < 0 and o[i] > pos["stop"])) else pos["stop"]
                close_pos(i, gap_px - d * slip, "stop")
            elif hit_tgt:
                close_pos(i, pos["target"], "target")
            elif m >= flat or i == n - 1:
                close_pos(i, c[i] - d * slip, "time")
        if pos is not None and (m >= flat or i == n - 1):
            close_pos(i, c[i] - pos["dir"] * slip, "time")

        # 2) ordre en attente
        if pending is not None and pos is None:
            d = pending["dir"]
            ft = p.fill_through_ticks * TICK
            touched = (l[i] <= pending["entry"] - ft) if d > 0 else (h[i] >= pending["entry"] + ft)
            beyond_tgt = (h[i] >= pending["target"]) if d > 0 else (l[i] <= pending["target"])
            if day_stopped or m > e_end or m >= flat or in_blackout(m):
                pending = None
            elif touched:
                pos = dict(pending, fill_i=i, mfe=0.0, mae=0.0)
                pending = None
                n_trades += 1
                # bougie de remplissage : seul le stop compte (hypothèse pessimiste)
                adv = (pos["entry"] - l[i]) if d > 0 else (h[i] - pos["entry"])
                pos["mae"] = max(0.0, adv)
                if (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"]):
                    close_pos(i, pos["stop"] - d * slip, "stop")
            elif beyond_tgt or i > pending["expiry"]:
                pending = None

        # 3) nouveaux sweeps (liquidité prise)
        if p.require_sweep:
            for lv in levels:
                if not lv[3]:
                    continue
                if lv[1] > 0 and h[i] > lv[0]:
                    sweeps.append(dict(dir=-1, s=i, ext=h[i], lvl=lv[2]))
                    lv[3] = False
                elif lv[1] < 0 and l[i] < lv[0]:
                    sweeps.append(dict(dir=+1, s=i, ext=l[i], lvl=lv[2]))
                    lv[3] = False
            for sw in sweeps:
                if i > sw["s"]:
                    sw["ext"] = max(sw["ext"], h[i]) if sw["dir"] < 0 else min(sw["ext"], l[i])
            sweeps = [sw for sw in sweeps if i - sw["s"] <= p.sweep_lookahead]

        # 4) détection d'un FVG à la clôture de la bougie i -> ordre limite actif dès i+1
        if i < 2 or pos is not None or pending is not None or day_stopped:
            continue
        if n_trades >= p.max_trades_day or m < e_start or m >= e_end or in_blackout(m):
            continue
        bear = (l[i - 2] - h[i]) >= p.min_gap_pts and (not p.require_displacement or c[i - 1] < o[i - 1])
        bull = (l[i] - h[i - 2]) >= p.min_gap_pts and (not p.require_displacement or c[i - 1] > o[i - 1])
        cand = None
        if p.require_sweep:
            for sw in sweeps:
                if i - 2 < sw["s"]:
                    continue
                if sw["dir"] < 0 and bear:
                    cand = (-1, sw["ext"], sw["lvl"], l[i - 2], h[i])
                elif sw["dir"] > 0 and bull:
                    cand = (+1, sw["ext"], sw["lvl"], h[i - 2], l[i])
                if cand:
                    sweeps.remove(sw)
                    break
        else:  # placebo : pas de sweep exigé, stop au-delà du swing des 10 dernières bougies
            lo = max(0, i - 10)
            if bear:
                cand = (-1, h[lo:i + 1].max(), "none", l[i - 2], h[i])
            elif bull:
                cand = (+1, l[lo:i + 1].min(), "none", h[i - 2], l[i])
        if cand is None:
            continue
        d, ext, lvl, far, near = cand
        entry = near if p.entry_mode == "proximal" else (near + far) / 2
        entry = round(entry / TICK) * TICK
        stop = ext + p.stop_buffer_pts if d < 0 else ext - p.stop_buffer_pts
        risk = (stop - entry) * (-d)
        if not (c[i] * p.min_risk_bps / 1e4 <= risk <= c[i] * p.max_risk_bps / 1e4):
            continue
        if p.pd_filter:
            mid = (day["onh"] + day["onl"]) / 2
            if (d < 0 and entry <= mid) or (d > 0 and entry >= mid):
                continue
        if p.bias_filter:
            bias = 1 if day["pdc"] > (day["pdh"] + day["pdl"]) / 2 else -1
            if d != bias:
                continue
        target = entry + d * p.r_target * risk
        pending = dict(dir=d, entry=entry, stop=stop, target=target, risk=risk, lvl=lvl,
                       sig_t=_hhmm(m), expiry=i + p.order_expiry)
    if pos is not None:  # sécurité (journées écourtées)
        close_pos(n - 1, c[n - 1] - pos["dir"] * slip, "time")
    return trades


def run_backtest(days: list[dict], p: Params, news: dict) -> pd.DataFrame:
    out = []
    for day in days:
        out += run_day(day, p, news.get(day["date"], []))
    t = pd.DataFrame(out)
    if len(t):
        t["date"] = pd.to_datetime(t["date"])
    return t


def stats(t: pd.DataFrame) -> dict:
    if len(t) == 0:
        return dict(trades=0)
    r = t.r_net.to_numpy()
    eq = np.cumsum(r)
    dd = (np.maximum.accumulate(np.concatenate([[0], eq])) - np.concatenate([[0], eq])).max()
    wins, losses = r[r > 0], r[r <= 0]
    streak = cur = 0
    for x in r:
        cur = cur + 1 if x <= 0 else 0
        streak = max(streak, cur)
    se = r.std(ddof=1) / np.sqrt(len(r)) if len(r) > 1 else np.nan
    return dict(
        trades=len(r),
        win_rate=round(len(wins) / len(r) * 100, 1),
        avg_win_r=round(wins.mean(), 2) if len(wins) else 0,
        avg_loss_r=round(losses.mean(), 2) if len(losses) else 0,
        expectancy_r=round(r.mean(), 3),
        ci95_low=round(r.mean() - 1.96 * se, 3),
        ci95_high=round(r.mean() + 1.96 * se, 3),
        profit_factor=round(wins.sum() / -losses.sum(), 2) if losses.sum() < 0 else np.inf,
        total_r=round(r.sum(), 1),
        max_dd_r=round(dd, 1),
        max_losing_streak=streak,
        avg_risk_pts=round(t.risk_pts.mean(), 1),
        trades_per_month=round(len(r) / max(1, t.date.dt.to_period("M").nunique()), 1),
    )
