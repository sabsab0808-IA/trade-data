set -u
O=${1:-data_ext}; mkdir -p $O/cboe $O/cftc_cot $O/fama_french $O/fred $O/treasury
A="Mozilla/5.0"
for s in VIX VIX3M VIX9D VIX6M VIX1D VVIX SKEW OVX GVZ; do curl -sSL -A "$A" --max-time 60 -o $O/cboe/${s}_History.csv "https://cdn.cboe.com/api/global/us_indices/daily_prices/${s}_History.csv" && echo "cboe $s $(wc -l < $O/cboe/${s}_History.csv)"; done
for y in $(seq 2010 2026); do
  curl -sSL -A "$A" --max-time 120 -o $O/cftc_cot/fut_fin_txt_$y.zip https://www.cftc.gov/files/dea/history/fut_fin_txt_$y.zip
  curl -sSL -A "$A" --max-time 120 -o $O/cftc_cot/fut_disagg_txt_$y.zip https://www.cftc.gov/files/dea/history/fut_disagg_txt_$y.zip
  curl -sSL -A "$A" --max-time 120 -o $O/cftc_cot/deacot$y.zip https://www.cftc.gov/files/dea/history/deacot$y.zip
  echo "cot $y"
done
for f in F-F_Research_Data_Factors_daily_CSV F-F_Momentum_Factor_daily_CSV F-F_Research_Data_5_Factors_2x3_daily_CSV F-F_Research_Data_Factors_CSV 48_Industry_Portfolios_daily_CSV; do
  curl -sSL -A "$A" --max-time 120 -o $O/fama_french/$f.zip https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/$f.zip && echo "ff $f"; done
for s in DGS10 DGS2 DGS3MO T10Y2Y DFF VIXCLS BAMLH0A0HYM2 DTWEXBGS DCOILWTICO WALCL RRPONTSYD; do curl -sS -A "$A" --max-time 90 -o $O/fred/$s.csv "https://fred.stlouisfed.org/graph/fredgraph.csv?id=$s" && echo "fred $s $(wc -l < $O/fred/$s.csv)" || echo "fred $s ECHEC"; done
for y in $(seq 2010 2026); do curl -sSL -A "$A" --max-time 60 -o $O/treasury/par_yield_$y.csv "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/$y/all?type=daily_treasury_yield_curve&field_tdr_date_value=$y&page&_format=csv" && echo "tsy $y $(wc -l < $O/treasury/par_yield_$y.csv)"; done
echo FINI
