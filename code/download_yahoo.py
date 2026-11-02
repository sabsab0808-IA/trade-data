import json, sys, time, urllib.request, csv, datetime as dt
from pathlib import Path
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
FUT = ["ES","NQ","YM","RTY","CL","BZ","NG","RB","HO","GC","SI","HG","PL","PA","ZN","ZB","ZF","ZT","6E","6J","6B","6A","6C","6S","6M","6N","ZC","ZS","ZW","KE","ZL","ZM","KC","SB","CC","CT","OJ","LE","HE","GF","BTC","ETH"]
IDX = ["^GSPC","^NDX","^DJI","^RUT","^VIX","^VIX3M","^VIX9D","^VVIX","^SKEW","^TNX","^IRX","^FVX","^TYX","DX-Y.NYB","SPY","QQQ","IWM","TLT","IEF","GLD","USO","HYG","LQD","EEM","EFA","^STOXX50E","^GDAXI","^FTSE","^N225","^HSI"]
H = {"User-Agent": "Mozilla/5.0"}
def get(sym, interval="1d", rng=None):
    q = f"interval={interval}&includeAdjustedClose=true&events=div%2Csplit"
    q += f"&range={rng}" if rng else f"&period1=0&period2={int(time.time())}"
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?{q}"
    for a in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60))
            res = r["chart"]["result"][0]; ts = res.get("timestamp") or []
            qq = res["indicators"]["quote"][0]; adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose")
            rows = []
            for i, t in enumerate(ts):
                d = dt.datetime.fromtimestamp(t, dt.timezone.utc)
                rows.append([d.strftime("%Y-%m-%dT%H:%M:%SZ"), qq["open"][i], qq["high"][i], qq["low"][i], qq["close"][i], adj[i] if adj else qq["close"][i], qq["volume"][i]])
            return rows, res["meta"].get("exchangeTimezoneName")
        except Exception as e:
            err = e; time.sleep(3)
    print("ECHEC", sym, interval, err, flush=True); return None, None
import urllib.parse
log = []
for kind, lst in (("futures", FUT), ("indices_etf", IDX)):
    for s in lst:
        sym = s + "=F" if kind == "futures" else s
        rows, tz = get(sym)
        if rows:
            name = sym.replace("^", "").replace("=F", "").replace(".", "_")
            p = OUT / kind / f"{name}_1d.csv"; p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", newline="") as f:
                w = csv.writer(f); w.writerow(["ts_utc","open","high","low","close","adjclose","volume"]); w.writerows(r for r in rows if r[4] is not None)
            log.append([kind, sym, rows[0][0][:10], rows[-1][0][:10], len(rows)]); print(sym, rows[0][0][:10], rows[-1][0][:10], len(rows), flush=True)
        time.sleep(0.5)
# 1 heure, ~2 ans, marchés autorisés chez Topstep (CME)
for s in ["ES","NQ","YM","RTY","CL","NG","GC","SI","HG","ZN","ZB","ZF","6E","6J","6B","6A","ZC","ZS","ZW","LE","HE"]:
    rows, tz = get(s + "=F", "60m", "730d")
    if rows:
        p = OUT / "futures_1h" / f"{s}_1h.csv"; p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["ts_utc","open","high","low","close","adjclose","volume"]); w.writerows(r for r in rows if r[4] is not None)
        log.append(["futures_1h", s + "=F", rows[0][0][:10], rows[-1][0][:10], len(rows)]); print(s, "1h", len(rows), flush=True)
    time.sleep(0.5)
with open(OUT / "inventaire_yahoo.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["type","symbole","debut","fin","barres"]); w.writerows(log)
