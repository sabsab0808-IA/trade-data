"""Charge les CSV Databento (ohlcv-1m, contrat continu roulé au volume) d'un symbole -> DataFrame en heure de New York.

Usage : python3 -I code/load_databento.py <dossier data/SYM> <sortie.pkl>
Les .csv.zst sont décompressés avec le module zstandard s'il existe, sinon avec Node (>= 22, zlib.zstdDecompressSync).
"""
import io, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd

def read_zst(path: Path) -> pd.DataFrame:
    try:
        import zstandard
        raw = zstandard.ZstdDecompressor().stream_reader(open(path, "rb")).read()
    except ImportError:
        raw = subprocess.run(["node", "-e", "process.stdout.write(require('zlib').zstdDecompressSync(require('fs').readFileSync(process.argv[1])))", str(path)],
                             capture_output=True, check=True).stdout
    return pd.read_csv(io.BytesIO(raw), usecols=["ts_event", "instrument_id", "open", "high", "low", "close", "volume"])

def load(folder) -> pd.DataFrame:
    df = pd.concat([read_zst(f) for f in sorted(Path(folder).glob("*.csv.zst"))], ignore_index=True)
    df["ts"] = pd.to_datetime(df.ts_event, utc=True).dt.tz_convert("America/New_York")
    df = df.drop(columns="ts_event").drop_duplicates("ts", keep="last").sort_values("ts").reset_index(drop=True)
    return df[["ts", "open", "high", "low", "close", "volume", "instrument_id"]]

if __name__ == "__main__":
    df = load(sys.argv[1])
    bad = (df.high < df[["open", "close"]].max(axis=1)) | (df.low > df[["open", "close"]].min(axis=1))
    print("barres", len(df), df.ts.iloc[0], "->", df.ts.iloc[-1], "| contrats", df.instrument_id.nunique(), "| bougies incohérentes", int(bad.sum()))
    df.to_pickle(sys.argv[2])
