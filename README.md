# Implied Volatility Surface and Model Calibration

Project by Alexsey Chernichenko. June 2026.

# Project Goal

The aim of this project is to analyse the behaviour of implied volatility (IV) in the S&P 500 options market and assess the ability of different models to reproduce observed market dynamics. Using S&P 500 option data from 2010 to 2023, implied volatilities are extracted by inverting the Black–Scholes model through Brent's numerical root-finding method, incorporating historical risk-free interest rates and dividend yields.

The extracted implied volatilities are used to investigate the evolution of the at-the-money (ATM) volatility and volatility skew over time, as well as to construct and compare implied volatility surfaces across different market regimes. In addition, the project calibrates the Heston stochastic volatility model and the Stochastic Volatility Inspired (SVI) model to market data by minimising the root mean square error between observed and model-implied volatilities. The performance of both models is then evaluated across low, moderate and high volatility environments to determine their effectiveness in capturing market-implied volatility dynamics.

# Data

The project uses publicly available datasets from the following sources:

1. **S&P 500 Options Data** : https://www.kaggle.com/datasets/dudesurfin/spy-options-eod-volatility-surface-2010-2023
2. **U.S. Treasury Yields** : https://www.kaggle.com/datasets/guillemservera/us-treasury-yields-daily
3. **S&P Stock Data with Dividend Yields** : https://www.kaggle.com/datasets/aliraza948/spdr-s-and-p-500-etf-spy
 
# Background

## Implied Volatility

