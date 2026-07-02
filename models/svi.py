import numpy as np

def svi(k, a, b, rho, m, sigma):

    tot_var = a + b * ( rho * (k - m) + np.sqrt((k-m)**2 + sigma**2))

    return tot_var