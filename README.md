# Implied Volatility Surface and Model Calibration

Project by Alexsey Chernichenko. June 2026.

# Project Goal

The aim of this project is to analyse the behaviour of implied volatility (IV) in the S&P 500 options market and assess the ability of different models to reproduce observed market dynamics. Using S&P 500 option data from 2010 to 2023, implied volatilities are extracted by inverting the Black–Scholes model through Brent's numerical root-finding method, incorporating historical risk-free interest rates and dividend yields.

The extracted implied volatilities are used to investigate the evolution of the at-the-money (ATM) volatility and volatility skew over time, as well as to construct and compare implied volatility surfaces across different market regimes. In addition, the project calibrates the Heston stochastic volatility model and the Stochastic Volatility Inspired (SVI) model to market data by minimising the root mean square error between observed and model-implied volatilities. The performance of both models is then evaluated across low, moderate and high volatility environments to determine their effectiveness in capturing market-implied volatility dynamics.

# Background

## Implied Volatility

Implied volatility (IV) is the volatility parameter that reproduces the observed market price of an option when it is substituted into an option pricing model. Unlike historical volatility that is calculated from past returns, implied volatility reflects the market's expectations of future price fluctuations over the remaining life of the option. Consequently, implied volatility has become a standard measure of market uncertainty and is widely used for comparing options across different strikes and maturities.
Within the Black-Scholes framework (the reader may familiarize themselves with the framework here: https://github.com/StarStrider23/Black-Scholes-project), volatility is the only unobservable model input. Since the Black–Scholes pricing equations cannot be inverted analytically with respect to volatility, implied volatility must be obtained numerically by solving

$$ C_{BS}(\sigma) = C_{market} $$

or equivalently

$$ f(\sigma) = C_{BS}(\sigma) - C_{market} = 0 $$

where $C_{BS}$ is the theoretical Black-Scholes price and $C_{market}$ is the observed market price. Several numerical methods may be employed to solve this nonlinear equation. The Newton–Raphson algorithm is frequently used although it requires the evaluation of option Vega and may fail to converge when the initial guess is poor. Alternatively, Brent's method provides a more robust root-finding procedure with guaranteed convergence provided that the solution lies in the specified interval. The methods' only drawback is its slower convergence. Nevertheless, despite the slower convergence speed, Brent's method is still commonly preferred in practical implementations due to its numerical stability. 

Although implied volatility is most often extracted using the Black–Scholes model, alternative frameworks such as the Black model for futures options or stochastic volatility models may also be employed. Regardless of the chosen pricing model, the underlying principle remains unchanged - implied volatility is defined as the volatility input that equates the model price with the observed market price.

Empirical evidence demonstrates that implied volatility is not constant across strikes and maturities. Instead, it exhibits systematic patterns known as volatility smiles, skews and term structures. To analyse these patterns, implied volatility is commonly plotted against strike price $K$, moneyness $M$, or forward moneyness $F$ for a fixed maturity, producing a volatility smile or skew. Moneyness is typically defined as the ratio of strike to spot price $ M $ = $ K/S $, while forward moneyness is defined as

$$ F=\frac{K}{F} $$

where

$$ F=S e^{(r-q) T} $$

with $r$ and $q$ being risk-free interest rates and dividend yields respectively.

Forward moneyness is often preferred as it accounts for interest rates and dividend yields, and therefore being  more consistent comparisons across maturities. 

Finally, there is a more comprehensive representation of how implied volatility changes across different maturity and strikes/moneyness/future moneyness. It is provided by the implied volatility surface.

$$ \sigma_{IV} = \sigma_{IV}(F, T) $$

The implied volatility surface offers a complete picture of market expectations and serves as the primary object for the calibration and evaluation of volatility models. 

Of course, one needs to be aware of the fact that a typical implied volatilty surface is also a product of interpolation. There does not exist a continuous spectrum of implied volatilties simply because maturities and strikes/moneyness/forward moneyness themselves are discrete. Therefore, a common practice is to connect the points by interpolation which creates a surface. An example can be found below.

<img width="925" height="430" alt="Снимок экрана 2026-06-29 в 18 40 03" src="https://github.com/user-attachments/assets/c1b5e07d-8c6a-4e7b-85f1-aee43dc0f9ab" />


## Heston Model. Dynamics

The Heston model is a continuous-time stochastic process that assumes that both the underlying and volatiltiy evolve stochastic. This allows the model to capture important market phenomena such as volatility clustering and the volatility smile observed in option markets. Overall, the model provides a more realistic reperesenation of market dynamics. 

The model is therefore fully described by two stochastic differential equations (SDE) - one for the underlying prices $S_t$ and the other one for its volatility $\nu_t$.

$$ dS_t = \mu S_{t} dt + \sqrt{\nu_t} S_t dW_t^S $$

$$ d\nu_t = \kappa (\theta - \nu_t) dt + \xi \sqrt{\nu_t} dW_t^\nu $$

where $dW_t^S$ and $dW_t^\nu$ are the Wiener processes\Brownian Motions for the asset price $S_t$ and volatility $\nu_t$ respectively. $\kappa$ is the rate at which $\nu_t$ reverts to $\theta$, which in its turn is the long variance or long-run average variance of the price (as $t$ tends to infinity, the expected value of $\nu_t$ tends to $\theta$). Finally, $\rho$ is the correlation between $dW_t^S$ and $dW_t^\nu$, and $\xi$ is the volatility of the volatility (vol-of-vol). The existence of $\xi$ is of course explained by the fact that volatility itself becomes a stochastic process within this framwork.

Besides the SDEs above, there are two important conditions:

$$ dW_t^S dW_t^\nu = \rho dt $$

which indicates that the two Wiener processes are correlated, and

$$ 2\kappa \theta > \xi^2 $$

which is called the Feller condition. This condition ensures that that the volatiltiy $\nu_t$ is strictly positive. 

## Heston Model. Semi-Analytical Solution

Despite incorporating stochastic volatility the Heston model remains analytically tractable for pricing European options. In 1993 Heston demonstrated that option prices can be expressed in semi-analytical form by exploiting the characteristic function of the logarithm of the underlying asset price rather than deriving its probability density directly.

Recall that, under the risk-neutral measure, the price of a European call option is given by

$$ C(S_t, K, T) = S_t e^{-q T} P_1 - K e^{-r T }P_2 $$

where ($S_t$) denotes the underlying asset price, ($K$) the strike price, ($T$) the time to maturity, ($r$) the risk-free interest rate and ($q$) the continuous dividend yield. Finally, ($P_1$) and ($P_2$) are risk-neutral probabilities. When the underlying probability is assumed to be normal, $P_1$ and $P_2$ are nothing else but the correspodning Cumulative Distribution Fucntion (CDF). However, the Heston model assumes that the underlying follows a distribution whose closed form is unknown. To be even more precise, the closed form cannot be dervied. This is because the distribution is now much more complicated since it depends on the volatility which itself is stochastic. Luckily, despite the obstacle, the Heston probabilities $P_1$ and $P_2$ can still be recovered. This is done through the Fourier inversion:

$$ P_j = \frac{1}{2} + \frac{1}{\pi} \int_0^\infty \Re \left( \frac{e^{-iu\ln K} \varphi_j(u)}{iu} \right)du \qquad j=1,2 $$

where $\Re(...)$ denotes the real part of a complex-valued function and $\varphi_j(u)$ is the characteristic function of the log-asset price.

The characteristic function can be written as

$$ \varphi(u) = \exp \left(C(u, T) + D(u, T) v_0 + i u \ln S_t\right) $$

where $v_0$ is the initial variance while the functions $C(u, T)$ and $D(u, T)$ depend on the model parameters and admit closed-form expressions involving complex-valued functions. Consequently, the Heston model is referred to as semi-analytical. Although the characteristic function is available in closed form, numerical integration is still required to evaluate the Fourier integral and obtain option prices.

An alternative formulation, commonly known as the Little Heston Trap, exists. It modifies the original representation of the characteristic function in order to avoid discontinuities associated with complex logarithms. This approach improves numerical stability and is frequently preferred in practical implementations, particularly when calibrating the model repeatedly to market data. 

## Stochastic Volatilty Inspired (SVI) model

Unlike the Heston model, which specifies stochastic dynamics for the underlying asset and its volatility, SVI directly parameterises the implied volatility surface. It models the shape of market implied volatility smiles without imposing assumptions on the underlying asset price process.

The SVI parameterisation is expressed in terms of total implied variance,

$$ \omega(k, T) = \sigma_{IV}^2 (k, T) T $$

where $\sigma_{IV}$ denotes the implied volatility, $T$ is the time to maturity and $k$ is log-forward moneyness. 

$$ k = \ln\left(\frac{K}{F}\right) $$

For a fixed maturity, the SVI smile is parameterised as

$$ \omega(k) = a + b \left( \rho(k - m) + \sqrt{(k - m)^2 + \sigma^2} \right)  $$

where $a$, $b$, $\rho$, $m$ and $\sigma$ are model parameters. The parameter $a$ controls the overall level of total variance, $b$ determines the slope of the smile wings, $\rho$ governs the orientation and asymmetry of the smile, $m$ shifts the location of the smile along the moneyness axis and $\sigma$ controls the curvature around the smile minimum.

Since SVI directly models total implied variance rather than option prices, calibration is typically performed by minimising the discrepancy between market and model-implied volatilities across strikes for each maturity. 

As a final note, it was already mentioned that SVI does not rely on an underlying stochastic process and directly parametrises implied volatility. It therefore cannot be used to simulate asset price dynamics directly unlike the Heston model. Instead, it should be viewed as a flexible and practical representation of market-implied volatility surfaces. Its ability to accurately fit market data and its computational speed have made SVI a widely adopted framework in both academic research and industry practice.

# Methodology

# Structure

# Results

# Discussion