Implied volatility (IV) is the volatility parameter that reproduces the observed market price of an option when it is substituted into an option pricing model. Unlike historical volatility that is calculated from past returns, implied volatility reflects the market's expectations of future price fluctuations over the remaining life of the option. Consequently, implied volatility has become a standard measure of market uncertainty and is widely used for comparing options across different strikes and maturities.
Within the Black-Scholes framework (the reader may familiarize themselves with the framework here: https://github.com/StarStrider23/Black-Scholes-project), volatility is the only unobservable model input. Since the Black–Scholes pricing equations cannot be inverted analytically with respect to volatility, implied volatility must be obtained numerically by solving

$$ C_{BS}(\sigma) = C_{market} $$

or equivalently

$$ f(\sigma) = C_{BS}(\sigma) - C_{market} = 0 $$

where $C_{BS}$ is the theoretical Black-Scholes price and $C_{market}$ is the observed market price. Several numerical methods may be employed to solve this nonlinear equation. The Newton–Raphson algorithm is frequently used although it requires the evaluation of option Vega and may fail to converge when the initial guess is poor. Alternatively, Brent's method provides a more robust root-finding procedure with guaranteed convergence provided that the solution lies in the specified interval. The methods' only drawback is its slower convergence. Nevertheless, despite the slower convergence speed, Brent's method is still commonly preferred in practical implementations due to its numerical stability. 

Although implied volatility is most often extracted using the Black–Scholes model, alternative frameworks such as the Black model for futures options or stochastic volatility models may also be employed. Regardless of the chosen pricing model, the underlying principle remains unchanged - implied volatility is defined as the volatility input that equates the model price with the observed market price.

Empirical evidence demonstrates that implied volatility is not constant across strikes and maturities. Instead, it exhibits systematic patterns known as volatility smiles, skews and term structures. To analyse these patterns, implied volatility is commonly plotted against strike price $K$, moneyness $M$, or forward moneyness $F$ for a fixed maturity, producing a volatility smile or skew. 

Forward moneyness is typically defined as the ratio of strike to spot price $M$ = $K/S$, while forward moneyness is defined as

$$ F = K/f $$

where

$$ f = S e^{(r-q) T} $$

with $r$ and $q$ being risk-free interest rates and dividend yields respectively.

Forward moneyness is often preferred as it accounts for interest rates and dividend yields, and therefore being  more consistent comparisons across maturities. 

Of course, one needs to be aware of the fact that a typical implied volatilty smile/skew is also a product of interpolation. There does not exist a continuous spectrum of implied volatilties simply because strikes/moneyness/forward moneyness themselves are discrete, albeit usually densely located. Therefore, a common practice is to connect the points by interpolation which creates a curve. An example can be found below.

<img width="1088" height="411" alt="Снимок экрана 2026-06-30 в 09 28 53" src="https://github.com/user-attachments/assets/b32afcdd-5ef1-4fb3-832d-23ff06b605ff" />

Finally, there is a more comprehensive representation of how implied volatility changes across different maturity and strikes/moneyness/future moneyness. It is provided by the implied volatility surface.

$$ \sigma_{IV} = \sigma_{IV}(F, T) $$

Equivalently $\sigma_{IV}(K, T)$ or $\sigma_{IV}(M, T)$. The implied volatility surface offers a complete picture of market expectations and serves as the primary object for the calibration and evaluation of volatility models. Analogous to an implied volatility smile/skew, an implied volatilty surface is also produced by interpolating. 

<img width="996" height="447" alt="Снимок экрана 2026-06-30 в 08 52 05" src="https://github.com/user-attachments/assets/0e85b1c5-ebf7-462d-88df-1b14c5334111" />

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

$$ k = \ln\left(K/F\right) $$

For a fixed maturity, the SVI smile is parameterised as

$$ \omega(k) = a + b \left( \rho(k - m) + \sqrt{(k - m)^2 + \sigma^2} \right)  $$

where $a$, $b$, $\rho$, $m$ and $\sigma$ are model parameters. The parameter $a$ controls the overall level of total variance, $b$ determines the slope of the smile wings, $\rho$ governs the orientation and asymmetry of the smile, $m$ shifts the location of the smile along the moneyness axis and $\sigma$ controls the curvature around the smile minimum.

Since SVI directly models total implied variance rather than option prices, calibration is typically performed by minimising the discrepancy between market and model-implied volatilities across strikes for each maturity. 

As a final note, it was already mentioned that SVI does not rely on an underlying stochastic process and directly parametrises implied volatility. It therefore cannot be used to simulate asset price dynamics directly unlike the Heston model. Instead, it should be viewed as a flexible and practical representation of market-implied volatility surfaces. Its ability to accurately fit market data and its computational speed have made SVI a widely adopted framework in both academic research and industry practice.

# Methodology

The analysis was conducted using S&P 500 European option data spanning the period from 2010 to 2023. As the option dataset did not include the corresponding risk-free interest rates or dividend yields required for option pricing, these inputs were obtained from separate historical datasets.

Historical U.S. Treasury yields were used as proxies for the risk-free interest rate. Since the available Treasury data consisted only of standard maturities (e.g., 1 month, 3 months, 6 months and 1 year), while the option dataset contained a wider range of maturities, the appropriate interest rate for each option was obtained through linear interpolation between the two nearest available Treasury maturities.

Historical dividend data were provided as quarterly values. To obtain the annual dividend yield required by the Black-Scholes model, the most recent four quarterly observations were summed for each option date, producing a rolling annual dividend estimate. Consequently, the dividend yield was allowed to vary over time rather than assuming a constant value across the entire dataset.

To focus the analysis on the most informative region of the implied volatility surface, the dataset was filtered to retain only options within the near ATM region. Implied volatilities were then extracted by numerically inverting the Black–Scholes pricing formula using an implementation of Brent's root-finding algorithm. Together with interpolation, this procedure was repeated for every option in the filtered dataset to construct the market implied volatility smiles/skews and surfaces.

It should be mentioend separately that the initial option dataset included a column with implied volatility values. However, by invsetigating the numbers, it turned out that these were not extracted using the Black-Scholes framework as these implied volatilty values didn't replicate the option prices in the dataset. A possible explanation is that the numbers were extracted using an alternative framework. Then, of course, one of the project goals was to extract the implied volatilties independently. 

The extracted implied volatilities were subsequently analysed to investigate the evolution of ATM implied volatility and the volatility skew throughout the sample period. The skew was defined as the difference between the implied volatility at forward moneyness 0.9 and that at forward moneyness 1.0. Based on this analysis, three representative trading dates corresponding to low, moderate and high volatility market regimes were selected for further investigation.

The second stage of the project focused on model calibration. A dedicated implementation of the Heston stochastic volatility model, based on its semi-analytical pricing formula, was developed to generate model option prices and implied volatilities. In parallel, the SVI parameterisation was implemented to model the implied volatility smile directly. For each model, a separate function based on the root mean square error (RMSE) between market and model-implied volatilities was constructed. In the case of the SVI model, the RMSE function additionally incorporated Black–Scholes Vega weights. This is a common practice in the SVI model calibration which allows to assign greater importance to options whose prices are more sensitive to changes in implied volatility.

The parameters of both models were estimated by minimising their respective objective functions for each of the three selected market regimes. In addition, the Heston model was calibrated using reduced subsets of the same market data in order to investigate the effect of sample size on calibration performance and parameter stability.

Finally, the calibrated models were evaluated by comparing their implied volatility surfaces and volatility smiles against the extracted market implied volatilities. Model performance was assessed both visually and quantitatively through the RMSE, discrepancy error and relative error between the market and model-implied volatilities. Additionally, error heatmaps were plotted in order to aid to asses model performance visually.

# Structure

# Results

## Near ATM Implied Volatilty Across Years

<img width="1191" height="751" alt="Снимок экрана 2026-06-27 в 16 39 48" src="https://github.com/user-attachments/assets/63658e3f-5dea-49d0-a00c-8884c38fb9d5" />

<img width="1175" height="734" alt="Снимок экрана 2026-06-27 в 16 47 20" src="https://github.com/user-attachments/assets/0dd651dc-bf81-4c0f-8e2c-87ae10d959e8" />

## Low, Moderate and High Volatilty Regimes

### Low Volatiltiy 

<img width="721" height="699" alt="Снимок экрана 2026-06-27 в 17 59 16" src="https://github.com/user-attachments/assets/0b1a61f7-d973-4f1d-9692-962cde420a93" />

<img width="1191" height="743" alt="Снимок экрана 2026-06-27 в 18 04 01" src="https://github.com/user-attachments/assets/bd133c08-5716-4f35-862e-6cb5b1d4a9f5" />

### Moderate Volatiltiy

<img width="703" height="683" alt="Снимок экрана 2026-06-27 в 18 00 29" src="https://github.com/user-attachments/assets/b4b91b37-1c2e-4bb3-ac4e-810c897eef8e" />

<img width="1187" height="740" alt="Снимок экрана 2026-06-27 в 18 05 30" src="https://github.com/user-attachments/assets/d690affb-a57c-4684-8e0a-abbd09599dbb" />

### High volatility 

<img width="696" height="699" alt="Снимок экрана 2026-06-27 в 18 01 29" src="https://github.com/user-attachments/assets/4c3b2a69-9085-4f01-8a3e-14dab187f721" />

<img width="1184" height="742" alt="Снимок экрана 2026-06-27 в 18 06 52" src="https://github.com/user-attachments/assets/40f1e696-1006-4f82-8393-51340fe45496" />

## Model Calibration. Heston Model

### Low Volatility 

Average error is:  -0.009852649667434293
Average relative error is:  -0.0722813670881121
RMSE: 0.042302903344413244

"kappa": 58.55405216806821
"theta": 0.021661461600542657
"xi": 1.1102242541446006
"rho": -0.9491776136870853
"v0": 0.07254150605992814

<img width="1440" height="461" alt="Снимок экрана 2026-06-28 в 13 25 38" src="https://github.com/user-attachments/assets/bc249e61-9f62-49ef-8eea-45616c4cdfc5" />

<img width="1107" height="448" alt="Снимок экрана 2026-06-28 в 14 26 17" src="https://github.com/user-attachments/assets/39cdebe6-bdb2-4c36-9b99-dc2ef988550a" />

<img width="936" height="440" alt="Снимок экрана 2026-06-28 в 14 19 12" src="https://github.com/user-attachments/assets/27a33c4c-2fd5-4e53-b1ab-6977bd23d57b" />

### Moderate Volatilty 

<img width="1440" height="466" alt="Снимок экрана 2026-06-28 в 13 26 26" src="https://github.com/user-attachments/assets/88c96f39-d4dd-4dd1-ad11-bce1dfd3f5e8" />

<img width="1094" height="441" alt="Снимок экрана 2026-06-28 в 14 27 31" src="https://github.com/user-attachments/assets/81d5bfee-9a32-4faa-9d1f-78e8805a97b3" />

<img width="922" height="432" alt="Снимок экрана 2026-06-28 в 14 20 24" src="https://github.com/user-attachments/assets/e8e83125-a0a6-47c6-8c6e-081dafb21689" />

### High Volatitility 

<img width="1440" height="466" alt="Снимок экрана 2026-06-28 в 13 24 50" src="https://github.com/user-attachments/assets/fa9aec4e-f313-42d4-8446-de5298fe28a2" />

<img width="1100" height="441" alt="Снимок экрана 2026-06-28 в 14 32 20" src="https://github.com/user-attachments/assets/16cad50d-8ef6-4c5a-b850-8e80d477129a" />

<img width="929" height="435" alt="Снимок экрана 2026-06-28 в 14 22 54" src="https://github.com/user-attachments/assets/e8903f41-5734-4783-a8df-8b92c49a010d" />

### Smaller Sample

## Model Calibration. SVI Model

### Low Volatility 

<img width="1215" height="415" alt="Снимок экрана 2026-06-30 в 16 21 39" src="https://github.com/user-attachments/assets/bf755bc5-d233-4809-8cfe-e4545a25f428" />

<img width="1323" height="437" alt="Снимок экрана 2026-06-28 в 16 55 29" src="https://github.com/user-attachments/assets/a198eed5-2cf8-4e6b-b380-94c4793cbf7e" />

<img width="825" height="419" alt="Снимок экрана 2026-06-28 в 16 51 35" src="https://github.com/user-attachments/assets/548b1119-4454-477c-933a-04cc00982874" />

### Moderate Volatilty 

<img width="1204" height="413" alt="Снимок экрана 2026-06-30 в 16 22 50" src="https://github.com/user-attachments/assets/891ea873-3cc8-4bc7-bd80-485d224ff792" />

<img width="1313" height="431" alt="Снимок экрана 2026-06-28 в 16 56 23" src="https://github.com/user-attachments/assets/8cfb4dee-a90d-48cb-8c26-8a4ae9033373" />

<img width="822" height="420" alt="Снимок экрана 2026-06-28 в 16 52 14" src="https://github.com/user-attachments/assets/262f7e78-b908-4ab2-9e08-a4772274b5fb" />

### High Volatitility 

<img width="1222" height="410" alt="Снимок экрана 2026-06-30 в 16 30 17" src="https://github.com/user-attachments/assets/5cd4795d-0c7d-475a-b4d1-59dcd48055c2" />

<img width="1308" height="441" alt="Снимок экрана 2026-06-28 в 16 54 35" src="https://github.com/user-attachments/assets/5e8b36c9-d094-4425-99a9-9fd869c7fa51" />

<img width="825" height="417" alt="Снимок экрана 2026-06-28 в 16 53 07" src="https://github.com/user-attachments/assets/3e5f33dc-7931-4fba-8b74-f478a55c5154" />

# Discussion
