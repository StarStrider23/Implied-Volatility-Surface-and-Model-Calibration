import numpy as np
from scipy.stats import norm

class BlackScholes:

    def __init__(self, S, K, r, q, sigma, T):
        self.S = S
        self.K = K
        self.r = r
        self.q = q
        self.sigma = sigma
        self.T = T

    def option_price(self, option="call"):
        if option == "call":
            V = (
                norm.cdf(self.compute_d1()) * self.S * np.exp(-self.q * self.T) - 
                norm.cdf(self.compute_d2()) * self.K * np.exp(-self.r * self.T)
                )
        elif option == "put":
            V = (
                norm.cdf(-self.compute_d2()) * self.K * np.exp(-self.r * self.T) - 
                norm.cdf(-self.compute_d1()) * self.S * np.exp(-self.q * self.T)
                )
        else:
            raise ValueError('Option should either be call or put')
        
        return V

    def compute_d1(self):
        d1 = (
            np.log(self.S / self.K) + 
            (self.r - self.q + self.sigma**2 / 2) * self.T) / (self.sigma * np.sqrt(self.T)
            )

        return d1

    def compute_d2(self):
        d2 = (
            (np.log(self.S / self.K) + 
            (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * np.sqrt(self.T)) - 
            self.sigma * np.sqrt(self.T)
            )

        return d2
    
    def compute_delta(self, option="call"):
        if option == "call":
            delta = np.exp(-self.q * self.T) * norm.cdf(self.compute_d1())
        elif option == "put":
            delta = np.exp(-self.q * self.T) * (norm.cdf(self.compute_d1()) - 1)
        else:
            raise ValueError('Option should either be call or put')
        
        return delta

    def compute_gamma(self, option="call"):
        if option == "call" or option == "put":
            gamma = np.exp(-self.q * self.T) * norm.pdf(self.compute_d1()) / (self.S * self.sigma * np.sqrt(self.T))
        else:
            raise ValueError('Option should either be call or put')

        return gamma

    def compute_vega(self, option="call"):
        if option == "call" or option == "put":
            vega = self.S * np.exp(-self.q * self.T) * norm.pdf(self.compute_d1()) * np.sqrt(self.T)
        else:
            raise ValueError('Option should either be call or put')

        return vega

    def compute_theta(self, option="call"):
        if option == "call":
            theta = (
                - self.S * np.exp(-self.q * self.T) * norm.pdf(self.compute_d1()) * self.sigma / (2 * np.sqrt(self.T)) - 
                self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.compute_d2())  +
                self.q * self.S * np.exp(-self.q * self.T) * norm.cdf(self.compute_d1())
                )
        elif option == "put":
            theta = (
                - self.S * np.exp(-self.q * self.T) * norm.pdf(self.compute_d1()) * self.sigma / (2 * np.sqrt(self.T)) + 
                self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-self.compute_d2()) - 
                self.q * self.S * np.exp(-self.q * self.T) * norm.cdf(-self.compute_d1())
                )
        else:
            raise ValueError('Option should either be call or put')
    
        return theta

    def compute_rho(self, option="call"):
        if option == "call":
            rho = self.K * self.T * np.exp(- self.r * self.T) * norm.cdf(self.compute_d2())
        elif option == "put":
            rho = - self.K * self.T * np.exp(- self.r * self.T) * norm.cdf(-self.compute_d2())
        else:
            raise ValueError('Option should either be call or put')

        return rho
