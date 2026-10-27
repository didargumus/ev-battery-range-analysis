# Results

Data: 1,585 battery-electric vehicle configurations from 42 manufacturers, model years 2011 to 2027 (EPA file obtained 2026-10-27). Trend figures use model years with at least 10 configurations (2013 to 2027).

1. The median EPA range went from 84 miles in 2013 to 311 miles in 2027. The geometric-mean range changed by +236%, energy per full charge by +243% and consumption by +2%. All of the range gain came from bigger batteries; average consumption per mile did not fall. This hides a real improvement: holding class, drivetrain and motor power fixed, consumption falls 0.6% per model year. The gap comes from the changing mix of vehicles on offer, with more SUVs and pickups, more all-wheel drive and more power.
2. The derived energy per charge passes a sanity check. For the 56 configurations whose battery size EPA lists, the stated capacity is a median 0.89 times the energy drawn from the wall, consistent with charging losses of about 11%.
3. The share of SUVs and pickups among EV configurations went from 14% to 69%. In the regression below an SUV uses 6% more energy per mile than a car of the same model year and motor power, so the shift towards SUVs pushes average consumption up.
4. EVs reverse the usual city/highway pattern. The median EV's highway efficiency is 0.89 times its city efficiency, against 1.37 for gasoline cars. 99.6% of gasoline cars but only 15% of EVs are more efficient on the highway.
5. For the same reference vehicle (all-wheel-drive SUV, 400 kW, model year 2027), predicted consumption ranges from 30.4 kWh/100 mi (Subaru) to 58.2 kWh/100 mi (GMC).
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
| Subaru        |         30.36 |    29.57 |     31.18 |  18 |
| Lucid         |         30.85 |    30.04 |     31.69 |  65 |
| Tesla         |         32.13 |    31.36 |     32.92 | 187 |
| Toyota        |         32.23 |    30.95 |     33.55 |  34 |
| Lexus         |         33.28 |    32.25 |     34.35 |  20 |
| Volkswagen    |         34.41 |    33.58 |     35.27 |  34 |
| Hyundai       |         34.84 |    33.55 |     36.17 |  61 |
| Mitsubishi    |         34.9  |    33.16 |     36.73 |   5 |
| Honda         |         35.09 |    34    |     36.23 |  14 |
| Volvo         |         36.25 |    35.29 |     37.24 |  45 |
| Fiat          |         36.29 |    34.5  |     38.17 |  13 |
| MINI          |         36.64 |    35.67 |     37.63 |  11 |
| Genesis       |         36.7  |    35.76 |     37.67 |  26 |
| Kia           |         36.91 |    35.69 |     38.17 |  48 |
| Nissan        |         37.59 |    36.63 |     38.57 |  46 |
| Ford          |         37.77 |    36.79 |     38.78 |  63 |
| Chevrolet     |         38.03 |    36.75 |     39.35 |  52 |
| smart         |         38.35 |    36.42 |     40.38 |  16 |
| Cadillac      |         38.78 |    37.75 |     39.84 |  37 |
| Jeep          |         38.81 |    35.48 |     42.44 |   7 |
| Polestar      |         38.89 |    37.99 |     39.82 |  34 |
| BMW           |         39.43 |    38.65 |     40.23 | 146 |
| Audi          |         39.72 |    38.39 |     41.1  |  76 |
| Acura         |         39.95 |    38.07 |     41.93 |   6 |
| Mercedes-Benz |         41.26 |    40.05 |     42.51 |  77 |
| Rivian        |         41.51 |    40.66 |     42.38 | 187 |
| Jaguar        |         41.54 |    39.53 |     43.66 |   5 |
| Dodge         |         42.46 |    40.48 |     44.53 |  22 |
| Porsche       |         43.27 |    42.04 |     44.54 |  95 |
| Maserati      |         44.18 |    42.03 |     46.44 |  10 |
| Rolls-Royce   |         47.43 |    45.93 |     48.98 |  16 |
| Vinfast       |         47.68 |    45.76 |     49.67 |  13 |
| BYD           |         52.56 |    49.78 |     55.48 |   7 |
| GMC           |         58.2  |    54.46 |     62.19 |  20 |

## Permutation importance

| feature         |   importance |    std |
|:----------------|-------------:|-------:|
| Manufacturer    |       0.068  | 0.0042 |
| All-wheel drive |       0.0258 | 0.0033 |
| Vehicle class   |       0.0168 | 0.0024 |
| Motor power     |       0.0113 | 0.0017 |
| Model year      |       0.0037 | 0.0015 |
