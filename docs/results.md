# Results

Data: 1,585 battery-electric vehicle configurations from 42 manufacturers, model years 2011 to 2027 (EPA file obtained 2026-10-27). Trend figures use model years with at least 10 configurations (2013 to 2027).

1. The median EPA range went from 84 miles in 2013 to 311 miles in 2027. The geometric-mean range changed by +236%, energy per full charge by +243% and consumption by +2%. All of the range gain came from bigger batteries; consumption per mile did not improve.
2. The derived energy per charge passes a sanity check. For the 56 configurations whose battery size EPA lists, the stated capacity is a median 0.89 times the energy drawn from the wall, consistent with charging losses of about 11%.
3. The share of SUVs and pickups among EV configurations went from 14% to 69%. In the regression below an SUV uses 6% more energy per mile than a car of the same model year and motor power, so the shift towards SUVs pushes average consumption up.
4. EVs reverse the usual city/highway pattern. The median EV's highway efficiency is 0.89 times its city efficiency, against 1.37 for gasoline cars. 99.6% of gasoline cars but only 15% of EVs are more efficient on the highway.
5. For the same reference vehicle (two-wheel-drive car, median motor power, model year 2027), predicted consumption ranges from 24.1 kWh/100 mi (Subaru) to 46.1 kWh/100 mi (GMC).
6. On model lines the models had never seen, Gradient boosting had the lowest error (MAE 3.32 kWh/100 mi, 9.1% of the true value), 37% below the class-median baseline.

#### Explanatory regression: log consumption (HC3 robust standard errors)

n = 1530, R² = 0.34

| Term | Effect on consumption | 95% CI | p-value |
|---|---:|---:|---:|
| Class: Pickup (vs car) | +29.5% | [+26.1%, +33.0%] | 0.000 |
| Class: SUV (vs car) | +6.2% | [+4.2%, +8.1%] | 0.000 |
| Class: Van (vs car) | +24.8% | [+4.0%, +49.7%] | 0.017 |
| Model year (+1) | -0.6% | [-0.9%, -0.3%] | 0.000 |
| All-wheel drive | +16.3% | [+13.8%, +18.8%] | 0.000 |
| Motor power (+10%) | +0.3% | [+0.1%, +0.4%] | 0.004 |

#### Predictive models: grouped 5-fold cross-validation by model line

| Model | MAE (kWh/100 mi) | MAPE | R² |
|---|---:|---:|---:|
| Baseline: class median | 5.28 | 14.1% | 0.16 |
| OLS (log scale) | 3.50 | 9.3% | 0.61 |
| Gradient boosting | 3.32 | 9.1% | 0.64 |

## Yearly summary

|   year |   n |   range_q25 |   range_median |   range_q75 |   consumption_median |   energy_median |   share_suv_pickup |   share_awd |
|-------:|----:|------------:|---------------:|------------:|---------------------:|----------------:|-------------------:|------------:|
|   2013 |  14 |       69.75 |           84.5 |      121    |               32     |          24.775 |              0.143 |       0     |
|   2014 |  15 |       78.5  |           84   |      115    |               32     |          25.2   |              0.133 |       0.067 |
|   2015 |  18 |       82.25 |           90   |      253    |               32.5   |          32.273 |              0     |       0.278 |
|   2016 |  31 |       84    |          218   |      258    |               34     |          79.2   |              0.194 |       0.419 |
|   2017 |  30 |       96.5  |          205   |      258.5  |               32.5   |          70.58  |              0.233 |       0.4   |
|   2018 |  24 |      113.25 |          212.5 |      290.5  |               30.501 |          69.409 |              0.167 |       0.333 |
|   2019 |  35 |      153    |          239   |      302.5  |               30.818 |          72.562 |              0.229 |       0.457 |
|   2020 |  38 |      215.75 |          258.5 |      315.75 |               30.313 |          88.218 |              0.316 |       0.579 |
|   2021 |  51 |      211.5  |          239   |      285    |               34.614 |          89.04  |              0.314 |       0.588 |
|   2022 |  89 |      226    |          258   |      312    |               35     |          95.634 |              0.449 |       0.708 |
|   2023 | 144 |      232.75 |          270   |      310.25 |               36.52  |          97.062 |              0.514 |       0.75  |
|   2024 | 266 |      250.25 |          282.5 |      313.75 |               38.393 |         104.388 |              0.632 |       0.752 |
|   2025 | 326 |      258    |          289   |      317    |               38.157 |         110.31  |              0.663 |       0.761 |
|   2026 | 321 |      270    |          295   |      321    |               37.125 |         108.57  |              0.701 |       0.776 |
|   2027 | 171 |      283    |          311   |      348    |               35.175 |         105.649 |              0.69  |       0.813 |

## Range decomposition (geometric means)

