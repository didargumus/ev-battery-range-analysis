# Results

Data: 186 battery-electric vehicle configurations from 20 manufacturers, model years 2011 to 2020 (EPA file obtained October 2019, via the TidyTuesday mirror; replaced by the latest file on the first refresh). Trend figures use model years with at least 10 configurations (2013 to 2019).

1. The median EPA range went from 84 miles in 2013 to 238 miles in 2019. The geometric-mean range changed by +121%, energy per full charge by +105% and consumption by -7%. Bigger batteries account for 90% of the (log) range gain and lower consumption for the remaining 10%.
2. The derived energy per charge passes a sanity check. For the 56 configurations whose battery size EPA lists, the stated capacity is a median 0.89 times the energy drawn from the wall, consistent with charging losses of about 11%.
3. The share of SUVs and pickups among EV configurations went from 14% to 25%. In the regression below an SUV uses 28% more energy per mile than a car of the same model year and motor power, so the shift towards SUVs pushes average consumption up.
4. EVs reverse the usual city/highway pattern. The median EV's highway efficiency is 0.90 times its city efficiency, against 1.38 for gasoline cars. 99.9% of gasoline cars but only 34% of EVs are more efficient on the highway.
5. For the same reference vehicle (two-wheel-drive car, median motor power, model year 2020), predicted consumption ranges from 24.7 kWh/100 mi (Hyundai) to 43.1 kWh/100 mi (BYD).
6. On model lines the models had never seen, OLS (log scale) had the lowest error (MAE 4.33 kWh/100 mi, 12.1% of the true value), 10% below the class-median baseline.

#### Explanatory regression: log consumption (HC3 robust standard errors)

n = 185, R² = 0.47

| Term | Effect on consumption | 95% CI | p-value |
|---|---:|---:|---:|
| Class: SUV (vs car) | +28.1% | [+20.7%, +35.9%] | 0.000 |
| Model year (+1) | -2.9% | [-3.8%, -2.0%] | 0.000 |
| All-wheel drive | +1.6% | [-4.8%, +8.3%] | 0.637 |
| Motor power (+10%) | +0.2% | [-0.2%, +0.6%] | 0.348 |

#### Predictive models: grouped 5-fold cross-validation by model line

| Model | MAE (kWh/100 mi) | MAPE | R² |
|---|---:|---:|---:|
| Baseline: class median | 4.82 | 13.6% | -0.12 |
| OLS (log scale) | 4.33 | 12.1% | 0.05 |
| Gradient boosting | 4.84 | 13.4% | -0.24 |

## Yearly summary

|   year |   n |   range_q25 |   range_median |   range_q75 |   consumption_median |   energy_median |   share_suv_pickup |   share_awd |
|-------:|----:|------------:|---------------:|------------:|---------------------:|----------------:|-------------------:|------------:|
|   2013 |  14 |       69.75 |           84.5 |      121    |               32     |          24.775 |              0.143 |       0     |
|   2014 |  15 |       78.5  |           84   |      115    |               32     |          25.2   |              0.133 |       0.067 |
|   2015 |  18 |       82.25 |           90   |      253    |               32.5   |          32.273 |              0     |       0.278 |
|   2016 |  31 |       84    |          218   |      258    |               34     |          79.2   |              0.194 |       0.419 |
|   2017 |  30 |       96.5  |          205   |      258.5  |               32.5   |          70.58  |              0.233 |       0.4   |
|   2018 |  24 |      113.25 |          212.5 |      290.5  |               30.501 |          69.409 |              0.167 |       0.333 |
|   2019 |  36 |      153    |          238.5 |      298.75 |               30.909 |          76.392 |              0.25  |       0.444 |

## Range decomposition (geometric means)

|   year |   n |   gm_range |   gm_energy_kwh |   gm_consumption |   range_index |   energy_index |   consumption_index |
|-------:|----:|-----------:|----------------:|-----------------:|--------------:|---------------:|--------------------:|
|   2013 |  14 |      93.51 |           32.35 |            34.59 |        100    |         100    |              100    |
|   2014 |  15 |     101.85 |           34.54 |            33.91 |        108.92 |         106.77 |               98.02 |
|   2015 |  18 |     133.74 |           43.9  |            32.83 |        143.03 |         135.73 |               94.89 |
|   2016 |  31 |     160.65 |           54.42 |            33.87 |        171.81 |         168.24 |               97.92 |
|   2017 |  30 |     161.77 |           52.97 |            32.74 |        173    |         163.76 |               94.66 |
|   2018 |  24 |     171.66 |           54.07 |            31.5  |        183.58 |         167.16 |               91.06 |
|   2019 |  36 |     206.75 |           66.16 |            32    |        221.11 |         204.53 |               92.5  |

## Manufacturer efficiency (reference vehicle)

| make       |   consumption |   ci_low |   ci_high |   n |
|:-----------|--------------:|---------:|----------:|----:|
| Hyundai    |         24.69 |    24.01 |     25.38 |   5 |
| Chevrolet  |         26.35 |    25.48 |     27.25 |   6 |
| BMW        |         26.74 |    25.31 |     28.25 |  10 |
| Honda      |         27.59 |    26    |     29.27 |   5 |
| Volkswagen |         28.17 |    26.81 |     29.6  |   6 |
| Fiat       |         28.28 |    26.43 |     30.25 |   7 |
| Tesla      |         28.81 |    26.15 |     31.75 |  77 |
| Nissan     |         28.9  |    27.62 |     30.23 |  12 |
| Mitsubishi |         28.95 |    26.12 |     32.08 |   5 |
| Ford       |         29.07 |    27.8  |     30.4  |   7 |
| Kia        |         30.39 |    29.15 |     31.69 |   7 |
| smart      |         31.99 |    29.39 |     34.82 |  16 |
| BYD        |         43.08 |    40.31 |     46.04 |   8 |

## Permutation importance

| feature         |   importance |    std |
|:----------------|-------------:|-------:|
| Vehicle class   |       0.0118 | 0.0053 |
| Model year      |       0.0058 | 0.0075 |
| All-wheel drive |       0.0022 | 0.0012 |
| Manufacturer    |      -0.0109 | 0.0047 |
| Motor power     |      -0.0319 | 0.0133 |
