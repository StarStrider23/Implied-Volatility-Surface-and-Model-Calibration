import pandas as pd
import numpy as np

from black_scholes import BlackScholes
from brent import brent
from interpolate_rate import interpolate_rate

# SPY option data (2010-2013)

dfs = [pd.read_parquet(f"spy_eod_{year}.parquet") for year in range(2010, 2024)]

df = pd.concat(dfs, ignore_index=True)

days = 365
df.columns = df.columns.str.strip("[]").str.lower()
df["c_mid"] = (df["c_bid"] + df["c_ask"]) / 2
df["yte"] = df["dte"]/days
df = df[(df["c_bid"] > 0) & (df["c_ask"] > 0) &
        (df["c_mid"] > 0.1) & (df["yte"].between(7/days, 1))].copy()

near_atm_data = df[(df["strike_distance_pct"].between(0, 0.2))].copy()

# Annual Dividend Yield q

div_data = pd.read_csv("_spy.csv")[["Date", "Close", "Dividend"]]
div_data = div_data.rename(columns={"Date" : "quote_date", "Dividend" : "dividend"})
nonzero_div = div_data[div_data["dividend"] > 0].copy()
nonzero_div["annual_dividend"] = (nonzero_div["dividend"].rolling(4, min_periods=1).sum())
nonzero_div["q"] = nonzero_div["annual_dividend"] / nonzero_div["Close"]
div_data = div_data.merge(nonzero_div[["quote_date", "q"]], on="quote_date", how="left")
div_data["q"] = div_data["q"].ffill()
near_atm_data = near_atm_data.merge(div_data[["quote_date", "q"]], on="quote_date", how="left").copy()

# Risk-free interest rate r

rate_data = pd.read_csv("us_treasury_yields_daily.csv")
rate_data = rate_data[["date", "US1M", "US3M", "US6M", "US1Y"]][rate_data["date"] > "2010-01-01"].copy()
rate_data = rate_data.rename(columns={"date" : "quote_date"})
near_atm_data = near_atm_data.merge(rate_data, on="quote_date", how="left")
near_atm_data["r"] = near_atm_data.apply(interpolate_rate, axis=1).copy()
near_atm_data["r"] = near_atm_data["r"] / 100
near_atm_data["r"] = near_atm_data["r"].ffill()
near_atm_data = near_atm_data.drop(["US1M", "US3M", "US6M", "US1Y"], axis="columns").copy()

# Forward Moneyness

near_atm_data["forward_moneyness"] = ( near_atm_data["strike"] 
                                      / (near_atm_data["underlying_last"] * 
                                         np.exp( (near_atm_data["r"] - near_atm_data["q"]) * near_atm_data["yte"]) ) 
                                         )

# Filtering out options with f_low * f_high < 0

near_atm_data["f_low"] = BlackScholes(S=near_atm_data["underlying_last"], K=near_atm_data["strike"], 
                                      r=near_atm_data["r"], q=near_atm_data["q"], sigma=1e-6,
                                      T=near_atm_data["yte"]).option_price() - near_atm_data["c_mid"]
near_atm_data["f_high"] = BlackScholes(S=near_atm_data["underlying_last"], K=near_atm_data["strike"], 
                                       r=near_atm_data["r"], q=near_atm_data["q"], sigma=5.0, 
                                       T=near_atm_data["yte"]).option_price() - near_atm_data["c_mid"]
near_atm_data = near_atm_data[(near_atm_data["f_low"] * near_atm_data["f_high"] < 0)].copy()

near_atm_data = near_atm_data.rename(columns={"c_mid" : "call_price"})

# Extracting IV w/ Brent

near_atm_data["iv"] = near_atm_data.apply(brent, axis=1).copy()

# Extracting Vega

near_atm_data["vega"] = BlackScholes(S=near_atm_data["underlying_last"], K=near_atm_data["strike"], 
                                      r=near_atm_data["r"], q=near_atm_data["q"], 
                                      sigma=near_atm_data["iv"], T=near_atm_data["yte"]).compute_vega()

# Saving the processed data

cols = ["quote_date", "yte", "call_price", "underlying_last", "strike", "forward_moneyness", 
        "strike_distance_pct", "r", "q", "iv", "vega"]

near_atm_data[cols].to_csv("near_atm_data.csv", index="False")