"""Réplication de l'étude 14 (suivi de tendance 40 futures, doc 18) + contribution par secteur et version sans agricoles (doc 20b).
Usage : python3 -I code/replication_etude14_secteurs.py data_ext"""
import glob, sys
from pathlib import Path
import numpy as np, pandas as pd
EXT=Path(sys.argv[1] if len(sys.argv) > 1 else 'data_ext')
def yahoo(path):
    d=pd.read_csv(path); d["date"]=pd.to_datetime(d.ts_utc.str[:10]); return d.drop_duplicates("date").set_index("date").sort_index()
def sharpe(r): r=pd.Series(r).dropna(); return float(r.mean()/r.std()*np.sqrt(252))
spy=yahoo(EXT/"yahoo/indices_etf/SPY_1d.csv"); ret=spy.adjclose.pct_change().dropna()
R={}
for f in sorted(glob.glob(str(EXT/"yahoo/futures/*_1d.csv"))):
    name=Path(f).name[:-7]
    if name in ("BTC","ETH"): continue
    d=yahoo(f); d=d[(d.close>0)&(d.open>0)]
    r=d.close.pct_change(); gap=d.open/d.close.shift(1)-1; med=r.abs().rolling(60).median().shift(1)
    r=r.where(~(gap.abs()>5*med), d.close/d.open-1); R[name]=r
R=pd.DataFrame(R).sort_index(); R=R[R.index>="2000-01-01"]
logcum=np.log1p(R.fillna(0)).cumsum(); hist=R.notna().cumsum(); vol=R.rolling(60,min_periods=40).std()*np.sqrt(252)
me=R.groupby(R.index.to_period("M")).tail(1).index
W=pd.DataFrame(np.nan,index=R.index,columns=R.columns)
for d in me:
    i=R.index.get_loc(d)
    if i<252: continue
    ok=(hist.loc[d]>=252)&vol.loc[d].notna()
    if ok.sum()==0: continue
    sgn=np.sign(logcum.iloc[i]-logcum.iloc[i-252]); W.loc[d]=((sgn*0.40/vol.loc[d].clip(lower=0.05)).where(ok,0.0)/ok.sum()).values
W=W.ffill().shift(1).fillna(0.0); turn=W.diff().abs().sum(axis=1).fillna(0)
contrib=(W*R.fillna(0)); s14=contrib.sum(axis=1)-0.0003*turn; s14=s14[s14.index>="2001-01-01"]
print("REPLICATION étude 14 (futures) : Sharpe 2001-12", round(sharpe(s14["2001":"2012"]),2), "| 2013-26", round(sharpe(s14["2013":"2026"]),2), "| 2021-26", round(sharpe(s14["2021":"2026"]),2))
SECT={"Indices":["ES","NQ","YM","RTY"],"Taux":["ZT","ZF","ZN","ZB"],"Devises":["6E","6J","6B","6A","6C","6S","6M","6N"],"Métaux":["GC","SI","HG","PL","PA"],
      "Énergie":["CL","BZ","NG","RB","HO"],"Grains":["ZC","ZS","ZW","KE","ZL","ZM"],"Softs":["KC","SB","CC","CT","OJ"],"Viandes":["LE","HE","GF"]}
rows=[]
for k,v in SECT.items():
    x=contrib[v].sum(axis=1)
    for lab,a,b in (("2013–2026","2013","2026"),("2021–2026","2021","2026")):
        q=x[a:b]; rows.append(dict(secteur=k,periode=lab,rend_an_brut_pct=round(100*q.mean()*252,2),sharpe_brut=round(sharpe(q),2)))
S=pd.DataFrame(rows); print(S.to_string(index=False)); S.to_csv("secteurs_etude14_futures.csv",index=False)
# même règle, univers « équivalent ETF » (sans grains, softs, viandes, PA/PL)
etf_like=SECT["Indices"]+SECT["Taux"]+SECT["Devises"]+["GC","SI","HG","CL","NG"]
for lab,cols in (("futures sans agricoles/viandes",etf_like),):
    Wl=pd.DataFrame(np.nan,index=R.index,columns=cols); Rl=R[cols]
    for d in me:
        i=R.index.get_loc(d)
        if i<252: continue
        ok=(hist.loc[d,cols]>=252)&vol.loc[d,cols].notna()
        if ok.sum()==0: continue
        sgn=np.sign(logcum.iloc[i][cols]-logcum.iloc[i-252][cols]); Wl.loc[d]=((sgn*0.40/vol.loc[d,cols].clip(lower=0.05)).where(ok,0.0)/ok.sum()).values
    Wl=Wl.ffill().shift(1).fillna(0.0); sl=(Wl*Rl.fillna(0)).sum(axis=1)-0.0003*Wl.diff().abs().sum(axis=1).fillna(0)
    print(lab,"Sharpe 2013-26",round(sharpe(sl["2013":"2026"]),2),"| 2021-26",round(sharpe(sl["2021":"2026"]),2))
