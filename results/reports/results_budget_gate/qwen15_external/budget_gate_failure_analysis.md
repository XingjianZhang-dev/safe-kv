# Budget Gate Failure Analysis

## Pareto Summary

| target | actual | safe equiv | random mean | percentile | changed+wrong |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.099 | 0.470 | 0.484 | 0.330 | 45 |
| 0.25 | 0.250 | 0.540 | 0.552 | 0.440 | 39 |
| 0.40 | 0.398 | 0.600 | 0.618 | 0.100 | 34 |

# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.410 | 0.499 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.440 | 0.270 | 0.362 | 48 | 0.000 |
| random_gate_budget_0.10_seed000 | 0.460 | 0.290 | 0.382 | 46 | 0.090 |
| random_gate_budget_0.10_seed001 | 0.510 | 0.310 | 0.404 | 41 | 0.097 |
| random_gate_budget_0.10_seed002 | 0.480 | 0.280 | 0.373 | 46 | 0.103 |
| random_gate_budget_0.10_seed003 | 0.500 | 0.290 | 0.379 | 43 | 0.103 |
| random_gate_budget_0.10_seed004 | 0.470 | 0.290 | 0.382 | 45 | 0.091 |
| random_gate_budget_0.10_seed005 | 0.500 | 0.310 | 0.400 | 42 | 0.089 |
| random_gate_budget_0.10_seed006 | 0.500 | 0.310 | 0.410 | 42 | 0.092 |
| random_gate_budget_0.10_seed007 | 0.500 | 0.300 | 0.397 | 42 | 0.092 |
| random_gate_budget_0.10_seed008 | 0.480 | 0.280 | 0.372 | 45 | 0.108 |
| random_gate_budget_0.10_seed009 | 0.480 | 0.290 | 0.384 | 45 | 0.103 |
| random_gate_budget_0.10_seed010 | 0.480 | 0.290 | 0.382 | 44 | 0.097 |
| random_gate_budget_0.10_seed011 | 0.480 | 0.300 | 0.399 | 44 | 0.093 |
| random_gate_budget_0.10_seed012 | 0.480 | 0.290 | 0.383 | 45 | 0.096 |
| random_gate_budget_0.10_seed013 | 0.460 | 0.280 | 0.382 | 46 | 0.103 |
| random_gate_budget_0.10_seed014 | 0.470 | 0.270 | 0.370 | 46 | 0.105 |
| random_gate_budget_0.10_seed015 | 0.500 | 0.290 | 0.380 | 43 | 0.099 |
| random_gate_budget_0.10_seed016 | 0.500 | 0.280 | 0.372 | 43 | 0.087 |
| random_gate_budget_0.10_seed017 | 0.470 | 0.280 | 0.372 | 46 | 0.108 |
| random_gate_budget_0.10_seed018 | 0.470 | 0.280 | 0.372 | 46 | 0.102 |
| random_gate_budget_0.10_seed019 | 0.500 | 0.290 | 0.386 | 43 | 0.099 |
| random_gate_budget_0.10_seed020 | 0.460 | 0.290 | 0.382 | 46 | 0.091 |
| random_gate_budget_0.10_seed021 | 0.480 | 0.280 | 0.372 | 44 | 0.097 |
| random_gate_budget_0.10_seed022 | 0.470 | 0.300 | 0.392 | 45 | 0.097 |
| random_gate_budget_0.10_seed023 | 0.490 | 0.260 | 0.360 | 46 | 0.098 |
| random_gate_budget_0.10_seed024 | 0.500 | 0.260 | 0.355 | 45 | 0.097 |
| random_gate_budget_0.10_seed025 | 0.500 | 0.270 | 0.362 | 44 | 0.103 |
| random_gate_budget_0.10_seed026 | 0.450 | 0.290 | 0.382 | 46 | 0.097 |
| random_gate_budget_0.10_seed027 | 0.500 | 0.290 | 0.372 | 43 | 0.100 |
| random_gate_budget_0.10_seed028 | 0.500 | 0.280 | 0.361 | 44 | 0.095 |
| random_gate_budget_0.10_seed029 | 0.500 | 0.290 | 0.376 | 43 | 0.108 |
| random_gate_budget_0.10_seed030 | 0.500 | 0.280 | 0.371 | 44 | 0.096 |
| random_gate_budget_0.10_seed031 | 0.470 | 0.260 | 0.359 | 47 | 0.104 |
| random_gate_budget_0.10_seed032 | 0.500 | 0.310 | 0.402 | 42 | 0.090 |
| random_gate_budget_0.10_seed033 | 0.480 | 0.280 | 0.367 | 45 | 0.103 |
| random_gate_budget_0.10_seed034 | 0.480 | 0.280 | 0.374 | 45 | 0.094 |
| random_gate_budget_0.10_seed035 | 0.510 | 0.300 | 0.389 | 41 | 0.107 |
| random_gate_budget_0.10_seed036 | 0.490 | 0.250 | 0.342 | 46 | 0.101 |
| random_gate_budget_0.10_seed037 | 0.510 | 0.270 | 0.368 | 43 | 0.096 |
| random_gate_budget_0.10_seed038 | 0.520 | 0.320 | 0.411 | 41 | 0.112 |
| random_gate_budget_0.10_seed039 | 0.480 | 0.280 | 0.362 | 44 | 0.104 |
| random_gate_budget_0.10_seed040 | 0.490 | 0.300 | 0.392 | 43 | 0.087 |
| random_gate_budget_0.10_seed041 | 0.460 | 0.290 | 0.382 | 46 | 0.099 |
| random_gate_budget_0.10_seed042 | 0.490 | 0.280 | 0.366 | 45 | 0.091 |
| random_gate_budget_0.10_seed043 | 0.480 | 0.290 | 0.389 | 44 | 0.107 |
| random_gate_budget_0.10_seed044 | 0.490 | 0.280 | 0.387 | 44 | 0.105 |
| random_gate_budget_0.10_seed045 | 0.470 | 0.290 | 0.385 | 45 | 0.097 |
| random_gate_budget_0.10_seed046 | 0.460 | 0.280 | 0.375 | 46 | 0.095 |
| random_gate_budget_0.10_seed047 | 0.470 | 0.270 | 0.371 | 46 | 0.102 |
| random_gate_budget_0.10_seed048 | 0.490 | 0.270 | 0.370 | 45 | 0.098 |
| random_gate_budget_0.10_seed049 | 0.490 | 0.310 | 0.391 | 42 | 0.114 |
| random_gate_budget_0.10_seed050 | 0.460 | 0.270 | 0.356 | 47 | 0.105 |
| random_gate_budget_0.10_seed051 | 0.500 | 0.280 | 0.374 | 45 | 0.096 |
| random_gate_budget_0.10_seed052 | 0.500 | 0.290 | 0.385 | 43 | 0.099 |
| random_gate_budget_0.10_seed053 | 0.480 | 0.280 | 0.367 | 45 | 0.090 |
| random_gate_budget_0.10_seed054 | 0.480 | 0.270 | 0.369 | 46 | 0.106 |
| random_gate_budget_0.10_seed055 | 0.490 | 0.280 | 0.372 | 44 | 0.099 |
| random_gate_budget_0.10_seed056 | 0.460 | 0.270 | 0.357 | 47 | 0.092 |
| random_gate_budget_0.10_seed057 | 0.450 | 0.300 | 0.392 | 46 | 0.094 |
| random_gate_budget_0.10_seed058 | 0.460 | 0.290 | 0.382 | 46 | 0.111 |
| random_gate_budget_0.10_seed059 | 0.490 | 0.270 | 0.360 | 45 | 0.115 |
| random_gate_budget_0.10_seed060 | 0.460 | 0.300 | 0.381 | 45 | 0.099 |
| random_gate_budget_0.10_seed061 | 0.450 | 0.280 | 0.376 | 47 | 0.105 |
| random_gate_budget_0.10_seed062 | 0.480 | 0.270 | 0.370 | 45 | 0.100 |
| random_gate_budget_0.10_seed063 | 0.510 | 0.280 | 0.373 | 43 | 0.111 |
| random_gate_budget_0.10_seed064 | 0.480 | 0.280 | 0.372 | 45 | 0.104 |
| random_gate_budget_0.10_seed065 | 0.500 | 0.280 | 0.372 | 44 | 0.098 |
| random_gate_budget_0.10_seed066 | 0.500 | 0.290 | 0.377 | 43 | 0.107 |
| random_gate_budget_0.10_seed067 | 0.510 | 0.270 | 0.357 | 43 | 0.107 |
| random_gate_budget_0.10_seed068 | 0.480 | 0.250 | 0.348 | 47 | 0.096 |
| random_gate_budget_0.10_seed069 | 0.470 | 0.280 | 0.367 | 46 | 0.104 |
| random_gate_budget_0.10_seed070 | 0.490 | 0.270 | 0.370 | 44 | 0.103 |
| random_gate_budget_0.10_seed071 | 0.490 | 0.270 | 0.362 | 45 | 0.091 |
| random_gate_budget_0.10_seed072 | 0.470 | 0.250 | 0.346 | 47 | 0.105 |
| random_gate_budget_0.10_seed073 | 0.470 | 0.300 | 0.400 | 44 | 0.095 |
| random_gate_budget_0.10_seed074 | 0.480 | 0.280 | 0.383 | 44 | 0.089 |
| random_gate_budget_0.10_seed075 | 0.480 | 0.310 | 0.397 | 43 | 0.101 |
| random_gate_budget_0.10_seed076 | 0.510 | 0.300 | 0.386 | 42 | 0.102 |
| random_gate_budget_0.10_seed077 | 0.460 | 0.300 | 0.387 | 45 | 0.100 |
| random_gate_budget_0.10_seed078 | 0.510 | 0.290 | 0.379 | 42 | 0.106 |
| random_gate_budget_0.10_seed079 | 0.470 | 0.290 | 0.386 | 45 | 0.094 |
| random_gate_budget_0.10_seed080 | 0.450 | 0.280 | 0.371 | 47 | 0.107 |
| random_gate_budget_0.10_seed081 | 0.470 | 0.290 | 0.371 | 45 | 0.092 |
| random_gate_budget_0.10_seed082 | 0.500 | 0.300 | 0.395 | 42 | 0.084 |
| random_gate_budget_0.10_seed083 | 0.460 | 0.300 | 0.386 | 45 | 0.095 |
| random_gate_budget_0.10_seed084 | 0.520 | 0.310 | 0.413 | 40 | 0.100 |
| random_gate_budget_0.10_seed085 | 0.460 | 0.250 | 0.353 | 48 | 0.108 |
| random_gate_budget_0.10_seed086 | 0.470 | 0.260 | 0.359 | 47 | 0.095 |
| random_gate_budget_0.10_seed087 | 0.470 | 0.280 | 0.367 | 46 | 0.104 |
| random_gate_budget_0.10_seed088 | 0.480 | 0.270 | 0.369 | 45 | 0.102 |
| random_gate_budget_0.10_seed089 | 0.510 | 0.320 | 0.396 | 42 | 0.114 |
| random_gate_budget_0.10_seed090 | 0.490 | 0.310 | 0.402 | 43 | 0.095 |
| random_gate_budget_0.10_seed091 | 0.530 | 0.290 | 0.376 | 41 | 0.109 |
| random_gate_budget_0.10_seed092 | 0.490 | 0.280 | 0.380 | 43 | 0.101 |
| random_gate_budget_0.10_seed093 | 0.450 | 0.300 | 0.387 | 45 | 0.112 |
| random_gate_budget_0.10_seed094 | 0.470 | 0.300 | 0.395 | 44 | 0.105 |
| random_gate_budget_0.10_seed095 | 0.510 | 0.270 | 0.358 | 43 | 0.100 |
| random_gate_budget_0.10_seed096 | 0.480 | 0.260 | 0.352 | 46 | 0.102 |
| random_gate_budget_0.10_seed097 | 0.480 | 0.290 | 0.388 | 44 | 0.110 |
| random_gate_budget_0.10_seed098 | 0.520 | 0.320 | 0.409 | 40 | 0.100 |
| random_gate_budget_0.10_seed099 | 0.490 | 0.290 | 0.376 | 44 | 0.112 |
| random_gate_budget_0.25_seed000 | 0.520 | 0.340 | 0.430 | 40 | 0.236 |
| random_gate_budget_0.25_seed001 | 0.560 | 0.300 | 0.400 | 39 | 0.244 |
| random_gate_budget_0.25_seed002 | 0.560 | 0.310 | 0.405 | 39 | 0.254 |
| random_gate_budget_0.25_seed003 | 0.580 | 0.310 | 0.407 | 36 | 0.258 |
| random_gate_budget_0.25_seed004 | 0.510 | 0.290 | 0.380 | 42 | 0.249 |
| random_gate_budget_0.25_seed005 | 0.610 | 0.330 | 0.428 | 34 | 0.246 |
| random_gate_budget_0.25_seed006 | 0.570 | 0.330 | 0.437 | 36 | 0.252 |
| random_gate_budget_0.25_seed007 | 0.530 | 0.300 | 0.401 | 40 | 0.252 |
| random_gate_budget_0.25_seed008 | 0.540 | 0.280 | 0.372 | 42 | 0.255 |
| random_gate_budget_0.25_seed009 | 0.530 | 0.320 | 0.407 | 41 | 0.261 |
| random_gate_budget_0.25_seed010 | 0.560 | 0.310 | 0.398 | 39 | 0.259 |
| random_gate_budget_0.25_seed011 | 0.570 | 0.330 | 0.429 | 36 | 0.245 |
| random_gate_budget_0.25_seed012 | 0.540 | 0.290 | 0.385 | 40 | 0.247 |
| random_gate_budget_0.25_seed013 | 0.530 | 0.330 | 0.421 | 39 | 0.251 |
| random_gate_budget_0.25_seed014 | 0.520 | 0.290 | 0.385 | 41 | 0.258 |
| random_gate_budget_0.25_seed015 | 0.570 | 0.330 | 0.420 | 37 | 0.243 |
| random_gate_budget_0.25_seed016 | 0.540 | 0.310 | 0.399 | 39 | 0.236 |
| random_gate_budget_0.25_seed017 | 0.500 | 0.300 | 0.387 | 43 | 0.260 |
| random_gate_budget_0.25_seed018 | 0.540 | 0.290 | 0.399 | 40 | 0.245 |
| random_gate_budget_0.25_seed019 | 0.610 | 0.290 | 0.398 | 36 | 0.257 |
| random_gate_budget_0.25_seed020 | 0.550 | 0.330 | 0.420 | 38 | 0.252 |
| random_gate_budget_0.25_seed021 | 0.570 | 0.300 | 0.399 | 38 | 0.245 |
| random_gate_budget_0.25_seed022 | 0.570 | 0.290 | 0.403 | 39 | 0.255 |
| random_gate_budget_0.25_seed023 | 0.570 | 0.320 | 0.415 | 38 | 0.243 |
| random_gate_budget_0.25_seed024 | 0.520 | 0.290 | 0.380 | 41 | 0.252 |
| random_gate_budget_0.25_seed025 | 0.560 | 0.290 | 0.396 | 40 | 0.249 |
| random_gate_budget_0.25_seed026 | 0.530 | 0.280 | 0.377 | 42 | 0.261 |
| random_gate_budget_0.25_seed027 | 0.560 | 0.290 | 0.384 | 39 | 0.259 |
| random_gate_budget_0.25_seed028 | 0.570 | 0.300 | 0.387 | 39 | 0.258 |
| random_gate_budget_0.25_seed029 | 0.590 | 0.300 | 0.403 | 37 | 0.255 |
| random_gate_budget_0.25_seed030 | 0.560 | 0.320 | 0.407 | 38 | 0.262 |
| random_gate_budget_0.25_seed031 | 0.510 | 0.300 | 0.403 | 42 | 0.248 |
| random_gate_budget_0.25_seed032 | 0.600 | 0.310 | 0.414 | 35 | 0.244 |
| random_gate_budget_0.25_seed033 | 0.550 | 0.290 | 0.386 | 40 | 0.256 |
| random_gate_budget_0.25_seed034 | 0.540 | 0.310 | 0.399 | 39 | 0.259 |
| random_gate_budget_0.25_seed035 | 0.570 | 0.320 | 0.416 | 36 | 0.251 |
| random_gate_budget_0.25_seed036 | 0.550 | 0.300 | 0.388 | 40 | 0.255 |
| random_gate_budget_0.25_seed037 | 0.590 | 0.280 | 0.380 | 38 | 0.257 |
| random_gate_budget_0.25_seed038 | 0.580 | 0.320 | 0.420 | 37 | 0.258 |
| random_gate_budget_0.25_seed039 | 0.530 | 0.300 | 0.386 | 40 | 0.255 |
| random_gate_budget_0.25_seed040 | 0.590 | 0.360 | 0.440 | 34 | 0.243 |
| random_gate_budget_0.25_seed041 | 0.540 | 0.330 | 0.437 | 38 | 0.243 |
| random_gate_budget_0.25_seed042 | 0.580 | 0.300 | 0.398 | 38 | 0.257 |
| random_gate_budget_0.25_seed043 | 0.600 | 0.320 | 0.421 | 34 | 0.259 |
| random_gate_budget_0.25_seed044 | 0.540 | 0.290 | 0.391 | 40 | 0.261 |
| random_gate_budget_0.25_seed045 | 0.520 | 0.300 | 0.398 | 41 | 0.257 |
| random_gate_budget_0.25_seed046 | 0.510 | 0.320 | 0.413 | 40 | 0.254 |
| random_gate_budget_0.25_seed047 | 0.550 | 0.300 | 0.408 | 39 | 0.257 |
| random_gate_budget_0.25_seed048 | 0.510 | 0.290 | 0.385 | 42 | 0.265 |
| random_gate_budget_0.25_seed049 | 0.540 | 0.340 | 0.416 | 38 | 0.255 |
| random_gate_budget_0.25_seed050 | 0.540 | 0.330 | 0.418 | 38 | 0.264 |
| random_gate_budget_0.25_seed051 | 0.580 | 0.310 | 0.408 | 37 | 0.238 |
| random_gate_budget_0.25_seed052 | 0.520 | 0.310 | 0.413 | 41 | 0.241 |
| random_gate_budget_0.25_seed053 | 0.530 | 0.300 | 0.396 | 40 | 0.252 |
| random_gate_budget_0.25_seed054 | 0.570 | 0.310 | 0.396 | 38 | 0.250 |
| random_gate_budget_0.25_seed055 | 0.560 | 0.340 | 0.429 | 36 | 0.263 |
| random_gate_budget_0.25_seed056 | 0.510 | 0.320 | 0.401 | 41 | 0.250 |
| random_gate_budget_0.25_seed057 | 0.530 | 0.320 | 0.419 | 39 | 0.257 |
| random_gate_budget_0.25_seed058 | 0.540 | 0.300 | 0.391 | 40 | 0.257 |
| random_gate_budget_0.25_seed059 | 0.520 | 0.300 | 0.391 | 42 | 0.266 |
| random_gate_budget_0.25_seed060 | 0.540 | 0.350 | 0.434 | 37 | 0.244 |
| random_gate_budget_0.25_seed061 | 0.520 | 0.310 | 0.404 | 41 | 0.252 |
| random_gate_budget_0.25_seed062 | 0.560 | 0.320 | 0.419 | 37 | 0.258 |
| random_gate_budget_0.25_seed063 | 0.560 | 0.300 | 0.394 | 39 | 0.264 |
| random_gate_budget_0.25_seed064 | 0.540 | 0.300 | 0.386 | 40 | 0.255 |
| random_gate_budget_0.25_seed065 | 0.570 | 0.280 | 0.381 | 40 | 0.254 |
| random_gate_budget_0.25_seed066 | 0.550 | 0.290 | 0.377 | 41 | 0.256 |
| random_gate_budget_0.25_seed067 | 0.570 | 0.300 | 0.386 | 38 | 0.248 |
| random_gate_budget_0.25_seed068 | 0.530 | 0.260 | 0.368 | 42 | 0.251 |
| random_gate_budget_0.25_seed069 | 0.570 | 0.300 | 0.389 | 39 | 0.258 |
| random_gate_budget_0.25_seed070 | 0.540 | 0.290 | 0.387 | 40 | 0.244 |
| random_gate_budget_0.25_seed071 | 0.590 | 0.300 | 0.396 | 36 | 0.246 |
| random_gate_budget_0.25_seed072 | 0.540 | 0.260 | 0.366 | 42 | 0.250 |
| random_gate_budget_0.25_seed073 | 0.570 | 0.290 | 0.394 | 38 | 0.238 |
| random_gate_budget_0.25_seed074 | 0.560 | 0.310 | 0.412 | 38 | 0.245 |
| random_gate_budget_0.25_seed075 | 0.570 | 0.350 | 0.439 | 36 | 0.240 |
| random_gate_budget_0.25_seed076 | 0.560 | 0.320 | 0.417 | 37 | 0.243 |
| random_gate_budget_0.25_seed077 | 0.520 | 0.310 | 0.410 | 40 | 0.260 |
| random_gate_budget_0.25_seed078 | 0.570 | 0.280 | 0.371 | 39 | 0.259 |
| random_gate_budget_0.25_seed079 | 0.550 | 0.310 | 0.403 | 38 | 0.246 |
| random_gate_budget_0.25_seed080 | 0.550 | 0.330 | 0.420 | 39 | 0.256 |
| random_gate_budget_0.25_seed081 | 0.530 | 0.330 | 0.417 | 38 | 0.241 |
| random_gate_budget_0.25_seed082 | 0.540 | 0.310 | 0.413 | 39 | 0.242 |
| random_gate_budget_0.25_seed083 | 0.540 | 0.330 | 0.409 | 38 | 0.232 |
| random_gate_budget_0.25_seed084 | 0.560 | 0.340 | 0.436 | 36 | 0.243 |
| random_gate_budget_0.25_seed085 | 0.560 | 0.280 | 0.393 | 39 | 0.262 |
| random_gate_budget_0.25_seed086 | 0.540 | 0.290 | 0.381 | 41 | 0.257 |
| random_gate_budget_0.25_seed087 | 0.540 | 0.310 | 0.399 | 39 | 0.247 |
| random_gate_budget_0.25_seed088 | 0.550 | 0.300 | 0.399 | 39 | 0.247 |
| random_gate_budget_0.25_seed089 | 0.560 | 0.330 | 0.409 | 38 | 0.245 |
| random_gate_budget_0.25_seed090 | 0.560 | 0.310 | 0.412 | 38 | 0.252 |
| random_gate_budget_0.25_seed091 | 0.570 | 0.310 | 0.411 | 37 | 0.249 |
| random_gate_budget_0.25_seed092 | 0.560 | 0.280 | 0.377 | 39 | 0.252 |
| random_gate_budget_0.25_seed093 | 0.520 | 0.310 | 0.405 | 40 | 0.249 |
| random_gate_budget_0.25_seed094 | 0.530 | 0.320 | 0.422 | 39 | 0.255 |
| random_gate_budget_0.25_seed095 | 0.600 | 0.330 | 0.421 | 34 | 0.260 |
| random_gate_budget_0.25_seed096 | 0.550 | 0.290 | 0.390 | 40 | 0.245 |
| random_gate_budget_0.25_seed097 | 0.540 | 0.300 | 0.400 | 40 | 0.257 |
| random_gate_budget_0.25_seed098 | 0.560 | 0.330 | 0.428 | 37 | 0.242 |
| random_gate_budget_0.25_seed099 | 0.580 | 0.310 | 0.406 | 37 | 0.262 |
| random_gate_budget_0.40_seed000 | 0.630 | 0.330 | 0.427 | 33 | 0.398 |
| random_gate_budget_0.40_seed001 | 0.600 | 0.320 | 0.423 | 35 | 0.397 |
| random_gate_budget_0.40_seed002 | 0.620 | 0.340 | 0.437 | 33 | 0.402 |
| random_gate_budget_0.40_seed003 | 0.630 | 0.340 | 0.442 | 32 | 0.403 |
| random_gate_budget_0.40_seed004 | 0.620 | 0.330 | 0.423 | 33 | 0.402 |
| random_gate_budget_0.40_seed005 | 0.620 | 0.350 | 0.447 | 32 | 0.403 |
| random_gate_budget_0.40_seed006 | 0.630 | 0.340 | 0.437 | 32 | 0.402 |
| random_gate_budget_0.40_seed007 | 0.630 | 0.350 | 0.441 | 31 | 0.404 |
| random_gate_budget_0.40_seed008 | 0.610 | 0.330 | 0.427 | 34 | 0.403 |
| random_gate_budget_0.40_seed009 | 0.620 | 0.340 | 0.437 | 33 | 0.405 |
| random_gate_budget_0.40_seed010 | 0.620 | 0.330 | 0.427 | 33 | 0.405 |
| random_gate_budget_0.40_seed011 | 0.630 | 0.340 | 0.442 | 32 | 0.397 |
| random_gate_budget_0.40_seed012 | 0.630 | 0.320 | 0.422 | 33 | 0.403 |
| random_gate_budget_0.40_seed013 | 0.610 | 0.320 | 0.417 | 34 | 0.403 |
| random_gate_budget_0.40_seed014 | 0.620 | 0.350 | 0.447 | 32 | 0.404 |
| random_gate_budget_0.40_seed015 | 0.620 | 0.340 | 0.430 | 33 | 0.404 |
| random_gate_budget_0.40_seed016 | 0.620 | 0.320 | 0.417 | 34 | 0.390 |
| random_gate_budget_0.40_seed017 | 0.610 | 0.320 | 0.413 | 35 | 0.396 |
| random_gate_budget_0.40_seed018 | 0.600 | 0.330 | 0.438 | 34 | 0.399 |
| random_gate_budget_0.40_seed019 | 0.620 | 0.330 | 0.433 | 33 | 0.398 |
| random_gate_budget_0.40_seed020 | 0.610 | 0.340 | 0.428 | 33 | 0.405 |
| random_gate_budget_0.40_seed021 | 0.610 | 0.330 | 0.425 | 35 | 0.405 |
| random_gate_budget_0.40_seed022 | 0.620 | 0.340 | 0.437 | 33 | 0.404 |
| random_gate_budget_0.40_seed023 | 0.620 | 0.330 | 0.432 | 33 | 0.403 |
| random_gate_budget_0.40_seed024 | 0.630 | 0.340 | 0.437 | 32 | 0.408 |
| random_gate_budget_0.40_seed025 | 0.620 | 0.340 | 0.435 | 33 | 0.407 |
| random_gate_budget_0.40_seed026 | 0.600 | 0.320 | 0.414 | 35 | 0.408 |
| random_gate_budget_0.40_seed027 | 0.610 | 0.320 | 0.417 | 34 | 0.399 |
| random_gate_budget_0.40_seed028 | 0.620 | 0.330 | 0.427 | 33 | 0.404 |
| random_gate_budget_0.40_seed029 | 0.620 | 0.330 | 0.427 | 33 | 0.399 |
| random_gate_budget_0.40_seed030 | 0.620 | 0.330 | 0.427 | 33 | 0.410 |
| random_gate_budget_0.40_seed031 | 0.620 | 0.330 | 0.428 | 33 | 0.403 |
| random_gate_budget_0.40_seed032 | 0.620 | 0.330 | 0.423 | 33 | 0.402 |
| random_gate_budget_0.40_seed033 | 0.610 | 0.330 | 0.427 | 34 | 0.406 |
| random_gate_budget_0.40_seed034 | 0.610 | 0.340 | 0.437 | 33 | 0.398 |
| random_gate_budget_0.40_seed035 | 0.590 | 0.350 | 0.441 | 33 | 0.398 |
| random_gate_budget_0.40_seed036 | 0.620 | 0.350 | 0.447 | 32 | 0.399 |
| random_gate_budget_0.40_seed037 | 0.620 | 0.330 | 0.427 | 33 | 0.400 |
| random_gate_budget_0.40_seed038 | 0.610 | 0.340 | 0.435 | 34 | 0.408 |
| random_gate_budget_0.40_seed039 | 0.610 | 0.330 | 0.419 | 34 | 0.404 |
| random_gate_budget_0.40_seed040 | 0.640 | 0.330 | 0.427 | 32 | 0.402 |
| random_gate_budget_0.40_seed041 | 0.610 | 0.350 | 0.447 | 33 | 0.408 |
| random_gate_budget_0.40_seed042 | 0.620 | 0.340 | 0.435 | 33 | 0.407 |
| random_gate_budget_0.40_seed043 | 0.630 | 0.340 | 0.437 | 32 | 0.401 |
| random_gate_budget_0.40_seed044 | 0.630 | 0.340 | 0.437 | 32 | 0.400 |
| random_gate_budget_0.40_seed045 | 0.620 | 0.320 | 0.413 | 34 | 0.397 |
| random_gate_budget_0.40_seed046 | 0.610 | 0.340 | 0.442 | 33 | 0.399 |
| random_gate_budget_0.40_seed047 | 0.600 | 0.330 | 0.427 | 34 | 0.401 |
| random_gate_budget_0.40_seed048 | 0.620 | 0.340 | 0.437 | 33 | 0.407 |
| random_gate_budget_0.40_seed049 | 0.620 | 0.330 | 0.427 | 33 | 0.395 |
| random_gate_budget_0.40_seed050 | 0.620 | 0.340 | 0.435 | 33 | 0.409 |
| random_gate_budget_0.40_seed051 | 0.630 | 0.340 | 0.437 | 32 | 0.399 |
| random_gate_budget_0.40_seed052 | 0.620 | 0.330 | 0.427 | 33 | 0.398 |
| random_gate_budget_0.40_seed053 | 0.630 | 0.340 | 0.437 | 32 | 0.410 |
| random_gate_budget_0.40_seed054 | 0.610 | 0.330 | 0.423 | 34 | 0.399 |
| random_gate_budget_0.40_seed055 | 0.630 | 0.350 | 0.437 | 31 | 0.403 |
| random_gate_budget_0.40_seed056 | 0.630 | 0.340 | 0.434 | 32 | 0.401 |
| random_gate_budget_0.40_seed057 | 0.630 | 0.340 | 0.442 | 32 | 0.399 |
| random_gate_budget_0.40_seed058 | 0.620 | 0.340 | 0.429 | 33 | 0.403 |
| random_gate_budget_0.40_seed059 | 0.620 | 0.340 | 0.433 | 33 | 0.400 |
| random_gate_budget_0.40_seed060 | 0.620 | 0.340 | 0.431 | 32 | 0.403 |
| random_gate_budget_0.40_seed061 | 0.610 | 0.320 | 0.417 | 34 | 0.400 |
| random_gate_budget_0.40_seed062 | 0.620 | 0.330 | 0.427 | 33 | 0.402 |
| random_gate_budget_0.40_seed063 | 0.600 | 0.310 | 0.412 | 35 | 0.400 |
| random_gate_budget_0.40_seed064 | 0.620 | 0.330 | 0.433 | 33 | 0.407 |
| random_gate_budget_0.40_seed065 | 0.640 | 0.320 | 0.417 | 33 | 0.394 |
| random_gate_budget_0.40_seed066 | 0.610 | 0.320 | 0.417 | 34 | 0.404 |
| random_gate_budget_0.40_seed067 | 0.620 | 0.320 | 0.417 | 34 | 0.402 |
| random_gate_budget_0.40_seed068 | 0.620 | 0.330 | 0.427 | 33 | 0.404 |
| random_gate_budget_0.40_seed069 | 0.600 | 0.320 | 0.417 | 35 | 0.402 |
| random_gate_budget_0.40_seed070 | 0.600 | 0.330 | 0.426 | 34 | 0.397 |
| random_gate_budget_0.40_seed071 | 0.630 | 0.350 | 0.441 | 31 | 0.404 |
| random_gate_budget_0.40_seed072 | 0.620 | 0.330 | 0.427 | 33 | 0.403 |
| random_gate_budget_0.40_seed073 | 0.610 | 0.320 | 0.423 | 34 | 0.398 |
| random_gate_budget_0.40_seed074 | 0.610 | 0.330 | 0.433 | 34 | 0.406 |
| random_gate_budget_0.40_seed075 | 0.630 | 0.340 | 0.437 | 32 | 0.397 |
| random_gate_budget_0.40_seed076 | 0.630 | 0.340 | 0.433 | 32 | 0.402 |
| random_gate_budget_0.40_seed077 | 0.610 | 0.320 | 0.417 | 34 | 0.401 |
| random_gate_budget_0.40_seed078 | 0.620 | 0.330 | 0.423 | 33 | 0.403 |
| random_gate_budget_0.40_seed079 | 0.630 | 0.340 | 0.437 | 32 | 0.397 |
| random_gate_budget_0.40_seed080 | 0.620 | 0.340 | 0.437 | 33 | 0.406 |
| random_gate_budget_0.40_seed081 | 0.600 | 0.330 | 0.427 | 34 | 0.404 |
| random_gate_budget_0.40_seed082 | 0.610 | 0.330 | 0.427 | 34 | 0.400 |
| random_gate_budget_0.40_seed083 | 0.630 | 0.340 | 0.437 | 32 | 0.402 |
| random_gate_budget_0.40_seed084 | 0.620 | 0.330 | 0.432 | 33 | 0.396 |
| random_gate_budget_0.40_seed085 | 0.630 | 0.340 | 0.437 | 32 | 0.408 |
| random_gate_budget_0.40_seed086 | 0.610 | 0.330 | 0.428 | 34 | 0.406 |
| random_gate_budget_0.40_seed087 | 0.620 | 0.330 | 0.427 | 33 | 0.406 |
| random_gate_budget_0.40_seed088 | 0.610 | 0.340 | 0.438 | 33 | 0.403 |
| random_gate_budget_0.40_seed089 | 0.610 | 0.340 | 0.437 | 34 | 0.403 |
| random_gate_budget_0.40_seed090 | 0.610 | 0.330 | 0.419 | 34 | 0.411 |
| random_gate_budget_0.40_seed091 | 0.620 | 0.330 | 0.432 | 33 | 0.402 |
| random_gate_budget_0.40_seed092 | 0.630 | 0.330 | 0.427 | 33 | 0.401 |
| random_gate_budget_0.40_seed093 | 0.620 | 0.350 | 0.447 | 32 | 0.401 |
| random_gate_budget_0.40_seed094 | 0.620 | 0.330 | 0.429 | 33 | 0.402 |
| random_gate_budget_0.40_seed095 | 0.620 | 0.350 | 0.447 | 32 | 0.408 |
| random_gate_budget_0.40_seed096 | 0.600 | 0.330 | 0.419 | 35 | 0.402 |
| random_gate_budget_0.40_seed097 | 0.620 | 0.330 | 0.427 | 33 | 0.408 |
| random_gate_budget_0.40_seed098 | 0.620 | 0.340 | 0.437 | 33 | 0.402 |
| random_gate_budget_0.40_seed099 | 0.630 | 0.340 | 0.437 | 32 | 0.399 |
| risk_guided_doc_patch_k2 | 0.630 | 0.340 | 0.437 | 32 | 0.428 |
| safe_gate_budget_0.10 | 0.470 | 0.290 | 0.382 | 45 | 0.104 |
| safe_gate_budget_0.25 | 0.540 | 0.320 | 0.404 | 39 | 0.241 |
| safe_gate_budget_0.40 | 0.600 | 0.330 | 0.427 | 34 | 0.396 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_2wiki | 1.000 | 0.300 | 0 |
| full_prefill::external_hotpotqa | 1.000 | 0.520 | 0 |
| prefix_conditioned_naive_global::external_2wiki | 0.480 | 0.200 | 22 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.400 | 0.340 | 26 |
| random_gate_budget_0.10_seed000::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed000::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed001::external_2wiki | 0.560 | 0.220 | 18 |
| random_gate_budget_0.10_seed001::external_hotpotqa | 0.460 | 0.400 | 23 |
| random_gate_budget_0.10_seed002::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed002::external_hotpotqa | 0.460 | 0.340 | 25 |
| random_gate_budget_0.10_seed003::external_2wiki | 0.520 | 0.240 | 19 |
| random_gate_budget_0.10_seed003::external_hotpotqa | 0.480 | 0.340 | 24 |
| random_gate_budget_0.10_seed004::external_2wiki | 0.480 | 0.240 | 21 |
| random_gate_budget_0.10_seed004::external_hotpotqa | 0.460 | 0.340 | 24 |
| random_gate_budget_0.10_seed005::external_2wiki | 0.580 | 0.260 | 17 |
| random_gate_budget_0.10_seed005::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed006::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed006::external_hotpotqa | 0.500 | 0.400 | 21 |
| random_gate_budget_0.10_seed007::external_2wiki | 0.540 | 0.240 | 19 |
| random_gate_budget_0.10_seed007::external_hotpotqa | 0.460 | 0.360 | 23 |
| random_gate_budget_0.10_seed008::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed008::external_hotpotqa | 0.460 | 0.340 | 24 |
| random_gate_budget_0.10_seed009::external_2wiki | 0.520 | 0.240 | 20 |
| random_gate_budget_0.10_seed009::external_hotpotqa | 0.440 | 0.340 | 25 |
| random_gate_budget_0.10_seed010::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed010::external_hotpotqa | 0.480 | 0.380 | 22 |
| random_gate_budget_0.10_seed011::external_2wiki | 0.520 | 0.240 | 19 |
| random_gate_budget_0.10_seed011::external_hotpotqa | 0.440 | 0.360 | 25 |
| random_gate_budget_0.10_seed012::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed012::external_hotpotqa | 0.460 | 0.360 | 24 |
| random_gate_budget_0.10_seed013::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.10_seed013::external_hotpotqa | 0.460 | 0.340 | 24 |
| random_gate_budget_0.10_seed014::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed014::external_hotpotqa | 0.440 | 0.320 | 25 |
| random_gate_budget_0.10_seed015::external_2wiki | 0.540 | 0.220 | 19 |
| random_gate_budget_0.10_seed015::external_hotpotqa | 0.460 | 0.360 | 24 |
| random_gate_budget_0.10_seed016::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed016::external_hotpotqa | 0.520 | 0.360 | 21 |
| random_gate_budget_0.10_seed017::external_2wiki | 0.520 | 0.200 | 21 |
| random_gate_budget_0.10_seed017::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed018::external_2wiki | 0.520 | 0.200 | 21 |
| random_gate_budget_0.10_seed018::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed019::external_2wiki | 0.560 | 0.220 | 19 |
| random_gate_budget_0.10_seed019::external_hotpotqa | 0.440 | 0.360 | 24 |
| random_gate_budget_0.10_seed020::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed020::external_hotpotqa | 0.440 | 0.380 | 24 |
| random_gate_budget_0.10_seed021::external_2wiki | 0.520 | 0.220 | 20 |
| random_gate_budget_0.10_seed021::external_hotpotqa | 0.440 | 0.340 | 24 |
| random_gate_budget_0.10_seed022::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed022::external_hotpotqa | 0.440 | 0.380 | 24 |
| random_gate_budget_0.10_seed023::external_2wiki | 0.520 | 0.180 | 21 |
| random_gate_budget_0.10_seed023::external_hotpotqa | 0.460 | 0.340 | 25 |
| random_gate_budget_0.10_seed024::external_2wiki | 0.560 | 0.200 | 20 |
| random_gate_budget_0.10_seed024::external_hotpotqa | 0.440 | 0.320 | 25 |
| random_gate_budget_0.10_seed025::external_2wiki | 0.520 | 0.200 | 21 |
| random_gate_budget_0.10_seed025::external_hotpotqa | 0.480 | 0.340 | 23 |
| random_gate_budget_0.10_seed026::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.10_seed026::external_hotpotqa | 0.440 | 0.360 | 24 |
| random_gate_budget_0.10_seed027::external_2wiki | 0.540 | 0.200 | 20 |
| random_gate_budget_0.10_seed027::external_hotpotqa | 0.460 | 0.380 | 23 |
| random_gate_budget_0.10_seed028::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed028::external_hotpotqa | 0.500 | 0.380 | 22 |
| random_gate_budget_0.10_seed029::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed029::external_hotpotqa | 0.500 | 0.400 | 21 |
| random_gate_budget_0.10_seed030::external_2wiki | 0.540 | 0.240 | 19 |
| random_gate_budget_0.10_seed030::external_hotpotqa | 0.460 | 0.320 | 25 |
| random_gate_budget_0.10_seed031::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed031::external_hotpotqa | 0.440 | 0.300 | 26 |
| random_gate_budget_0.10_seed032::external_2wiki | 0.540 | 0.240 | 19 |
| random_gate_budget_0.10_seed032::external_hotpotqa | 0.460 | 0.380 | 23 |
| random_gate_budget_0.10_seed033::external_2wiki | 0.520 | 0.220 | 20 |
| random_gate_budget_0.10_seed033::external_hotpotqa | 0.440 | 0.340 | 25 |
| random_gate_budget_0.10_seed034::external_2wiki | 0.520 | 0.180 | 21 |
| random_gate_budget_0.10_seed034::external_hotpotqa | 0.440 | 0.380 | 24 |
| random_gate_budget_0.10_seed035::external_2wiki | 0.520 | 0.220 | 20 |
| random_gate_budget_0.10_seed035::external_hotpotqa | 0.500 | 0.380 | 21 |
| random_gate_budget_0.10_seed036::external_2wiki | 0.540 | 0.180 | 21 |
| random_gate_budget_0.10_seed036::external_hotpotqa | 0.440 | 0.320 | 25 |
| random_gate_budget_0.10_seed037::external_2wiki | 0.520 | 0.180 | 21 |
| random_gate_budget_0.10_seed037::external_hotpotqa | 0.500 | 0.360 | 22 |
| random_gate_budget_0.10_seed038::external_2wiki | 0.560 | 0.280 | 18 |
| random_gate_budget_0.10_seed038::external_hotpotqa | 0.480 | 0.360 | 23 |
| random_gate_budget_0.10_seed039::external_2wiki | 0.520 | 0.240 | 19 |
| random_gate_budget_0.10_seed039::external_hotpotqa | 0.440 | 0.320 | 25 |
| random_gate_budget_0.10_seed040::external_2wiki | 0.520 | 0.220 | 20 |
| random_gate_budget_0.10_seed040::external_hotpotqa | 0.460 | 0.380 | 23 |
| random_gate_budget_0.10_seed041::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.10_seed041::external_hotpotqa | 0.460 | 0.360 | 24 |
| random_gate_budget_0.10_seed042::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed042::external_hotpotqa | 0.500 | 0.360 | 23 |
| random_gate_budget_0.10_seed043::external_2wiki | 0.480 | 0.240 | 21 |
| random_gate_budget_0.10_seed043::external_hotpotqa | 0.480 | 0.340 | 23 |
| random_gate_budget_0.10_seed044::external_2wiki | 0.520 | 0.260 | 19 |
| random_gate_budget_0.10_seed044::external_hotpotqa | 0.460 | 0.300 | 25 |
| random_gate_budget_0.10_seed045::external_2wiki | 0.540 | 0.240 | 19 |
| random_gate_budget_0.10_seed045::external_hotpotqa | 0.400 | 0.340 | 26 |
| random_gate_budget_0.10_seed046::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed046::external_hotpotqa | 0.420 | 0.340 | 25 |
| random_gate_budget_0.10_seed047::external_2wiki | 0.500 | 0.240 | 20 |
| random_gate_budget_0.10_seed047::external_hotpotqa | 0.440 | 0.300 | 26 |
| random_gate_budget_0.10_seed048::external_2wiki | 0.520 | 0.240 | 20 |
| random_gate_budget_0.10_seed048::external_hotpotqa | 0.460 | 0.300 | 25 |
| random_gate_budget_0.10_seed049::external_2wiki | 0.480 | 0.260 | 20 |
| random_gate_budget_0.10_seed049::external_hotpotqa | 0.500 | 0.360 | 22 |
| random_gate_budget_0.10_seed050::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed050::external_hotpotqa | 0.440 | 0.340 | 25 |
| random_gate_budget_0.10_seed051::external_2wiki | 0.520 | 0.240 | 20 |
| random_gate_budget_0.10_seed051::external_hotpotqa | 0.480 | 0.320 | 25 |
| random_gate_budget_0.10_seed052::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed052::external_hotpotqa | 0.500 | 0.400 | 21 |
| random_gate_budget_0.10_seed053::external_2wiki | 0.540 | 0.200 | 20 |
| random_gate_budget_0.10_seed053::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed054::external_2wiki | 0.520 | 0.220 | 20 |
| random_gate_budget_0.10_seed054::external_hotpotqa | 0.440 | 0.320 | 26 |
| random_gate_budget_0.10_seed055::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.10_seed055::external_hotpotqa | 0.480 | 0.360 | 23 |
| random_gate_budget_0.10_seed056::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed056::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed057::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.10_seed057::external_hotpotqa | 0.440 | 0.380 | 24 |
| random_gate_budget_0.10_seed058::external_2wiki | 0.520 | 0.240 | 20 |
| random_gate_budget_0.10_seed058::external_hotpotqa | 0.400 | 0.340 | 26 |
| random_gate_budget_0.10_seed059::external_2wiki | 0.520 | 0.200 | 21 |
| random_gate_budget_0.10_seed059::external_hotpotqa | 0.460 | 0.340 | 24 |
| random_gate_budget_0.10_seed060::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.10_seed060::external_hotpotqa | 0.460 | 0.380 | 23 |
| random_gate_budget_0.10_seed061::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed061::external_hotpotqa | 0.400 | 0.340 | 26 |
| random_gate_budget_0.10_seed062::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed062::external_hotpotqa | 0.460 | 0.360 | 23 |
| random_gate_budget_0.10_seed063::external_2wiki | 0.520 | 0.220 | 20 |
| random_gate_budget_0.10_seed063::external_hotpotqa | 0.500 | 0.340 | 23 |
| random_gate_budget_0.10_seed064::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed064::external_hotpotqa | 0.460 | 0.340 | 24 |
| random_gate_budget_0.10_seed065::external_2wiki | 0.520 | 0.200 | 21 |
| random_gate_budget_0.10_seed065::external_hotpotqa | 0.480 | 0.360 | 23 |
| random_gate_budget_0.10_seed066::external_2wiki | 0.540 | 0.220 | 19 |
| random_gate_budget_0.10_seed066::external_hotpotqa | 0.460 | 0.360 | 24 |
| random_gate_budget_0.10_seed067::external_2wiki | 0.560 | 0.180 | 20 |
| random_gate_budget_0.10_seed067::external_hotpotqa | 0.460 | 0.360 | 23 |
| random_gate_budget_0.10_seed068::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed068::external_hotpotqa | 0.460 | 0.320 | 25 |
| random_gate_budget_0.10_seed069::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed069::external_hotpotqa | 0.460 | 0.360 | 24 |
| random_gate_budget_0.10_seed070::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.10_seed070::external_hotpotqa | 0.480 | 0.340 | 23 |
| random_gate_budget_0.10_seed071::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed071::external_hotpotqa | 0.480 | 0.360 | 23 |
| random_gate_budget_0.10_seed072::external_2wiki | 0.520 | 0.180 | 21 |
| random_gate_budget_0.10_seed072::external_hotpotqa | 0.420 | 0.320 | 26 |
| random_gate_budget_0.10_seed073::external_2wiki | 0.480 | 0.240 | 21 |
| random_gate_budget_0.10_seed073::external_hotpotqa | 0.460 | 0.360 | 23 |
| random_gate_budget_0.10_seed074::external_2wiki | 0.520 | 0.200 | 20 |
| random_gate_budget_0.10_seed074::external_hotpotqa | 0.440 | 0.360 | 24 |
| random_gate_budget_0.10_seed075::external_2wiki | 0.540 | 0.260 | 18 |
| random_gate_budget_0.10_seed075::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed076::external_2wiki | 0.520 | 0.200 | 21 |
| random_gate_budget_0.10_seed076::external_hotpotqa | 0.500 | 0.400 | 21 |
| random_gate_budget_0.10_seed077::external_2wiki | 0.480 | 0.240 | 21 |
| random_gate_budget_0.10_seed077::external_hotpotqa | 0.440 | 0.360 | 24 |
| random_gate_budget_0.10_seed078::external_2wiki | 0.540 | 0.200 | 20 |
| random_gate_budget_0.10_seed078::external_hotpotqa | 0.480 | 0.380 | 22 |
| random_gate_budget_0.10_seed079::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.10_seed079::external_hotpotqa | 0.460 | 0.360 | 24 |
| random_gate_budget_0.10_seed080::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed080::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed081::external_2wiki | 0.500 | 0.220 | 21 |
| random_gate_budget_0.10_seed081::external_hotpotqa | 0.440 | 0.360 | 24 |
| random_gate_budget_0.10_seed082::external_2wiki | 0.520 | 0.200 | 20 |
| random_gate_budget_0.10_seed082::external_hotpotqa | 0.480 | 0.400 | 22 |
| random_gate_budget_0.10_seed083::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.10_seed083::external_hotpotqa | 0.440 | 0.380 | 24 |
| random_gate_budget_0.10_seed084::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.10_seed084::external_hotpotqa | 0.480 | 0.380 | 22 |
| random_gate_budget_0.10_seed085::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed085::external_hotpotqa | 0.420 | 0.320 | 26 |
| random_gate_budget_0.10_seed086::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed086::external_hotpotqa | 0.440 | 0.340 | 25 |
| random_gate_budget_0.10_seed087::external_2wiki | 0.520 | 0.200 | 21 |
| random_gate_budget_0.10_seed087::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed088::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed088::external_hotpotqa | 0.460 | 0.360 | 23 |
| random_gate_budget_0.10_seed089::external_2wiki | 0.560 | 0.240 | 19 |
| random_gate_budget_0.10_seed089::external_hotpotqa | 0.460 | 0.400 | 23 |
| random_gate_budget_0.10_seed090::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed090::external_hotpotqa | 0.500 | 0.420 | 21 |
| random_gate_budget_0.10_seed091::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.10_seed091::external_hotpotqa | 0.500 | 0.340 | 23 |
| random_gate_budget_0.10_seed092::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.10_seed092::external_hotpotqa | 0.500 | 0.340 | 22 |
| random_gate_budget_0.10_seed093::external_2wiki | 0.480 | 0.260 | 20 |
| random_gate_budget_0.10_seed093::external_hotpotqa | 0.420 | 0.340 | 25 |
| random_gate_budget_0.10_seed094::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.10_seed094::external_hotpotqa | 0.460 | 0.380 | 23 |
| random_gate_budget_0.10_seed095::external_2wiki | 0.520 | 0.200 | 20 |
| random_gate_budget_0.10_seed095::external_hotpotqa | 0.500 | 0.340 | 23 |
| random_gate_budget_0.10_seed096::external_2wiki | 0.540 | 0.160 | 21 |
| random_gate_budget_0.10_seed096::external_hotpotqa | 0.420 | 0.360 | 25 |
| random_gate_budget_0.10_seed097::external_2wiki | 0.500 | 0.260 | 19 |
| random_gate_budget_0.10_seed097::external_hotpotqa | 0.460 | 0.320 | 25 |
| random_gate_budget_0.10_seed098::external_2wiki | 0.540 | 0.260 | 19 |
| random_gate_budget_0.10_seed098::external_hotpotqa | 0.500 | 0.380 | 21 |
| random_gate_budget_0.10_seed099::external_2wiki | 0.500 | 0.180 | 22 |
| random_gate_budget_0.10_seed099::external_hotpotqa | 0.480 | 0.400 | 22 |
| random_gate_budget_0.25_seed000::external_2wiki | 0.520 | 0.260 | 19 |
| random_gate_budget_0.25_seed000::external_hotpotqa | 0.520 | 0.420 | 21 |
| random_gate_budget_0.25_seed001::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.25_seed001::external_hotpotqa | 0.520 | 0.340 | 23 |
| random_gate_budget_0.25_seed002::external_2wiki | 0.540 | 0.240 | 19 |
| random_gate_budget_0.25_seed002::external_hotpotqa | 0.580 | 0.380 | 20 |
| random_gate_budget_0.25_seed003::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed003::external_hotpotqa | 0.600 | 0.380 | 18 |
| random_gate_budget_0.25_seed004::external_2wiki | 0.520 | 0.260 | 19 |
| random_gate_budget_0.25_seed004::external_hotpotqa | 0.500 | 0.320 | 23 |
| random_gate_budget_0.25_seed005::external_2wiki | 0.640 | 0.260 | 15 |
| random_gate_budget_0.25_seed005::external_hotpotqa | 0.580 | 0.400 | 19 |
| random_gate_budget_0.25_seed006::external_2wiki | 0.580 | 0.280 | 16 |
| random_gate_budget_0.25_seed006::external_hotpotqa | 0.560 | 0.380 | 20 |
| random_gate_budget_0.25_seed007::external_2wiki | 0.540 | 0.280 | 18 |
| random_gate_budget_0.25_seed007::external_hotpotqa | 0.520 | 0.320 | 22 |
| random_gate_budget_0.25_seed008::external_2wiki | 0.520 | 0.200 | 21 |
| random_gate_budget_0.25_seed008::external_hotpotqa | 0.560 | 0.360 | 21 |
| random_gate_budget_0.25_seed009::external_2wiki | 0.560 | 0.280 | 18 |
| random_gate_budget_0.25_seed009::external_hotpotqa | 0.500 | 0.360 | 23 |
| random_gate_budget_0.25_seed010::external_2wiki | 0.580 | 0.240 | 18 |
| random_gate_budget_0.25_seed010::external_hotpotqa | 0.540 | 0.380 | 21 |
| random_gate_budget_0.25_seed011::external_2wiki | 0.580 | 0.280 | 16 |
| random_gate_budget_0.25_seed011::external_hotpotqa | 0.560 | 0.380 | 20 |
| random_gate_budget_0.25_seed012::external_2wiki | 0.540 | 0.220 | 19 |
| random_gate_budget_0.25_seed012::external_hotpotqa | 0.540 | 0.360 | 21 |
| random_gate_budget_0.25_seed013::external_2wiki | 0.520 | 0.280 | 18 |
| random_gate_budget_0.25_seed013::external_hotpotqa | 0.540 | 0.380 | 21 |
| random_gate_budget_0.25_seed014::external_2wiki | 0.580 | 0.260 | 17 |
| random_gate_budget_0.25_seed014::external_hotpotqa | 0.460 | 0.320 | 24 |
| random_gate_budget_0.25_seed015::external_2wiki | 0.580 | 0.260 | 17 |
| random_gate_budget_0.25_seed015::external_hotpotqa | 0.560 | 0.400 | 20 |
| random_gate_budget_0.25_seed016::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.25_seed016::external_hotpotqa | 0.600 | 0.420 | 17 |
| random_gate_budget_0.25_seed017::external_2wiki | 0.540 | 0.260 | 19 |
| random_gate_budget_0.25_seed017::external_hotpotqa | 0.460 | 0.340 | 24 |
| random_gate_budget_0.25_seed018::external_2wiki | 0.540 | 0.220 | 19 |
| random_gate_budget_0.25_seed018::external_hotpotqa | 0.540 | 0.360 | 21 |
| random_gate_budget_0.25_seed019::external_2wiki | 0.640 | 0.240 | 16 |
| random_gate_budget_0.25_seed019::external_hotpotqa | 0.580 | 0.340 | 20 |
| random_gate_budget_0.25_seed020::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed020::external_hotpotqa | 0.540 | 0.420 | 20 |
| random_gate_budget_0.25_seed021::external_2wiki | 0.580 | 0.200 | 19 |
| random_gate_budget_0.25_seed021::external_hotpotqa | 0.560 | 0.400 | 19 |
| random_gate_budget_0.25_seed022::external_2wiki | 0.600 | 0.200 | 18 |
| random_gate_budget_0.25_seed022::external_hotpotqa | 0.540 | 0.380 | 21 |
| random_gate_budget_0.25_seed023::external_2wiki | 0.600 | 0.260 | 17 |
| random_gate_budget_0.25_seed023::external_hotpotqa | 0.540 | 0.380 | 21 |
| random_gate_budget_0.25_seed024::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed024::external_hotpotqa | 0.480 | 0.340 | 23 |
| random_gate_budget_0.25_seed025::external_2wiki | 0.580 | 0.220 | 19 |
| random_gate_budget_0.25_seed025::external_hotpotqa | 0.540 | 0.360 | 21 |
| random_gate_budget_0.25_seed026::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.25_seed026::external_hotpotqa | 0.560 | 0.360 | 21 |
| random_gate_budget_0.25_seed027::external_2wiki | 0.580 | 0.220 | 18 |
| random_gate_budget_0.25_seed027::external_hotpotqa | 0.540 | 0.360 | 21 |
| random_gate_budget_0.25_seed028::external_2wiki | 0.580 | 0.240 | 18 |
| random_gate_budget_0.25_seed028::external_hotpotqa | 0.560 | 0.360 | 21 |
| random_gate_budget_0.25_seed029::external_2wiki | 0.600 | 0.200 | 18 |
| random_gate_budget_0.25_seed029::external_hotpotqa | 0.580 | 0.400 | 19 |
| random_gate_budget_0.25_seed030::external_2wiki | 0.580 | 0.300 | 16 |
| random_gate_budget_0.25_seed030::external_hotpotqa | 0.540 | 0.340 | 22 |
| random_gate_budget_0.25_seed031::external_2wiki | 0.500 | 0.240 | 20 |
| random_gate_budget_0.25_seed031::external_hotpotqa | 0.520 | 0.360 | 22 |
| random_gate_budget_0.25_seed032::external_2wiki | 0.620 | 0.240 | 16 |
| random_gate_budget_0.25_seed032::external_hotpotqa | 0.580 | 0.380 | 19 |
| random_gate_budget_0.25_seed033::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed033::external_hotpotqa | 0.540 | 0.340 | 22 |
| random_gate_budget_0.25_seed034::external_2wiki | 0.580 | 0.240 | 17 |
| random_gate_budget_0.25_seed034::external_hotpotqa | 0.500 | 0.380 | 22 |
| random_gate_budget_0.25_seed035::external_2wiki | 0.580 | 0.240 | 17 |
| random_gate_budget_0.25_seed035::external_hotpotqa | 0.560 | 0.400 | 19 |
| random_gate_budget_0.25_seed036::external_2wiki | 0.600 | 0.260 | 17 |
| random_gate_budget_0.25_seed036::external_hotpotqa | 0.500 | 0.340 | 23 |
| random_gate_budget_0.25_seed037::external_2wiki | 0.580 | 0.200 | 19 |
| random_gate_budget_0.25_seed037::external_hotpotqa | 0.600 | 0.360 | 19 |
| random_gate_budget_0.25_seed038::external_2wiki | 0.600 | 0.260 | 17 |
| random_gate_budget_0.25_seed038::external_hotpotqa | 0.560 | 0.380 | 20 |
| random_gate_budget_0.25_seed039::external_2wiki | 0.560 | 0.260 | 17 |
| random_gate_budget_0.25_seed039::external_hotpotqa | 0.500 | 0.340 | 23 |
| random_gate_budget_0.25_seed040::external_2wiki | 0.600 | 0.280 | 16 |
| random_gate_budget_0.25_seed040::external_hotpotqa | 0.580 | 0.440 | 18 |
| random_gate_budget_0.25_seed041::external_2wiki | 0.560 | 0.260 | 17 |
| random_gate_budget_0.25_seed041::external_hotpotqa | 0.520 | 0.400 | 21 |
| random_gate_budget_0.25_seed042::external_2wiki | 0.560 | 0.200 | 20 |
| random_gate_budget_0.25_seed042::external_hotpotqa | 0.600 | 0.400 | 18 |
| random_gate_budget_0.25_seed043::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.25_seed043::external_hotpotqa | 0.600 | 0.380 | 18 |
| random_gate_budget_0.25_seed044::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed044::external_hotpotqa | 0.520 | 0.340 | 22 |
| random_gate_budget_0.25_seed045::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed045::external_hotpotqa | 0.480 | 0.360 | 23 |
| random_gate_budget_0.25_seed046::external_2wiki | 0.540 | 0.260 | 18 |
| random_gate_budget_0.25_seed046::external_hotpotqa | 0.480 | 0.380 | 22 |
| random_gate_budget_0.25_seed047::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed047::external_hotpotqa | 0.540 | 0.360 | 21 |
| random_gate_budget_0.25_seed048::external_2wiki | 0.540 | 0.280 | 18 |
| random_gate_budget_0.25_seed048::external_hotpotqa | 0.480 | 0.300 | 24 |
| random_gate_budget_0.25_seed049::external_2wiki | 0.520 | 0.260 | 19 |
| random_gate_budget_0.25_seed049::external_hotpotqa | 0.560 | 0.420 | 19 |
| random_gate_budget_0.25_seed050::external_2wiki | 0.560 | 0.280 | 17 |
| random_gate_budget_0.25_seed050::external_hotpotqa | 0.520 | 0.380 | 21 |
| random_gate_budget_0.25_seed051::external_2wiki | 0.580 | 0.260 | 17 |
| random_gate_budget_0.25_seed051::external_hotpotqa | 0.580 | 0.360 | 20 |
| random_gate_budget_0.25_seed052::external_2wiki | 0.540 | 0.240 | 19 |
| random_gate_budget_0.25_seed052::external_hotpotqa | 0.500 | 0.380 | 22 |
| random_gate_budget_0.25_seed053::external_2wiki | 0.560 | 0.220 | 18 |
| random_gate_budget_0.25_seed053::external_hotpotqa | 0.500 | 0.380 | 22 |
| random_gate_budget_0.25_seed054::external_2wiki | 0.600 | 0.240 | 17 |
| random_gate_budget_0.25_seed054::external_hotpotqa | 0.540 | 0.380 | 21 |
| random_gate_budget_0.25_seed055::external_2wiki | 0.540 | 0.260 | 18 |
| random_gate_budget_0.25_seed055::external_hotpotqa | 0.580 | 0.420 | 18 |
| random_gate_budget_0.25_seed056::external_2wiki | 0.520 | 0.240 | 20 |
| random_gate_budget_0.25_seed056::external_hotpotqa | 0.500 | 0.400 | 21 |
| random_gate_budget_0.25_seed057::external_2wiki | 0.500 | 0.260 | 19 |
| random_gate_budget_0.25_seed057::external_hotpotqa | 0.560 | 0.380 | 20 |
| random_gate_budget_0.25_seed058::external_2wiki | 0.600 | 0.280 | 16 |
| random_gate_budget_0.25_seed058::external_hotpotqa | 0.480 | 0.320 | 24 |
| random_gate_budget_0.25_seed059::external_2wiki | 0.540 | 0.240 | 19 |
| random_gate_budget_0.25_seed059::external_hotpotqa | 0.500 | 0.360 | 23 |
| random_gate_budget_0.25_seed060::external_2wiki | 0.540 | 0.280 | 18 |
| random_gate_budget_0.25_seed060::external_hotpotqa | 0.540 | 0.420 | 19 |
| random_gate_budget_0.25_seed061::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed061::external_hotpotqa | 0.480 | 0.380 | 23 |
| random_gate_budget_0.25_seed062::external_2wiki | 0.580 | 0.260 | 17 |
| random_gate_budget_0.25_seed062::external_hotpotqa | 0.540 | 0.380 | 20 |
| random_gate_budget_0.25_seed063::external_2wiki | 0.580 | 0.220 | 18 |
| random_gate_budget_0.25_seed063::external_hotpotqa | 0.540 | 0.380 | 21 |
| random_gate_budget_0.25_seed064::external_2wiki | 0.540 | 0.240 | 19 |
| random_gate_budget_0.25_seed064::external_hotpotqa | 0.540 | 0.360 | 21 |
| random_gate_budget_0.25_seed065::external_2wiki | 0.580 | 0.220 | 19 |
| random_gate_budget_0.25_seed065::external_hotpotqa | 0.560 | 0.340 | 21 |
| random_gate_budget_0.25_seed066::external_2wiki | 0.600 | 0.240 | 17 |
| random_gate_budget_0.25_seed066::external_hotpotqa | 0.500 | 0.340 | 24 |
| random_gate_budget_0.25_seed067::external_2wiki | 0.620 | 0.240 | 17 |
| random_gate_budget_0.25_seed067::external_hotpotqa | 0.520 | 0.360 | 21 |
| random_gate_budget_0.25_seed068::external_2wiki | 0.580 | 0.200 | 18 |
| random_gate_budget_0.25_seed068::external_hotpotqa | 0.480 | 0.320 | 24 |
| random_gate_budget_0.25_seed069::external_2wiki | 0.560 | 0.220 | 19 |
| random_gate_budget_0.25_seed069::external_hotpotqa | 0.580 | 0.380 | 20 |
| random_gate_budget_0.25_seed070::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed070::external_hotpotqa | 0.520 | 0.340 | 22 |
| random_gate_budget_0.25_seed071::external_2wiki | 0.600 | 0.220 | 17 |
| random_gate_budget_0.25_seed071::external_hotpotqa | 0.580 | 0.380 | 19 |
| random_gate_budget_0.25_seed072::external_2wiki | 0.560 | 0.220 | 19 |
| random_gate_budget_0.25_seed072::external_hotpotqa | 0.520 | 0.300 | 23 |
| random_gate_budget_0.25_seed073::external_2wiki | 0.580 | 0.220 | 18 |
| random_gate_budget_0.25_seed073::external_hotpotqa | 0.560 | 0.360 | 20 |
| random_gate_budget_0.25_seed074::external_2wiki | 0.560 | 0.200 | 19 |
| random_gate_budget_0.25_seed074::external_hotpotqa | 0.560 | 0.420 | 19 |
| random_gate_budget_0.25_seed075::external_2wiki | 0.580 | 0.260 | 17 |
| random_gate_budget_0.25_seed075::external_hotpotqa | 0.560 | 0.440 | 19 |
| random_gate_budget_0.25_seed076::external_2wiki | 0.520 | 0.220 | 20 |
| random_gate_budget_0.25_seed076::external_hotpotqa | 0.600 | 0.420 | 17 |
| random_gate_budget_0.25_seed077::external_2wiki | 0.520 | 0.280 | 18 |
| random_gate_budget_0.25_seed077::external_hotpotqa | 0.520 | 0.340 | 22 |
| random_gate_budget_0.25_seed078::external_2wiki | 0.580 | 0.220 | 18 |
| random_gate_budget_0.25_seed078::external_hotpotqa | 0.560 | 0.340 | 21 |
| random_gate_budget_0.25_seed079::external_2wiki | 0.520 | 0.200 | 20 |
| random_gate_budget_0.25_seed079::external_hotpotqa | 0.580 | 0.420 | 18 |
| random_gate_budget_0.25_seed080::external_2wiki | 0.560 | 0.260 | 18 |
| random_gate_budget_0.25_seed080::external_hotpotqa | 0.540 | 0.400 | 21 |
| random_gate_budget_0.25_seed081::external_2wiki | 0.560 | 0.260 | 17 |
| random_gate_budget_0.25_seed081::external_hotpotqa | 0.500 | 0.400 | 21 |
| random_gate_budget_0.25_seed082::external_2wiki | 0.560 | 0.200 | 19 |
| random_gate_budget_0.25_seed082::external_hotpotqa | 0.520 | 0.420 | 20 |
| random_gate_budget_0.25_seed083::external_2wiki | 0.560 | 0.260 | 17 |
| random_gate_budget_0.25_seed083::external_hotpotqa | 0.520 | 0.400 | 21 |
| random_gate_budget_0.25_seed084::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.25_seed084::external_hotpotqa | 0.520 | 0.420 | 20 |
| random_gate_budget_0.25_seed085::external_2wiki | 0.540 | 0.220 | 19 |
| random_gate_budget_0.25_seed085::external_hotpotqa | 0.580 | 0.340 | 20 |
| random_gate_budget_0.25_seed086::external_2wiki | 0.560 | 0.240 | 18 |
| random_gate_budget_0.25_seed086::external_hotpotqa | 0.520 | 0.340 | 23 |
| random_gate_budget_0.25_seed087::external_2wiki | 0.560 | 0.260 | 18 |
| random_gate_budget_0.25_seed087::external_hotpotqa | 0.520 | 0.360 | 21 |
| random_gate_budget_0.25_seed088::external_2wiki | 0.560 | 0.220 | 19 |
| random_gate_budget_0.25_seed088::external_hotpotqa | 0.540 | 0.380 | 20 |
| random_gate_budget_0.25_seed089::external_2wiki | 0.600 | 0.260 | 17 |
| random_gate_budget_0.25_seed089::external_hotpotqa | 0.520 | 0.400 | 21 |
| random_gate_budget_0.25_seed090::external_2wiki | 0.580 | 0.220 | 18 |
| random_gate_budget_0.25_seed090::external_hotpotqa | 0.540 | 0.400 | 20 |
| random_gate_budget_0.25_seed091::external_2wiki | 0.540 | 0.260 | 18 |
| random_gate_budget_0.25_seed091::external_hotpotqa | 0.600 | 0.360 | 19 |
| random_gate_budget_0.25_seed092::external_2wiki | 0.580 | 0.220 | 18 |
| random_gate_budget_0.25_seed092::external_hotpotqa | 0.540 | 0.340 | 21 |
| random_gate_budget_0.25_seed093::external_2wiki | 0.560 | 0.300 | 16 |
| random_gate_budget_0.25_seed093::external_hotpotqa | 0.480 | 0.320 | 24 |
| random_gate_budget_0.25_seed094::external_2wiki | 0.480 | 0.260 | 20 |
| random_gate_budget_0.25_seed094::external_hotpotqa | 0.580 | 0.380 | 19 |
| random_gate_budget_0.25_seed095::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.25_seed095::external_hotpotqa | 0.580 | 0.380 | 19 |
| random_gate_budget_0.25_seed096::external_2wiki | 0.600 | 0.220 | 17 |
| random_gate_budget_0.25_seed096::external_hotpotqa | 0.500 | 0.360 | 23 |
| random_gate_budget_0.25_seed097::external_2wiki | 0.560 | 0.280 | 17 |
| random_gate_budget_0.25_seed097::external_hotpotqa | 0.520 | 0.320 | 23 |
| random_gate_budget_0.25_seed098::external_2wiki | 0.580 | 0.260 | 17 |
| random_gate_budget_0.25_seed098::external_hotpotqa | 0.540 | 0.400 | 20 |
| random_gate_budget_0.25_seed099::external_2wiki | 0.580 | 0.220 | 18 |
| random_gate_budget_0.25_seed099::external_hotpotqa | 0.580 | 0.400 | 19 |
| random_gate_budget_0.40_seed000::external_2wiki | 0.620 | 0.260 | 16 |
| random_gate_budget_0.40_seed000::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed001::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed001::external_hotpotqa | 0.580 | 0.360 | 20 |
| random_gate_budget_0.40_seed002::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed002::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed003::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed003::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed004::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed004::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed005::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed005::external_hotpotqa | 0.620 | 0.420 | 17 |
| random_gate_budget_0.40_seed006::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed006::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed007::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed007::external_hotpotqa | 0.640 | 0.420 | 16 |
| random_gate_budget_0.40_seed008::external_2wiki | 0.600 | 0.280 | 16 |
| random_gate_budget_0.40_seed008::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed009::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed009::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed010::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed010::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed011::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed011::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed012::external_2wiki | 0.620 | 0.240 | 16 |
| random_gate_budget_0.40_seed012::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed013::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed013::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed014::external_2wiki | 0.600 | 0.300 | 15 |
| random_gate_budget_0.40_seed014::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed015::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed015::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed016::external_2wiki | 0.600 | 0.240 | 17 |
| random_gate_budget_0.40_seed016::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed017::external_2wiki | 0.600 | 0.260 | 17 |
| random_gate_budget_0.40_seed017::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed018::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed018::external_hotpotqa | 0.600 | 0.400 | 18 |
| random_gate_budget_0.40_seed019::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed019::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed020::external_2wiki | 0.580 | 0.260 | 17 |
| random_gate_budget_0.40_seed020::external_hotpotqa | 0.640 | 0.420 | 16 |
| random_gate_budget_0.40_seed021::external_2wiki | 0.600 | 0.260 | 17 |
| random_gate_budget_0.40_seed021::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed022::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed022::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed023::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed023::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed024::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed024::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed025::external_2wiki | 0.600 | 0.280 | 16 |
| random_gate_budget_0.40_seed025::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed026::external_2wiki | 0.580 | 0.240 | 17 |
| random_gate_budget_0.40_seed026::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed027::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed027::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed028::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed028::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed029::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed029::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed030::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed030::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed031::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed031::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed032::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed032::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed033::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed033::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed034::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed034::external_hotpotqa | 0.600 | 0.400 | 18 |
| random_gate_budget_0.40_seed035::external_2wiki | 0.580 | 0.280 | 16 |
| random_gate_budget_0.40_seed035::external_hotpotqa | 0.600 | 0.420 | 17 |
| random_gate_budget_0.40_seed036::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed036::external_hotpotqa | 0.620 | 0.420 | 17 |
| random_gate_budget_0.40_seed037::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed037::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed038::external_2wiki | 0.580 | 0.280 | 17 |
| random_gate_budget_0.40_seed038::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed039::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed039::external_hotpotqa | 0.600 | 0.380 | 19 |
| random_gate_budget_0.40_seed040::external_2wiki | 0.640 | 0.260 | 15 |
| random_gate_budget_0.40_seed040::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed041::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed041::external_hotpotqa | 0.600 | 0.420 | 18 |
| random_gate_budget_0.40_seed042::external_2wiki | 0.600 | 0.280 | 16 |
| random_gate_budget_0.40_seed042::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed043::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed043::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed044::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed044::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed045::external_2wiki | 0.620 | 0.260 | 16 |
| random_gate_budget_0.40_seed045::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed046::external_2wiki | 0.600 | 0.300 | 15 |
| random_gate_budget_0.40_seed046::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed047::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed047::external_hotpotqa | 0.580 | 0.380 | 19 |
| random_gate_budget_0.40_seed048::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed048::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed049::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed049::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed050::external_2wiki | 0.600 | 0.280 | 16 |
| random_gate_budget_0.40_seed050::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed051::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed051::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed052::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed052::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed053::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed053::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed054::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed054::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed055::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed055::external_hotpotqa | 0.640 | 0.420 | 16 |
| random_gate_budget_0.40_seed056::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed056::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed057::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed057::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed058::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed058::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed059::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed059::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed060::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed060::external_hotpotqa | 0.640 | 0.420 | 16 |
| random_gate_budget_0.40_seed061::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed061::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed062::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed062::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed063::external_2wiki | 0.580 | 0.240 | 17 |
| random_gate_budget_0.40_seed063::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed064::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed064::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed065::external_2wiki | 0.640 | 0.240 | 16 |
| random_gate_budget_0.40_seed065::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed066::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed066::external_hotpotqa | 0.600 | 0.360 | 19 |
| random_gate_budget_0.40_seed067::external_2wiki | 0.620 | 0.260 | 16 |
| random_gate_budget_0.40_seed067::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed068::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed068::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed069::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed069::external_hotpotqa | 0.600 | 0.380 | 19 |
| random_gate_budget_0.40_seed070::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed070::external_hotpotqa | 0.580 | 0.380 | 19 |
| random_gate_budget_0.40_seed071::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed071::external_hotpotqa | 0.640 | 0.420 | 16 |
| random_gate_budget_0.40_seed072::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed072::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed073::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed073::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed074::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed074::external_hotpotqa | 0.600 | 0.380 | 19 |
| random_gate_budget_0.40_seed075::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed075::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed076::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed076::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed077::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed077::external_hotpotqa | 0.600 | 0.360 | 19 |
| random_gate_budget_0.40_seed078::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed078::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed079::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed079::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed080::external_2wiki | 0.600 | 0.280 | 16 |
| random_gate_budget_0.40_seed080::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed081::external_2wiki | 0.580 | 0.280 | 16 |
| random_gate_budget_0.40_seed081::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed082::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed082::external_hotpotqa | 0.600 | 0.380 | 19 |
| random_gate_budget_0.40_seed083::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed083::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed084::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed084::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed085::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed085::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed086::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed086::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed087::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed087::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed088::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed088::external_hotpotqa | 0.600 | 0.400 | 18 |
| random_gate_budget_0.40_seed089::external_2wiki | 0.600 | 0.280 | 16 |
| random_gate_budget_0.40_seed089::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed090::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed090::external_hotpotqa | 0.620 | 0.400 | 18 |
| random_gate_budget_0.40_seed091::external_2wiki | 0.600 | 0.260 | 16 |
| random_gate_budget_0.40_seed091::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed092::external_2wiki | 0.620 | 0.260 | 16 |
| random_gate_budget_0.40_seed092::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed093::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed093::external_hotpotqa | 0.620 | 0.420 | 17 |
| random_gate_budget_0.40_seed094::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed094::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed095::external_2wiki | 0.600 | 0.300 | 15 |
| random_gate_budget_0.40_seed095::external_hotpotqa | 0.640 | 0.400 | 17 |
| random_gate_budget_0.40_seed096::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed096::external_hotpotqa | 0.580 | 0.380 | 20 |
| random_gate_budget_0.40_seed097::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed097::external_hotpotqa | 0.620 | 0.380 | 18 |
| random_gate_budget_0.40_seed098::external_2wiki | 0.620 | 0.260 | 16 |
| random_gate_budget_0.40_seed098::external_hotpotqa | 0.620 | 0.420 | 17 |
| random_gate_budget_0.40_seed099::external_2wiki | 0.620 | 0.280 | 15 |
| random_gate_budget_0.40_seed099::external_hotpotqa | 0.640 | 0.400 | 17 |
| risk_guided_doc_patch_k2::external_2wiki | 0.620 | 0.280 | 15 |
| risk_guided_doc_patch_k2::external_hotpotqa | 0.640 | 0.400 | 17 |
| safe_gate_budget_0.10::external_2wiki | 0.520 | 0.260 | 19 |
| safe_gate_budget_0.10::external_hotpotqa | 0.420 | 0.320 | 26 |
| safe_gate_budget_0.25::external_2wiki | 0.560 | 0.280 | 17 |
| safe_gate_budget_0.25::external_hotpotqa | 0.520 | 0.360 | 22 |
| safe_gate_budget_0.40::external_2wiki | 0.580 | 0.280 | 16 |
| safe_gate_budget_0.40::external_hotpotqa | 0.620 | 0.380 | 18 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_0544 | external_hotpotqa | 12.2456 | `Phyllocnistis liquidambarisella` | `Liquidambar styraciflua` | `moth` |
| hotpotqa_7385 | external_hotpotqa | 10.1573 | `Christine MacIntyre` | `Joe Weider` | `Christine MacIntyre` |
| 2wiki_782f0c160bd911eba7f7acde48001122 | external_2wiki | 5.7468 | `Kodambakkam` | `October 22, 1970` | `Trivandrum` |
| hotpotqa_6827 | external_hotpotqa | 5.16592 | `Poughkeepsie–Newburgh–Middletown, NY Metropolitan` | `Rochester` | `Buffalo` |
| hotpotqa_7267 | external_hotpotqa | 5.15354 | `Kentucky Wildcats` | `Duke` | `The 1997–98 Kentucky Wildcats men's basketball team` |
| hotpotqa_4222 | external_hotpotqa | 5.04414 | `New York City` | `Fordham University` | `New York City` |
| 2wiki_21e70b7e0bde11eba7f7acde48001122 | external_2wiki | 4.9493 | `Russia` | `Prussia` | `Prussia` |
| 2wiki_34c3dd940bde11eba7f7acde48001122 | external_2wiki | 4.66675 | `Beaulieu-sur-Loire` | `Allada` | `Allada` |
| 2wiki_adf59bec0bdb11eba7f7acde48001122 | external_2wiki | 4.5356 | `Ian Hendry` | `Peter Michael Hamel` | `Leopoldo Torres Ríos` |
| hotpotqa_4537 | external_hotpotqa | 4.5186 | `Hakim Jamal` | `Malcolm X` | `Hakim Abdullah Jamal` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
