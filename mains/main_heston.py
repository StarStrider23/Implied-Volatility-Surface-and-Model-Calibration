import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

from models.heston import Heston
from functions.rmse import rmse_heston
from functions.brent import brent

from scipy.optimize import differential_evolution

date1 = '2017-07-24' #low vol
date2 = '2020-03-13' #high vol
date3 = '2023-10-20' #moderate vol

df = pd.read_csv("near_atm_data.csv")

date = date1
df_date = df[(df["quote_date"] == date)].copy()

# Smaller sample with common strikes (5 first strikes just below the underlying price)
strike_set = [set(group["strike"]) for _, group in df_date.groupby("yte")]

common_strikes = sorted(set.intersection(*strike_set))
common_strikes = [strike for strike in common_strikes if strike < df_date["underlying_last"].values[0]][-5:]

df_date = df_date[df_date["strike"].isin(common_strikes)].copy()

# Optimizing Heston parameters

# kappa, theta, xi, rho, v0
bounds = [(0.01, 100.0), (0.0001, 1.0), (0.01, 5.0), (-0.99, 0.99), (0.0001, 1.0)] 

if __name__ == "__main__":

    params = differential_evolution(rmse_heston, bounds=bounds, args=(df_date,), maxiter=200,
                                    popsize=15, polish=True, tol=1e-4, workers=-1, updating='deferred')

    best_params = params.x

    call_price_heston = []

    for _, option in df_date.iterrows():

        S0 = option["underlying_last"]
        r = option["r"]
        q = option["q"]
        K = option["strike"]
        T = option["yte"]

        heston = Heston(S0=S0, r=r, q=q, kappa=best_params[0],
                        theta=best_params[1], xi=best_params[2], 
                        rho=best_params[3], v0=best_params[4])

        call_price_h = heston.call_price(K, T)

        call_price_heston.append(call_price_h)

    df_date["call_price"] = call_price_heston

    df_date["iv_heston"] = df_date.apply(brent, axis=1)

    df_date.to_csv(f"heston_{date}.csv", index=False)

    params_dict = {"kappa": float(best_params[0]), "theta": float(best_params[1]),
                   "xi": float(best_params[2]), "rho": float(best_params[3]),
                   "v0": float(best_params[4]), "rmse": float(params.fun)}
        
    with open(f"heston_params_{date}.json", "w") as f:
        json.dump(params_dict, f, indent=4)

# Error Heatmap

df_heston = pd.read_csv(f"heston_{date}.csv")

df_heston["error"] = df_heston["iv"] - df_heston["iv_heston"]
df_heston["rel_error"] = df_heston["error"] / df_heston["iv"]

print("MAE is: ", abs(df_heston["error"]).mean())
print("MRE is: ", df_heston["rel_error"].mean())

heatmap_data = df_heston.pivot(values="error", index="strike", columns="yte")

plt.figure(figsize=(12, 8))

plt.imshow(heatmap_data, aspect='auto', origin='lower', cmap='RdBu_r',
           extent = [heatmap_data.columns.min(), heatmap_data.columns.max(), 
                     heatmap_data.index.min(), heatmap_data.index.max()])

plt.colorbar(label='Extracted IV - Heston IV')

plt.xlabel('Maturity')
plt.ylabel('Strike')
plt.title(f'Error Heat Map, {date}')

plt.show()

# Error Heatmap side by side

heatmap_data = df_heston.pivot(values="error", index="strike", columns="yte")
heatmap_data_int = heatmap_data.interpolate(axis=0, limit_area="inside")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))

im1 = ax1.imshow(heatmap_data, aspect='auto', origin='lower', cmap='RdBu_r',
           extent = [heatmap_data.columns.min(), heatmap_data.columns.max(), 
                     heatmap_data.index.min(), heatmap_data.index.max()])

ax1.set_xlabel("Maturity")
ax1.set_ylabel("Strike")
ax1.set_title("Raw Uninterpolated IV")
fig.colorbar(im1, ax=ax1, label='Extracted IV - Heston IV')

im2 = ax2.imshow(heatmap_data_int, aspect='auto', origin='lower', cmap='RdBu_r',
           extent = [heatmap_data_int.columns.min(), heatmap_data_int.columns.max(), 
                     heatmap_data_int.index.min(), heatmap_data_int.index.max()])

ax2.set_xlabel("Maturity")
ax2.set_ylabel("Strike")
ax2.set_title("Raw Uninterpolated IV")
fig.colorbar(im2, ax=ax2, label='Extracted IV - Heston IV')

fig.suptitle(f'Error Heat Map, {date}')

plt.show()

# Vol 3D surfaces, Heston

surface_iv = df_heston.pivot_table(values="iv", index="forward_moneyness", columns="yte").copy()
surface_iv = surface_iv.interpolate(axis=0, limit_area='inside')

surface_heston = df_heston.pivot_table(values="iv_heston", index="forward_moneyness", columns="yte").copy()
surface_heston = surface_heston.interpolate(axis=0, limit_area='inside')

X1, Y1 = np.meshgrid(surface_iv.columns, surface_iv.index)
Z1 = surface_iv.values

Z2 = surface_heston.values

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

ax1.plot_surface(X1, Y1, Z1, cmap='viridis')
ax2.plot_surface(X1, Y1, Z2, cmap='plasma')

fig.suptitle(f"Implied Volatility Surfaces {date}")

ax1.set_xlabel("Maturity")
ax1.set_ylabel("Forward Moneyness")
ax1.set_zlabel("IV")
ax1.set_title("Implied Volatility")

ax2.set_xlabel("Maturity")
ax2.set_ylabel("Forward Moneyness")
ax2.set_zlabel("Heston IV")
ax2.set_title("Heston Implied Volatility")

ax1.view_init(elev=30, azim=45)
ax2.view_init(elev=30, azim=45)

plt.show()

# Vol smiles, Heston

yte_unique = sorted(surface_iv.columns)

L = int(round(len(yte_unique)/5))

c = ["blue", "red", "green", "gold", "violet", "black"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,8))

for l in range(len(c)-1):
    ax1.plot(surface_iv.iloc[:, l * L], color=c[l], label=f"{round(surface_iv.iloc[:, l * L].name, 2)} years")
    ax2.plot(surface_heston.iloc[:, l * L], color = c[l])

ax1.plot(surface_iv.iloc[:, -1], color = c[-1], label=f"{round(surface_iv.iloc[:, -1].name, 2)} years")
ax2.plot(surface_heston.iloc[:, -1], color = c[-1])

fig.suptitle(f"Implied Volatiltiy Skews, {date}")

ax1.set_title("Implied Volatility Skews")
ax1.set_xlabel("Forward Moneyness")
ax1.set_ylabel("IV")

ax2.set_title("Heston Implied Volatility Skews")
ax2.set_xlabel("Forward Moneyness")
ax2.set_ylabel("Heston IV")

ax1.grid(True, alpha=0.2, color = "grey", ls='--', lw = 1)
ax2.grid(True, alpha=0.2, color = "grey", ls='--', lw = 1)

fig.legend()

plt.show()
