"""Convertit les CSV Databento (NQ.v.0, ohlcv-1m) au format du projet (heure de New York) + id du contrat."""
import sys, glob
import numpy as np, pandas as pd
src, out = sys.argv[1], sys.argv[2]
frames = [pd.read_csv(f, usecols=["ts_event","instrument_id","open","high","low","close","volume"]) for f in sorted(glob.glob(f"{src}/nq_20*.csv"))]
df = pd.concat(frames, ignore_index=True)
df["ts"] = pd.to_datetime(df.ts_event, utc=True).dt.tz_convert("America/New_York")
df = df.drop(columns="ts_event").drop_duplicates("ts", keep="last").sort_values("ts").reset_index(drop=True)
df = df[["ts","open","high","low","close","volume","instrument_id"]]
bad = (df.high < df[["open","close"]].max(axis=1)) | (df.low > df[["open","close"]].min(axis=1))
tick_ok = np.isclose((df[["open","high","low","close"]]*4) % 1, 0).all(axis=1)
print("bars", len(df), df.ts.iloc[0], "->", df.ts.iloc[-1])
print("bad_ohlc", int(bad.sum()), "off_tick", int((~tick_ok).sum()), "contrats", df.instrument_id.nunique())
j = df.close.pct_change().abs(); print("sauts >2% en 1 min:", df.loc[j>0.02,"ts"].astype(str).tolist()[:15])
df.to_pickle(out)
