"""Collecte quotidienne gratuite (Yahoo Finance) — lancée chaque soir par GitHub Actions (.github/workflows/collecte.yml).

- 1 minute : 21 futures autorisés chez Topstep, 7 derniers jours, ajoutés à data_live/1m/<SYM>/<SYM>_<AAAA-MM>.csv (sans doublons).
  Yahoo ne garde que ~30 jours de 1 minute : en tournant chaque jour, on construit un historique 1 minute gratuit et sans trou.
- Journalier : VIX, VIX3M, VVIX, indices, ETF, ajoutés à data_live/1d/<SYM>.csv.
Horodatage UTC. Usage : python3 -I code/collecte_quotidienne.py <racine du dépôt>
"""
import csv, json, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
FUT_1M = ["ES", "NQ", "YM", "RTY", "CL", "NG", "GC", "SI", "HG", "ZN", "ZB", "ZF", "6E", "6J", "6B", "6A", "ZC", "ZS", "ZW", "LE", "HE"]
DAILY = ["^VIX", "^VIX3M", "^VIX9D", "^VVIX", "^SKEW", "^GSPC", "^NDX", "^RUT", "^TNX", "DX-Y.NYB", "SPY", "QQQ", "IWM", "TLT", "IEF", "GLD", "USO", "HYG"] + [s + "=F" for s in FUT_1M]
H = {"User-Agent": "Mozilla/5.0"}


def get(sym, interval, p1, p2):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?interval={interval}&period1={int(p1)}&period2={int(p2)}"
    for a in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            return [[datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]]
                    for i, t in enumerate(r.get("timestamp") or []) if q["close"][i] is not None]
        except Exception as e:  # noqa: BLE001
            err = e; time.sleep(10 * (a + 1))
    print("ECHEC", sym, interval, err, flush=True); return []


def merge(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    old = {}
    if path.exists():
        with open(path) as f:
            rd = csv.reader(f); next(rd, None)
            old = {r[0]: r for r in rd}
    for r in rows:
        old[r[0]] = [str(x) for x in r]
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["ts_utc", "open", "high", "low", "close", "volume"]); w.writerows(old[k] for k in sorted(old))
    return len(old)


now = time.time(); n_new = 0
for s in FUT_1M:
    rows = get(s + "=F", "1m", now - 7 * 86400, now)
    if not rows:
        continue
    by_month = {}
    for r in rows:
        by_month.setdefault(r[0][:7], []).append(r)
    for m, rr in by_month.items():
        merge(ROOT / "data_live" / "1m" / s / f"{s}_{m}.csv", rr)
    n_new += len(rows); print(s, "1m", len(rows), flush=True); time.sleep(1)
for s in DAILY:
    rows = get(s, "1d", now - 30 * 86400, now)
    if rows:
        name = s.replace("^", "").replace("=F", "").replace(".", "_")
        merge(ROOT / "data_live" / "1d" / f"{name}.csv", [r for r in rows if r[0][:10] < datetime.now(timezone.utc).strftime("%Y-%m-%d")])
        print(s, "1d", len(rows), flush=True)
    time.sleep(0.5)
print("barres 1 minute reçues :", n_new)
