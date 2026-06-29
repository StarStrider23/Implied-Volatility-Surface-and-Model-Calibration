# Implied Volatility Surface and Model Calibration

Project by Alexsey Chernichenko. June 2026.

# Project Goal

The aim of this project is to analyse the behaviour of implied volatility (IV) in the S&P 500 options market and assess the ability of different models to reproduce observed market dynamics. Using S&P 500 option data from 2010 to 2023, implied volatilities are extracted by inverting the Black–Scholes model through Brent's numerical root-finding method, incorporating historical risk-free interest rates and dividend yields.

The extracted implied volatilities are used to investigate the evolution of at-the-money (ATM) volatility and volatility skew over time, as well as to construct and compare implied volatility surfaces across different market regimes. In addition, the project calibrates the Heston stochastic volatility model and the Stochastic Volatility Inspired (SVI) model to market data by minimising the root mean square error between observed and model-implied volatilities. The performance of both models is then evaluated across low, moderate and high volatility environments to determine their effectiveness in capturing market-implied volatility dynamics.

# Background

## Heston Model: Semi-Analytical Solution

Despite incorporating stochastic volatility the Heston model remains analytically tractable for pricing European options. In 1993 Heston demonstrated that option prices can be expressed in semi-analytical form by exploiting the characteristic function of the logarithm of the underlying asset price rather than deriving its probability density directly.

Recall that, under the risk-neutral measure, the price of a European call option is given by

$$ C(S_t, K, T) = S_t e^{-q T} P_1 - K e^{-r T }P_2 $$

where ($S_t$) denotes the underlying asset price, ($K$) the strike price, ($T$) the time to maturity, ($r$) the risk-free interest rate and ($q$) the continuous dividend yield. Finally, ($P_1$) and ($P_2$) are risk-neutral probabilities. When the underlying probability is assumed to be normal, $P_1$ and $P_2$ are nothing else but the correspodning Cumulative Distribution Fucntion (CDF). However, the Heston model assumes that the underlying follows a distribution whose closed form is unknown. To be even more precise, the closed form cannot be dervied. This is because the distribution is now much more complicated since it depends on the volatility which itself is stochastic. Luckily, despite the obstacle, the Heston probabilities $P_1$ and $P_2$ can still be recovered. This is done through the Fourier inversion:

$$ P_j = \frac{1}{2} + \frac{1}{\pi} \int_0^\infty \Re \left( \frac{e^{-iu\ln K} \varphi_j(u)}{iu} \right)du \qquad j=1,2 $$

where $\Re(...)$ denotes the real part of a complex-valued function and ($\varphi_j(u)$) is the characteristic function of the log-asset price.

The characteristic function can be written as

[
\phi(u)=\exp\left(C(u,\tau)+D(u,\tau)v_0+i u \ln S_t\right),
]

where (v_0) is the initial variance, while the functions (C(u,\tau)) and (D(u,\tau)) depend on the model parameters and admit closed-form expressions involving complex-valued functions. Consequently, the Heston model is referred to as **semi-analytical**: although the characteristic function is available in closed form, numerical integration is still required to evaluate the Fourier integral and obtain option prices.

An alternative formulation, commonly known as the **Little Heston Trap** (Albrecher et al., 2007), modifies the original representation of the characteristic function in order to avoid discontinuities associated with complex logarithms. This approach improves numerical stability and is frequently preferred in practical implementations, particularly when calibrating the model repeatedly to market data.


# Methodology

# Structure

# Results

# Discussion
