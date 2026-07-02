import numpy as np
from scipy.integrate import quad

# Feller condition: 2 * kappa * theta > xi^2

class Heston:

    def __init__(self, S0, r, q, kappa, theta, xi, rho, v0):
        self.S0 = S0
        self.r = r
        self.q = q

        self.kappa = kappa
        self.theta = theta
        self.xi = xi
        self.rho = rho
        self.v0 = v0

    def heston_cf(self, u, T):

        log_S0 = np.log(self.S0)
        z = self.kappa - self.rho * self.xi * 1j * u
        d = np.sqrt( (self.rho * self.xi * 1j * u - self.kappa)**2 + self.xi**2 * (u**2 + 1j * u) )
        if abs(z+d) < 1e-12:
            return np.nan
        g = (z - d) / (z + d)
        C = ( 1j * u * (self.r - self.q) * T + 
            self.kappa * self.theta * ( (z - d) * T - 
            2 * np.log( (1 - g * np.exp(-d * T)) / (1 - g) ) ) / self.xi**2 ) 
        D = (z - d) * (1 - np.exp(-d * T)) / ( self.xi**2 * (1 - g * np.exp(-d * T)) )
        phi = np.exp(C + D * self.v0 + 1j * u * log_S0)

        if np.isnan(phi):
            return np.nan
        else:
            return phi

    def p1_integrand(self, u, K, T):

        integrand_p1 = self.heston_cf(u=u-1j, T=T) * np.exp(-1j * u * np.log(K)) / (1j * u * self.heston_cf(u=-1j, T=T))
        real_integrand_p1 = np.real(integrand_p1)

        return real_integrand_p1

    def p2_integrand(self, u, K, T):

        integrand_p2 = self.heston_cf(u, T) * np.exp(-1j * u * np.log(K)) / (1j * u)
        real_integrand_p2 = np.real(integrand_p2)

        return real_integrand_p2

    def p_integral(self, p_integrand, K, T, lower_bound=1e-8, upper_bound=100):

        if lower_bound == 0:
            lower_bound += 1e-8
        integral, _ = quad(func=p_integrand, a=lower_bound, b=upper_bound, args=(K, T), epsabs=1e-6, epsrel=1e-6)
        p = 0.5 + integral / np.pi

        return p
    
    def p1(self, K, T):
        return self.p_integral(self.p1_integrand, K, T)
    
    def p2(self, K, T):
        return self.p_integral(self.p2_integrand, K, T)

    def call_price(self, K, T):
        P1 = self.p1(K, T)
        P2 = self.p2(K, T)
        C = self.S0 * np.exp(-self.q * T) * P1 - K * np.exp(-self.r * T) * P2
        return C
    
    def update_params(self, params):
        self.kappa, self.theta, self.xi, self.rho, self.v0 = params