import numpy as np

from heston import Heston
from brent import brent_scalar

from svi import svi

# Heston

def rmse_heston(params, data):

    kappa, theta, xi, rho, v0 = params

    if (kappa <= 0 or theta <= 0 or xi <= 0 or
        v0 <= 0 or abs(rho) >= 1):
        return 1e10

    if 2 * kappa * theta <= xi**2:
        return 1e10

    errors = []

    for _, option in data.iterrows():

        try:

            S0 = option["underlying_last"]
            r = option["r"]
            q = option["q"]
            K = option["strike"]
            T = option["yte"]
            iv = option["iv"]

            heston = Heston(S0=S0, r=r, q=q, kappa=kappa,
                            theta=theta, xi=xi, rho=rho, v0=v0)

            call_price = heston.call_price(K, T)

            if not np.isfinite(call_price):
                return 1e10

            if call_price <= 0:
                return 1e10

            upper_bound = S0 * np.exp(-q * T)

            if call_price > upper_bound:
                return 1e10

            iv_h = brent_scalar(S=S0, K=K, T=T, r=r,
                                    q=q, call_price=call_price)

            if not np.isfinite(iv_h):
                return 1e10

            errors.append((iv_h - iv)**2)

        except Exception:
            return 1e10

    return np.sqrt(np.mean(errors))

# SVI

def rmse_svi(params, market_tot_var, k, vega):

    a, b, rho, m, sigma = params

    model_tot_var = svi(k, a, b, rho, m, sigma)

    error = (market_tot_var - model_tot_var)**2

    return np.sqrt(np.average(error, weights=vega))