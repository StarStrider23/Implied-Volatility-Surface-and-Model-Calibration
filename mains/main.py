import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("near_atm_data.csv")

# IV(ATM) vs IV(Near ATM), skew and skew/IV(ATM) across the years

df["year"] = pd.to_datetime(df["quote_date"]).dt.year

atm = df[df["forward_moneyness"].between(0.999, 1.001)].copy()
atm_annual = atm[["year", "iv"]].groupby(["year"]).mean(["iv"])
atm_annual = atm_annual.rename(columns={"iv" : "iv_atm"})

plt.figure(figsize=(12,8))
plt.plot(atm_annual.index, atm_annual["iv_atm"].values, "r--o", label="ATM IV")
plt.xlabel('Years')
plt.ylabel('IV')
plt.title('ATM IV Across Years 2010-2023')
plt.grid(True, alpha=0.2, color = "grey", ls='--', lw = 1)
plt.legend()
plt.show()

near_atm = df[df["forward_moneyness"].between(0.899, 0.901)].copy()
near_atm_annual = near_atm[["year", "iv"]].groupby(["year"]).mean(["iv"])
near_atm_annual = near_atm_annual.rename(columns={"iv" : "iv_near_atm"})

annual_diff = pd.merge(atm_annual, near_atm_annual, on=['year'], how = 'inner')
annual_diff["skew"] = annual_diff["iv_near_atm"] - annual_diff["iv_atm"]
annual_diff["rel_skew"] = annual_diff["skew"] / annual_diff["iv_atm"]

plt.figure(figsize=(12,8))
# plt.plot(annual_diff.index, annual_diff["iv_atm"].values, 'r--o', label="ATM IV")
# plt.plot(annual_diff.index, annual_diff["iv_near_atm"].values, 'b--o', label="near ATM IV")
plt.plot(annual_diff.index, annual_diff["skew"].values, 'y--o', label="Skew")
plt.plot(annual_diff.index, annual_diff["rel_skew"].values, 'g--o', label="Skew/(ATM IV)")
plt.xlabel('Years')
plt.ylabel('Metrics')
plt.title('Skew Across Years 2010-2023')
plt.grid(True, alpha=0.2, color = "grey", ls='--', lw = 1)
plt.legend()
plt.show()

# IV(FM, T), 3D plot, scatter

date1 = '2017-07-24' #low vol
date2 = '2020-03-13' #high vol
date3 = '2023-10-20' #moderate vol

date = date3

df_date = df[df["quote_date"] == date]

# Scatter plot

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111, projection='3d')

ax.scatter3D(df_date["yte"], df_date["forward_moneyness"], df_date["iv"], s=1, alpha=0.5, color='red', marker='o')

ax.set_title(f"Implied Volatility Scatter, {date}")
ax.set_xlabel('Forward Moneyness')
ax.set_ylabel('Maturity')
ax.set_zlabel('Implied Volatility')

ax.view_init(elev=30, azim=45)
plt.show()

# IV(FM, T), 3D plot, interpolated

surface = df_date.pivot_table(values="iv", index="forward_moneyness", columns="yte").copy()
surface = surface.interpolate(axis=0, limit_area='inside')

X, Y = np.meshgrid(surface.columns, surface.index)
Z = surface.values

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, Z, cmap = 'viridis')

ax.set_title(f"Implied Volatility Surface, {date}")
ax.set_xlabel('Maturity')
ax.set_ylabel('Forward Moneyness')
ax.set_zlabel('Implied Volatility')

ax.view_init(elev=30, azim=45)
plt.show()

# Vol skew/smile 

yte_unique = sorted(surface.columns)

L = int(round(len(yte_unique)/5))

c = ["blue", "red", "green", "gold", "violet", "black"]

plt.figure(figsize=(12,8))

for l in range(len(c)-1):
    plt.plot(surface.iloc[:, l * L], color=c[l], label=f"{round(surface.iloc[:, l * L].name, 2)} years")

plt.plot(surface.iloc[:, -1], color=c[-1], label=f"{round(surface.iloc[:, -1].name, 2)} years")

plt.grid(True, alpha=0.2, color = "grey", ls='--', lw = 1)
plt.title(f"Implied Volatiltiy Skews, {date}")
plt.xlabel("Forward Moneyness")
plt.ylabel("Implied Volatility")
plt.legend()

plt.show()
