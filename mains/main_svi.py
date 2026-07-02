import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize

from functions.rmse import rmse_svi
from models.svi import svi

date1 = '2017-07-24' #low vol
date2 = '2020-03-13' #high vol
date3 = '2023-10-20' #moderate vol

df = pd.read_csv("near_atm_data.csv")

date = date3
df_date = df[(df["quote_date"] == date)].copy()

df_date["tot_var"] = df["iv"]**2 * df["yte"]

df_date["log_fm"] = np.log(df["forward_moneyness"])

# Optimizing SVI parameters

# a, b, rho, m, sigma
x0 = [0.02, 0.2, -0.5, 0.0, 0.2]
bounds = [(-1.0, 1.0), (1e-6, 5.0), (-0.999, 0.999), (-2.0, 2.0), (1e-6, 2.0)]

params = []
    
for maturity, group in df_date.groupby("yte"):

    k = group["log_fm"].values
    market_tot_var = group["tot_var"].values
    vega = group["vega"].values

    res = minimize(rmse_svi, x0=x0, args=(market_tot_var, k, vega),
                   method="L-BFGS-B", bounds=bounds)

    params.append({"yte": maturity, "a": res.x[0], "b": res.x[1],
                   "rho": res.x[2], "m": res.x[3], "sigma": res.x[4], "rmse": res.fun})
        
    params_df = pd.DataFrame(params)

    params_df.to_csv(f"svi_params_{date}.csv", index="False")

params_df = pd.read_csv(f"svi_params_{date}.csv")

print("ARMSE is: ", params_df["rmse"].mean())

df_svi = df_date.merge(params_df, on="yte", how="left")
        
df_svi["svi_tot_var"] = svi(df_svi["log_fm"], df_svi["a"], df_svi["b"], 
                             df_svi["rho"], df_svi["m"], df_svi["sigma"])

df_svi["svi_iv"] = np.sqrt(df_svi["svi_tot_var"] / df_svi["yte"])

df_svi["error"] = df_svi["iv"] - df_svi["svi_iv"]
df_svi["rel_error"] = df_svi["error"] / df_svi["iv"]

print("MAE is: ", abs(df_svi["error"]).mean())
print("MRE is: ", df_svi["rel_error"].mean())

# Error Heatmap, SVI

heatmap_data = df_svi.pivot(values="error", index="strike", columns="yte")
heatmap_data_int = heatmap_data.interpolate(axis=0, limit_area="inside")

plt.figure(figsize=(12, 8))

plt.imshow(heatmap_data, aspect='auto', origin='lower', cmap='RdBu_r',
           extent = [heatmap_data.columns.min(), heatmap_data.columns.max(), 
                     heatmap_data.index.min(), heatmap_data.index.max()])
plt.colorbar(label='Extracted IV - SVI IV')

plt.xlabel("Maturity")
plt.ylabel("Moneyness")
plt.title(f"SVI Calibration Error Heatmap, {date}")

plt.show()

# Error Heatmap side by side

heatmap_data = df_svi.pivot(values="error", index="strike", columns="yte")
heatmap_data_int = heatmap_data.interpolate(axis=0, limit_area="inside")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))

im1 = ax1.imshow(heatmap_data, aspect='auto', origin='lower', cmap='RdBu_r',
           extent = [heatmap_data.columns.min(), heatmap_data.columns.max(), 
                     heatmap_data.index.min(), heatmap_data.index.max()])

ax1.set_xlabel("Maturity")
ax1.set_ylabel("Strike")
ax1.set_title("Raw Uninterpolated IV")
fig.colorbar(im1, ax=ax1, label='Extracted IV - SVI IV')

im2 = ax2.imshow(heatmap_data_int, aspect='auto', origin='lower', cmap='RdBu_r',
           extent = [heatmap_data_int.columns.min(), heatmap_data_int.columns.max(), 
                     heatmap_data_int.index.min(), heatmap_data_int.index.max()])

ax2.set_xlabel("Maturity")
ax2.set_ylabel("Strike")
ax2.set_title("Raw Uninterpolated IV")
fig.colorbar(im2, ax=ax2, label='Extracted IV - SVI IV')

fig.suptitle(f'Error Heat Map, {date}')

plt.show()

# Implied Vol Surfaces, SVI

surface_svi = df_svi.pivot_table(values="svi_iv", index="forward_moneyness", columns="yte")
surface_svi = surface_svi.interpolate(axis=0, limit_area="inside")

surface_iv = df_svi.pivot_table(values="iv", index="forward_moneyness", columns="yte")
surface_iv = surface_iv.interpolate(axis=0, limit_area="inside")

X1, Y1 = np.meshgrid(surface_iv.columns, surface_iv.index)
Z1 = surface_iv.values

X2, Y2 = np.meshgrid(surface_svi.columns, surface_svi.index)
Z2 = surface_svi.values

fig = plt.figure(figsize=(10,8))
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

ax1.plot_surface(X1, Y1, Z1, cmap='viridis')
ax2.plot_surface(X2, Y2, Z2, cmap='plasma')

fig.suptitle(f"Implied Volatility Surfaces, {date}")

ax1.set_xlabel("Maturity")
ax1.set_ylabel("Forward Moneyness")
ax1.set_zlabel("IV")
ax1.set_title("Implied Volatility")

ax2.set_xlabel("Maturity")
ax2.set_ylabel("Forward Moneyness")
ax2.set_zlabel("SVI IV")
ax2.set_title("SVI Implied Volatility")

ax1.view_init(elev=30, azim=45)
ax2.view_init(elev=30, azim=45)

plt.show()

# Implied Vol Skews, SVI

yte_unique = sorted(surface_iv.columns)

L = int(round(len(yte_unique)/5))

c = ["blue", "red", "green", "gold", "violet", "black"]

fig, (ax1, ax2) = plt.subplots(1, 2)

for l in range(len(c)-1):
    ax1.plot(surface_iv.iloc[:, l * L], color = c[l], label=f"{round(surface_iv.iloc[:, l * L].name, 2)} years")
    ax2.plot(surface_svi.iloc[:, l * L], color = c[l])

ax1.plot(surface_iv.iloc[:, -1], color = c[-1], label=f"{round(surface_iv.iloc[:, -1].name, 2)} years")
ax2.plot(surface_svi.iloc[:, -1], color = c[-1])

fig.suptitle(f"Implied Volatiltiy Skews, {date}")

ax1.set_title("Implied Volatility Skews")
ax1.set_xlabel("Forward Moneyness")
ax1.set_ylabel("IV")

ax2.set_title("SVI Implied Volatility Skews")
ax2.set_xlabel("Forward Moneyness")
ax2.set_ylabel("SVI IV")

ax1.grid(True, alpha=0.2, color = "grey", ls='--', lw = 1)
ax2.grid(True, alpha=0.2, color = "grey", ls='--', lw = 1)

fig.legend()

plt.show()
