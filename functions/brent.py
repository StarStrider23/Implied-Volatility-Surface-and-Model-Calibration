from models.black_scholes import BlackScholes
from scipy.optimize import brentq

def brent(df):

    S = df['underlying_last']
    K = df['strike']
    T = df['yte']
    r = df['r']
    q = df['q']

    call_price_market = df['call_price']

    def f(sigma):
        bs = BlackScholes(S=S, K=K, r=r, q=q, sigma=sigma, T=T)
        diff = bs.option_price('call') - call_price_market
        return diff

    return brentq(f, 1e-6, 5.0)

def brent_scalar(S, K, r, q, T, call_price):

    def f(sigma):
        bs = BlackScholes(S, K, r, q, sigma, T)
        diff = bs.option_price('call') - call_price
        return diff

    return brentq(f, 1e-6, 5.0)