|   year |   n |   gm_range |   gm_energy_kwh |   gm_consumption |   range_index |   energy_index |   consumption_index |
|-------:|----:|-----------:|----------------:|-----------------:|--------------:|---------------:|--------------------:|
|   2013 |  14 |      93.51 |           32.35 |            34.59 |        100    |         100    |              100    |
|   2014 |  15 |     101.85 |           34.54 |            33.91 |        108.92 |         106.77 |               98.02 |
|   2015 |  18 |     133.74 |           43.9  |            32.83 |        143.03 |         135.73 |               94.89 |
|   2016 |  31 |     160.65 |           54.42 |            33.87 |        171.81 |         168.24 |               97.92 |
|   2017 |  30 |     161.77 |           52.97 |            32.74 |        173    |         163.76 |               94.66 |
|   2018 |  24 |     171.66 |           54.07 |            31.5  |        183.58 |         167.16 |               91.06 |
|   2019 |  35 |     207.35 |           65.64 |            31.66 |        221.74 |         202.92 |               91.51 |
|   2020 |  38 |     250.59 |           80.78 |            32.24 |        267.98 |         249.75 |               93.2  |
|   2021 |  51 |     236.15 |           82.43 |            34.91 |        252.54 |         254.83 |              100.91 |
|   2022 |  89 |     264.51 |           94.79 |            35.84 |        282.88 |         293.05 |              103.59 |
|   2023 | 144 |     268.92 |           97.87 |            36.39 |        287.59 |         302.56 |              105.2  |
|   2024 | 266 |     281.36 |          107.38 |            38.16 |        300.89 |         331.96 |              110.32 |
|   2025 | 326 |     286.6  |          108.95 |            38.02 |        306.5  |         336.83 |              109.9  |
|   2026 | 321 |     297.68 |          109.07 |            36.64 |        318.35 |         337.21 |              105.92 |
|   2027 | 171 |     314.51 |          110.89 |            35.26 |        336.34 |         342.82 |              101.92 |

## Manufacturer efficiency (reference vehicle)

| make          |   consumption |   ci_low |   ci_high |   n |
|:--------------|--------------:|---------:|----------:|----:|
| Subaru        |         24.08 |    23.29 |     24.89 |  18 |
| Lucid         |         24.46 |    23.81 |     25.14 |  65 |
| Tesla         |         25.48 |    24.74 |     26.24 | 187 |
| Toyota        |         25.55 |    24.48 |     26.67 |  34 |
| Lexus         |         26.39 |    25.48 |     27.33 |  20 |
| Volkswagen    |         27.29 |    26.51 |     28.08 |  34 |
| Hyundai       |         27.62 |    26.55 |     28.74 |  61 |
| Mitsubishi    |         27.67 |    26.27 |     29.15 |   5 |
| Honda         |         27.83 |    26.86 |     28.83 |  14 |
| Volvo         |         28.74 |    27.83 |     29.68 |  45 |
| Fiat          |         28.77 |    27.38 |     30.24 |  13 |
| MINI          |         29.05 |    28.21 |     29.92 |  11 |
| Genesis       |         29.1  |    28.19 |     30.04 |  26 |
| Kia           |         29.27 |    28.24 |     30.33 |  48 |
| Nissan        |         29.8  |    29.04 |     30.59 |  46 |
| Ford          |         29.95 |    29.06 |     30.87 |  63 |
| Chevrolet     |         30.15 |    29.08 |     31.26 |  52 |
| smart         |         30.41 |    28.87 |     32.03 |  16 |
| Cadillac      |         30.75 |    29.79 |     31.75 |  37 |
| Jeep          |         30.77 |    28.07 |     33.74 |   7 |
| Polestar      |         30.84 |    30.05 |     31.64 |  34 |
| BMW           |         31.27 |    30.61 |     31.94 | 146 |
| Audi          |         31.5  |    30.37 |     32.67 |  76 |
| Acura         |         31.68 |    30.09 |     33.35 |   6 |
| Mercedes-Benz |         32.72 |    31.7  |     33.76 |  77 |
| Rivian        |         32.91 |    32    |     33.86 | 187 |
| Jaguar        |         32.94 |    31.18 |     34.8  |   5 |
| Dodge         |         33.67 |    32.11 |     35.3  |  22 |
| Porsche       |         34.31 |    33.4  |     35.25 |  95 |
| Maserati      |         35.03 |    33.28 |     36.88 |  10 |
| Rolls-Royce   |         37.61 |    36.44 |     38.81 |  16 |
| Vinfast       |         37.8  |    36.23 |     39.44 |  13 |
| BYD           |         41.67 |    39.32 |     44.17 |   7 |
| GMC           |         46.15 |    43.05 |     49.47 |  20 |

## Permutation importance

| feature         |   importance |    std |
|:----------------|-------------:|-------:|
| Manufacturer    |       0.068  | 0.0042 |
| All-wheel drive |       0.0258 | 0.0033 |
| Vehicle class   |       0.0168 | 0.0024 |
| Motor power     |       0.0113 | 0.0017 |
| Model year      |       0.0037 | 0.0015 |
