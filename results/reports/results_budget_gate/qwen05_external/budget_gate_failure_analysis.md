# Budget Gate Failure Analysis

## Pareto Summary

| target | actual | safe equiv | random mean | percentile | changed+wrong |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.099 | 0.420 | 0.426 | 0.480 | 49 |
| 0.25 | 0.250 | 0.440 | 0.454 | 0.320 | 47 |
| 0.40 | 0.398 | 0.480 | 0.475 | 0.850 | 45 |

# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.250 | 0.357 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.410 | 0.230 | 0.331 | 49 | 0.000 |
| random_gate_budget_0.10_seed000 | 0.410 | 0.240 | 0.339 | 48 | 0.090 |
| random_gate_budget_0.10_seed001 | 0.440 | 0.200 | 0.309 | 50 | 0.097 |
| random_gate_budget_0.10_seed002 | 0.430 | 0.200 | 0.295 | 49 | 0.103 |
| random_gate_budget_0.10_seed003 | 0.420 | 0.220 | 0.319 | 49 | 0.103 |
| random_gate_budget_0.10_seed004 | 0.400 | 0.250 | 0.347 | 48 | 0.091 |
| random_gate_budget_0.10_seed005 | 0.410 | 0.230 | 0.325 | 49 | 0.089 |
| random_gate_budget_0.10_seed006 | 0.420 | 0.240 | 0.329 | 48 | 0.092 |
| random_gate_budget_0.10_seed007 | 0.410 | 0.260 | 0.357 | 48 | 0.092 |
| random_gate_budget_0.10_seed008 | 0.410 | 0.220 | 0.319 | 50 | 0.108 |
| random_gate_budget_0.10_seed009 | 0.410 | 0.220 | 0.326 | 50 | 0.103 |
| random_gate_budget_0.10_seed010 | 0.420 | 0.220 | 0.330 | 49 | 0.097 |
| random_gate_budget_0.10_seed011 | 0.430 | 0.210 | 0.314 | 49 | 0.093 |
| random_gate_budget_0.10_seed012 | 0.420 | 0.220 | 0.325 | 50 | 0.096 |
| random_gate_budget_0.10_seed013 | 0.450 | 0.220 | 0.322 | 47 | 0.103 |
| random_gate_budget_0.10_seed014 | 0.430 | 0.250 | 0.345 | 46 | 0.105 |
| random_gate_budget_0.10_seed015 | 0.470 | 0.210 | 0.320 | 46 | 0.099 |
| random_gate_budget_0.10_seed016 | 0.390 | 0.240 | 0.341 | 49 | 0.087 |
| random_gate_budget_0.10_seed017 | 0.440 | 0.200 | 0.296 | 49 | 0.108 |
| random_gate_budget_0.10_seed018 | 0.440 | 0.220 | 0.321 | 48 | 0.102 |
| random_gate_budget_0.10_seed019 | 0.450 | 0.210 | 0.328 | 47 | 0.099 |
| random_gate_budget_0.10_seed020 | 0.450 | 0.200 | 0.286 | 48 | 0.091 |
| random_gate_budget_0.10_seed021 | 0.410 | 0.240 | 0.335 | 49 | 0.097 |
| random_gate_budget_0.10_seed022 | 0.410 | 0.220 | 0.317 | 49 | 0.097 |
| random_gate_budget_0.10_seed023 | 0.420 | 0.250 | 0.354 | 48 | 0.098 |
| random_gate_budget_0.10_seed024 | 0.410 | 0.250 | 0.342 | 49 | 0.097 |
| random_gate_budget_0.10_seed025 | 0.420 | 0.210 | 0.312 | 50 | 0.103 |
| random_gate_budget_0.10_seed026 | 0.390 | 0.240 | 0.338 | 50 | 0.097 |
| random_gate_budget_0.10_seed027 | 0.440 | 0.210 | 0.308 | 48 | 0.100 |
| random_gate_budget_0.10_seed028 | 0.450 | 0.250 | 0.340 | 45 | 0.095 |
| random_gate_budget_0.10_seed029 | 0.430 | 0.210 | 0.302 | 49 | 0.108 |
| random_gate_budget_0.10_seed030 | 0.430 | 0.210 | 0.315 | 49 | 0.096 |
| random_gate_budget_0.10_seed031 | 0.430 | 0.210 | 0.316 | 49 | 0.104 |
| random_gate_budget_0.10_seed032 | 0.420 | 0.220 | 0.321 | 49 | 0.090 |
| random_gate_budget_0.10_seed033 | 0.440 | 0.210 | 0.304 | 48 | 0.103 |
| random_gate_budget_0.10_seed034 | 0.420 | 0.220 | 0.319 | 49 | 0.094 |
| random_gate_budget_0.10_seed035 | 0.430 | 0.240 | 0.337 | 48 | 0.107 |
| random_gate_budget_0.10_seed036 | 0.430 | 0.220 | 0.315 | 47 | 0.101 |
| random_gate_budget_0.10_seed037 | 0.440 | 0.210 | 0.309 | 49 | 0.096 |
| random_gate_budget_0.10_seed038 | 0.410 | 0.200 | 0.309 | 51 | 0.112 |
| random_gate_budget_0.10_seed039 | 0.420 | 0.230 | 0.333 | 48 | 0.104 |
| random_gate_budget_0.10_seed040 | 0.400 | 0.240 | 0.342 | 49 | 0.087 |
| random_gate_budget_0.10_seed041 | 0.420 | 0.220 | 0.316 | 49 | 0.099 |
| random_gate_budget_0.10_seed042 | 0.430 | 0.240 | 0.333 | 47 | 0.091 |
| random_gate_budget_0.10_seed043 | 0.450 | 0.230 | 0.331 | 46 | 0.107 |
| random_gate_budget_0.10_seed044 | 0.420 | 0.240 | 0.344 | 48 | 0.105 |
| random_gate_budget_0.10_seed045 | 0.410 | 0.240 | 0.339 | 48 | 0.097 |
| random_gate_budget_0.10_seed046 | 0.460 | 0.240 | 0.331 | 44 | 0.095 |
| random_gate_budget_0.10_seed047 | 0.390 | 0.220 | 0.322 | 52 | 0.102 |
| random_gate_budget_0.10_seed048 | 0.430 | 0.230 | 0.314 | 48 | 0.098 |
| random_gate_budget_0.10_seed049 | 0.410 | 0.240 | 0.334 | 49 | 0.114 |
| random_gate_budget_0.10_seed050 | 0.440 | 0.230 | 0.319 | 47 | 0.105 |
| random_gate_budget_0.10_seed051 | 0.420 | 0.230 | 0.318 | 48 | 0.096 |
| random_gate_budget_0.10_seed052 | 0.450 | 0.230 | 0.324 | 46 | 0.099 |
| random_gate_budget_0.10_seed053 | 0.400 | 0.240 | 0.338 | 48 | 0.090 |
| random_gate_budget_0.10_seed054 | 0.420 | 0.210 | 0.308 | 50 | 0.106 |
| random_gate_budget_0.10_seed055 | 0.430 | 0.220 | 0.322 | 49 | 0.099 |
| random_gate_budget_0.10_seed056 | 0.450 | 0.220 | 0.307 | 46 | 0.092 |
| random_gate_budget_0.10_seed057 | 0.390 | 0.240 | 0.333 | 49 | 0.094 |
| random_gate_budget_0.10_seed058 | 0.410 | 0.230 | 0.318 | 49 | 0.111 |
| random_gate_budget_0.10_seed059 | 0.470 | 0.230 | 0.316 | 44 | 0.115 |
| random_gate_budget_0.10_seed060 | 0.430 | 0.240 | 0.336 | 47 | 0.099 |
| random_gate_budget_0.10_seed061 | 0.430 | 0.230 | 0.344 | 48 | 0.105 |
| random_gate_budget_0.10_seed062 | 0.410 | 0.240 | 0.336 | 49 | 0.100 |
| random_gate_budget_0.10_seed063 | 0.430 | 0.260 | 0.364 | 46 | 0.111 |
| random_gate_budget_0.10_seed064 | 0.420 | 0.210 | 0.293 | 49 | 0.104 |
| random_gate_budget_0.10_seed065 | 0.420 | 0.200 | 0.294 | 50 | 0.098 |
| random_gate_budget_0.10_seed066 | 0.430 | 0.200 | 0.300 | 50 | 0.107 |
| random_gate_budget_0.10_seed067 | 0.420 | 0.220 | 0.305 | 49 | 0.107 |
| random_gate_budget_0.10_seed068 | 0.400 | 0.230 | 0.334 | 50 | 0.096 |
| random_gate_budget_0.10_seed069 | 0.430 | 0.220 | 0.315 | 48 | 0.104 |
| random_gate_budget_0.10_seed070 | 0.430 | 0.230 | 0.321 | 48 | 0.103 |
| random_gate_budget_0.10_seed071 | 0.430 | 0.210 | 0.311 | 49 | 0.091 |
| random_gate_budget_0.10_seed072 | 0.430 | 0.190 | 0.279 | 50 | 0.105 |
| random_gate_budget_0.10_seed073 | 0.420 | 0.230 | 0.329 | 49 | 0.095 |
| random_gate_budget_0.10_seed074 | 0.390 | 0.240 | 0.337 | 50 | 0.089 |
| random_gate_budget_0.10_seed075 | 0.420 | 0.220 | 0.324 | 49 | 0.101 |
| random_gate_budget_0.10_seed076 | 0.440 | 0.220 | 0.327 | 48 | 0.102 |
| random_gate_budget_0.10_seed077 | 0.390 | 0.250 | 0.347 | 49 | 0.100 |
| random_gate_budget_0.10_seed078 | 0.420 | 0.220 | 0.318 | 50 | 0.106 |
| random_gate_budget_0.10_seed079 | 0.430 | 0.210 | 0.314 | 49 | 0.094 |
| random_gate_budget_0.10_seed080 | 0.420 | 0.260 | 0.360 | 46 | 0.107 |
| random_gate_budget_0.10_seed081 | 0.450 | 0.240 | 0.332 | 45 | 0.092 |
| random_gate_budget_0.10_seed082 | 0.410 | 0.240 | 0.336 | 48 | 0.084 |
| random_gate_budget_0.10_seed083 | 0.430 | 0.230 | 0.326 | 48 | 0.095 |
| random_gate_budget_0.10_seed084 | 0.440 | 0.230 | 0.329 | 48 | 0.100 |
| random_gate_budget_0.10_seed085 | 0.450 | 0.170 | 0.276 | 50 | 0.108 |
| random_gate_budget_0.10_seed086 | 0.440 | 0.200 | 0.293 | 49 | 0.095 |
| random_gate_budget_0.10_seed087 | 0.430 | 0.210 | 0.312 | 49 | 0.104 |
| random_gate_budget_0.10_seed088 | 0.450 | 0.220 | 0.313 | 47 | 0.102 |
| random_gate_budget_0.10_seed089 | 0.470 | 0.200 | 0.295 | 46 | 0.114 |
| random_gate_budget_0.10_seed090 | 0.390 | 0.230 | 0.331 | 50 | 0.095 |
| random_gate_budget_0.10_seed091 | 0.460 | 0.240 | 0.330 | 44 | 0.109 |
| random_gate_budget_0.10_seed092 | 0.410 | 0.240 | 0.350 | 49 | 0.101 |
| random_gate_budget_0.10_seed093 | 0.440 | 0.240 | 0.329 | 46 | 0.112 |
| random_gate_budget_0.10_seed094 | 0.440 | 0.230 | 0.324 | 47 | 0.105 |
| random_gate_budget_0.10_seed095 | 0.430 | 0.230 | 0.327 | 48 | 0.100 |
| random_gate_budget_0.10_seed096 | 0.420 | 0.220 | 0.328 | 49 | 0.102 |
| random_gate_budget_0.10_seed097 | 0.420 | 0.220 | 0.320 | 49 | 0.110 |
| random_gate_budget_0.10_seed098 | 0.470 | 0.230 | 0.323 | 44 | 0.100 |
| random_gate_budget_0.10_seed099 | 0.440 | 0.220 | 0.315 | 49 | 0.112 |
| random_gate_budget_0.25_seed000 | 0.440 | 0.240 | 0.329 | 47 | 0.236 |
| random_gate_budget_0.25_seed001 | 0.440 | 0.210 | 0.308 | 49 | 0.244 |
| random_gate_budget_0.25_seed002 | 0.460 | 0.240 | 0.344 | 45 | 0.254 |
| random_gate_budget_0.25_seed003 | 0.450 | 0.230 | 0.329 | 47 | 0.258 |
| random_gate_budget_0.25_seed004 | 0.440 | 0.250 | 0.347 | 45 | 0.249 |
| random_gate_budget_0.25_seed005 | 0.470 | 0.220 | 0.309 | 46 | 0.246 |
| random_gate_budget_0.25_seed006 | 0.460 | 0.240 | 0.332 | 46 | 0.252 |
| random_gate_budget_0.25_seed007 | 0.440 | 0.240 | 0.347 | 47 | 0.252 |
| random_gate_budget_0.25_seed008 | 0.470 | 0.220 | 0.312 | 46 | 0.255 |
| random_gate_budget_0.25_seed009 | 0.440 | 0.200 | 0.314 | 50 | 0.261 |
| random_gate_budget_0.25_seed010 | 0.420 | 0.220 | 0.317 | 50 | 0.259 |
| random_gate_budget_0.25_seed011 | 0.460 | 0.250 | 0.351 | 45 | 0.245 |
| random_gate_budget_0.25_seed012 | 0.450 | 0.190 | 0.289 | 49 | 0.247 |
| random_gate_budget_0.25_seed013 | 0.440 | 0.250 | 0.340 | 46 | 0.251 |
| random_gate_budget_0.25_seed014 | 0.430 | 0.240 | 0.325 | 47 | 0.258 |
| random_gate_budget_0.25_seed015 | 0.430 | 0.220 | 0.326 | 48 | 0.243 |
| random_gate_budget_0.25_seed016 | 0.430 | 0.240 | 0.336 | 47 | 0.236 |
| random_gate_budget_0.25_seed017 | 0.460 | 0.200 | 0.289 | 47 | 0.260 |
| random_gate_budget_0.25_seed018 | 0.450 | 0.210 | 0.323 | 48 | 0.245 |
| random_gate_budget_0.25_seed019 | 0.460 | 0.210 | 0.311 | 47 | 0.257 |
| random_gate_budget_0.25_seed020 | 0.460 | 0.210 | 0.307 | 47 | 0.252 |
| random_gate_budget_0.25_seed021 | 0.440 | 0.210 | 0.309 | 49 | 0.245 |
| random_gate_budget_0.25_seed022 | 0.440 | 0.210 | 0.317 | 48 | 0.255 |
| random_gate_budget_0.25_seed023 | 0.440 | 0.220 | 0.330 | 48 | 0.243 |
| random_gate_budget_0.25_seed024 | 0.450 | 0.240 | 0.324 | 45 | 0.252 |
| random_gate_budget_0.25_seed025 | 0.460 | 0.210 | 0.307 | 48 | 0.249 |
| random_gate_budget_0.25_seed026 | 0.440 | 0.190 | 0.289 | 50 | 0.261 |
| random_gate_budget_0.25_seed027 | 0.470 | 0.220 | 0.317 | 46 | 0.259 |
| random_gate_budget_0.25_seed028 | 0.470 | 0.220 | 0.335 | 46 | 0.258 |
| random_gate_budget_0.25_seed029 | 0.450 | 0.220 | 0.312 | 47 | 0.255 |
| random_gate_budget_0.25_seed030 | 0.470 | 0.210 | 0.298 | 46 | 0.262 |
| random_gate_budget_0.25_seed031 | 0.440 | 0.210 | 0.310 | 48 | 0.248 |
| random_gate_budget_0.25_seed032 | 0.440 | 0.230 | 0.326 | 48 | 0.244 |
| random_gate_budget_0.25_seed033 | 0.470 | 0.200 | 0.293 | 47 | 0.256 |
| random_gate_budget_0.25_seed034 | 0.450 | 0.230 | 0.324 | 46 | 0.259 |
| random_gate_budget_0.25_seed035 | 0.460 | 0.240 | 0.339 | 46 | 0.251 |
| random_gate_budget_0.25_seed036 | 0.420 | 0.220 | 0.314 | 48 | 0.255 |
| random_gate_budget_0.25_seed037 | 0.490 | 0.200 | 0.293 | 46 | 0.257 |
| random_gate_budget_0.25_seed038 | 0.420 | 0.220 | 0.315 | 50 | 0.258 |
| random_gate_budget_0.25_seed039 | 0.420 | 0.240 | 0.342 | 48 | 0.255 |
| random_gate_budget_0.25_seed040 | 0.460 | 0.230 | 0.329 | 45 | 0.243 |
| random_gate_budget_0.25_seed041 | 0.460 | 0.220 | 0.314 | 46 | 0.243 |
| random_gate_budget_0.25_seed042 | 0.480 | 0.220 | 0.322 | 45 | 0.257 |
| random_gate_budget_0.25_seed043 | 0.470 | 0.240 | 0.345 | 44 | 0.259 |
| random_gate_budget_0.25_seed044 | 0.470 | 0.230 | 0.334 | 46 | 0.261 |
| random_gate_budget_0.25_seed045 | 0.450 | 0.260 | 0.345 | 44 | 0.257 |
| random_gate_budget_0.25_seed046 | 0.470 | 0.240 | 0.335 | 44 | 0.254 |
| random_gate_budget_0.25_seed047 | 0.460 | 0.200 | 0.305 | 48 | 0.257 |
| random_gate_budget_0.25_seed048 | 0.420 | 0.250 | 0.332 | 48 | 0.265 |
| random_gate_budget_0.25_seed049 | 0.440 | 0.210 | 0.306 | 49 | 0.255 |
| random_gate_budget_0.25_seed050 | 0.470 | 0.220 | 0.316 | 46 | 0.264 |
| random_gate_budget_0.25_seed051 | 0.440 | 0.230 | 0.322 | 47 | 0.238 |
| random_gate_budget_0.25_seed052 | 0.470 | 0.210 | 0.317 | 45 | 0.241 |
| random_gate_budget_0.25_seed053 | 0.460 | 0.220 | 0.321 | 45 | 0.252 |
| random_gate_budget_0.25_seed054 | 0.470 | 0.220 | 0.315 | 46 | 0.250 |
| random_gate_budget_0.25_seed055 | 0.460 | 0.230 | 0.315 | 46 | 0.263 |
| random_gate_budget_0.25_seed056 | 0.470 | 0.220 | 0.304 | 46 | 0.250 |
| random_gate_budget_0.25_seed057 | 0.430 | 0.250 | 0.348 | 46 | 0.257 |
| random_gate_budget_0.25_seed058 | 0.440 | 0.220 | 0.300 | 48 | 0.257 |
| random_gate_budget_0.25_seed059 | 0.490 | 0.250 | 0.334 | 42 | 0.266 |
| random_gate_budget_0.25_seed060 | 0.470 | 0.230 | 0.319 | 45 | 0.244 |
| random_gate_budget_0.25_seed061 | 0.450 | 0.210 | 0.309 | 48 | 0.252 |
| random_gate_budget_0.25_seed062 | 0.460 | 0.210 | 0.313 | 47 | 0.258 |
| random_gate_budget_0.25_seed063 | 0.470 | 0.210 | 0.308 | 46 | 0.264 |
| random_gate_budget_0.25_seed064 | 0.480 | 0.200 | 0.289 | 45 | 0.255 |
| random_gate_budget_0.25_seed065 | 0.470 | 0.190 | 0.275 | 47 | 0.254 |
| random_gate_budget_0.25_seed066 | 0.490 | 0.200 | 0.293 | 46 | 0.256 |
| random_gate_budget_0.25_seed067 | 0.450 | 0.250 | 0.342 | 44 | 0.248 |
| random_gate_budget_0.25_seed068 | 0.420 | 0.230 | 0.319 | 49 | 0.251 |
| random_gate_budget_0.25_seed069 | 0.460 | 0.200 | 0.298 | 48 | 0.258 |
| random_gate_budget_0.25_seed070 | 0.440 | 0.230 | 0.327 | 47 | 0.244 |
| random_gate_budget_0.25_seed071 | 0.470 | 0.230 | 0.329 | 45 | 0.246 |
| random_gate_budget_0.25_seed072 | 0.460 | 0.200 | 0.301 | 47 | 0.250 |
| random_gate_budget_0.25_seed073 | 0.430 | 0.210 | 0.306 | 49 | 0.238 |
| random_gate_budget_0.25_seed074 | 0.460 | 0.210 | 0.311 | 46 | 0.245 |
| random_gate_budget_0.25_seed075 | 0.460 | 0.240 | 0.331 | 45 | 0.240 |
| random_gate_budget_0.25_seed076 | 0.470 | 0.240 | 0.335 | 45 | 0.243 |
| random_gate_budget_0.25_seed077 | 0.420 | 0.220 | 0.326 | 50 | 0.260 |
| random_gate_budget_0.25_seed078 | 0.450 | 0.220 | 0.307 | 47 | 0.259 |
| random_gate_budget_0.25_seed079 | 0.480 | 0.220 | 0.315 | 45 | 0.246 |
| random_gate_budget_0.25_seed080 | 0.460 | 0.240 | 0.341 | 45 | 0.256 |
| random_gate_budget_0.25_seed081 | 0.440 | 0.260 | 0.338 | 45 | 0.241 |
| random_gate_budget_0.25_seed082 | 0.430 | 0.230 | 0.326 | 48 | 0.242 |
| random_gate_budget_0.25_seed083 | 0.450 | 0.220 | 0.300 | 46 | 0.232 |
| random_gate_budget_0.25_seed084 | 0.450 | 0.230 | 0.321 | 47 | 0.243 |
| random_gate_budget_0.25_seed085 | 0.450 | 0.190 | 0.291 | 49 | 0.262 |
| random_gate_budget_0.25_seed086 | 0.430 | 0.230 | 0.320 | 48 | 0.257 |
| random_gate_budget_0.25_seed087 | 0.450 | 0.200 | 0.296 | 47 | 0.247 |
| random_gate_budget_0.25_seed088 | 0.450 | 0.240 | 0.327 | 45 | 0.247 |
| random_gate_budget_0.25_seed089 | 0.470 | 0.200 | 0.289 | 46 | 0.245 |
| random_gate_budget_0.25_seed090 | 0.450 | 0.200 | 0.302 | 48 | 0.252 |
| random_gate_budget_0.25_seed091 | 0.440 | 0.250 | 0.335 | 45 | 0.249 |
| random_gate_budget_0.25_seed092 | 0.470 | 0.210 | 0.301 | 46 | 0.252 |
| random_gate_budget_0.25_seed093 | 0.450 | 0.200 | 0.292 | 48 | 0.249 |
| random_gate_budget_0.25_seed094 | 0.450 | 0.220 | 0.309 | 46 | 0.255 |
| random_gate_budget_0.25_seed095 | 0.490 | 0.250 | 0.335 | 42 | 0.260 |
| random_gate_budget_0.25_seed096 | 0.470 | 0.190 | 0.292 | 47 | 0.245 |
| random_gate_budget_0.25_seed097 | 0.470 | 0.210 | 0.312 | 46 | 0.257 |
| random_gate_budget_0.25_seed098 | 0.450 | 0.230 | 0.324 | 47 | 0.242 |
| random_gate_budget_0.25_seed099 | 0.480 | 0.230 | 0.316 | 44 | 0.262 |
| random_gate_budget_0.40_seed000 | 0.470 | 0.230 | 0.318 | 45 | 0.398 |
| random_gate_budget_0.40_seed001 | 0.470 | 0.200 | 0.294 | 47 | 0.397 |
| random_gate_budget_0.40_seed002 | 0.490 | 0.220 | 0.314 | 44 | 0.402 |
| random_gate_budget_0.40_seed003 | 0.460 | 0.220 | 0.325 | 47 | 0.403 |
| random_gate_budget_0.40_seed004 | 0.460 | 0.240 | 0.334 | 45 | 0.402 |
| random_gate_budget_0.40_seed005 | 0.480 | 0.220 | 0.314 | 45 | 0.403 |
| random_gate_budget_0.40_seed006 | 0.480 | 0.220 | 0.308 | 45 | 0.402 |
| random_gate_budget_0.40_seed007 | 0.470 | 0.240 | 0.334 | 44 | 0.404 |
| random_gate_budget_0.40_seed008 | 0.470 | 0.230 | 0.325 | 45 | 0.403 |
| random_gate_budget_0.40_seed009 | 0.480 | 0.220 | 0.319 | 45 | 0.405 |
| random_gate_budget_0.40_seed010 | 0.480 | 0.210 | 0.304 | 46 | 0.405 |
| random_gate_budget_0.40_seed011 | 0.470 | 0.220 | 0.319 | 46 | 0.397 |
| random_gate_budget_0.40_seed012 | 0.470 | 0.220 | 0.310 | 46 | 0.403 |
| random_gate_budget_0.40_seed013 | 0.480 | 0.220 | 0.314 | 45 | 0.403 |
| random_gate_budget_0.40_seed014 | 0.470 | 0.230 | 0.324 | 45 | 0.404 |
| random_gate_budget_0.40_seed015 | 0.470 | 0.210 | 0.304 | 46 | 0.404 |
| random_gate_budget_0.40_seed016 | 0.470 | 0.220 | 0.310 | 46 | 0.390 |
| random_gate_budget_0.40_seed017 | 0.470 | 0.230 | 0.317 | 45 | 0.396 |
| random_gate_budget_0.40_seed018 | 0.470 | 0.200 | 0.304 | 47 | 0.399 |
| random_gate_budget_0.40_seed019 | 0.470 | 0.200 | 0.294 | 46 | 0.398 |
| random_gate_budget_0.40_seed020 | 0.480 | 0.230 | 0.321 | 44 | 0.405 |
| random_gate_budget_0.40_seed021 | 0.480 | 0.220 | 0.314 | 45 | 0.405 |
| random_gate_budget_0.40_seed022 | 0.480 | 0.220 | 0.314 | 45 | 0.404 |
| random_gate_budget_0.40_seed023 | 0.470 | 0.220 | 0.319 | 46 | 0.403 |
| random_gate_budget_0.40_seed024 | 0.480 | 0.220 | 0.314 | 45 | 0.408 |
| random_gate_budget_0.40_seed025 | 0.490 | 0.220 | 0.312 | 44 | 0.407 |
| random_gate_budget_0.40_seed026 | 0.480 | 0.200 | 0.294 | 46 | 0.408 |
| random_gate_budget_0.40_seed027 | 0.490 | 0.210 | 0.304 | 45 | 0.399 |
| random_gate_budget_0.40_seed028 | 0.480 | 0.220 | 0.314 | 45 | 0.404 |
| random_gate_budget_0.40_seed029 | 0.460 | 0.210 | 0.304 | 47 | 0.399 |
| random_gate_budget_0.40_seed030 | 0.480 | 0.220 | 0.314 | 45 | 0.410 |
| random_gate_budget_0.40_seed031 | 0.470 | 0.230 | 0.319 | 45 | 0.403 |
| random_gate_budget_0.40_seed032 | 0.460 | 0.230 | 0.324 | 46 | 0.402 |
| random_gate_budget_0.40_seed033 | 0.500 | 0.210 | 0.303 | 44 | 0.406 |
| random_gate_budget_0.40_seed034 | 0.470 | 0.220 | 0.311 | 46 | 0.398 |
| random_gate_budget_0.40_seed035 | 0.460 | 0.240 | 0.335 | 45 | 0.398 |
| random_gate_budget_0.40_seed036 | 0.470 | 0.220 | 0.323 | 46 | 0.399 |
| random_gate_budget_0.40_seed037 | 0.490 | 0.220 | 0.314 | 44 | 0.400 |
| random_gate_budget_0.40_seed038 | 0.460 | 0.230 | 0.324 | 46 | 0.408 |
| random_gate_budget_0.40_seed039 | 0.460 | 0.230 | 0.324 | 45 | 0.404 |
| random_gate_budget_0.40_seed040 | 0.480 | 0.220 | 0.310 | 45 | 0.402 |
| random_gate_budget_0.40_seed041 | 0.490 | 0.210 | 0.309 | 45 | 0.408 |
| random_gate_budget_0.40_seed042 | 0.480 | 0.220 | 0.314 | 45 | 0.407 |
| random_gate_budget_0.40_seed043 | 0.480 | 0.220 | 0.314 | 45 | 0.401 |
| random_gate_budget_0.40_seed044 | 0.480 | 0.220 | 0.314 | 45 | 0.400 |
| random_gate_budget_0.40_seed045 | 0.460 | 0.240 | 0.327 | 45 | 0.397 |
| random_gate_budget_0.40_seed046 | 0.460 | 0.230 | 0.330 | 46 | 0.399 |
| random_gate_budget_0.40_seed047 | 0.480 | 0.200 | 0.294 | 47 | 0.401 |
| random_gate_budget_0.40_seed048 | 0.470 | 0.220 | 0.314 | 46 | 0.407 |
| random_gate_budget_0.40_seed049 | 0.450 | 0.200 | 0.297 | 49 | 0.395 |
| random_gate_budget_0.40_seed050 | 0.480 | 0.220 | 0.319 | 45 | 0.409 |
| random_gate_budget_0.40_seed051 | 0.460 | 0.220 | 0.320 | 47 | 0.399 |
| random_gate_budget_0.40_seed052 | 0.480 | 0.220 | 0.319 | 45 | 0.398 |
| random_gate_budget_0.40_seed053 | 0.470 | 0.220 | 0.319 | 46 | 0.410 |
| random_gate_budget_0.40_seed054 | 0.460 | 0.240 | 0.322 | 45 | 0.399 |
| random_gate_budget_0.40_seed055 | 0.490 | 0.230 | 0.314 | 43 | 0.403 |
| random_gate_budget_0.40_seed056 | 0.460 | 0.230 | 0.312 | 46 | 0.401 |
| random_gate_budget_0.40_seed057 | 0.470 | 0.220 | 0.319 | 46 | 0.399 |
| random_gate_budget_0.40_seed058 | 0.480 | 0.200 | 0.294 | 46 | 0.403 |
| random_gate_budget_0.40_seed059 | 0.470 | 0.230 | 0.317 | 45 | 0.400 |
| random_gate_budget_0.40_seed060 | 0.500 | 0.220 | 0.310 | 43 | 0.403 |
| random_gate_budget_0.40_seed061 | 0.470 | 0.220 | 0.317 | 46 | 0.400 |
| random_gate_budget_0.40_seed062 | 0.490 | 0.200 | 0.298 | 46 | 0.402 |
| random_gate_budget_0.40_seed063 | 0.480 | 0.220 | 0.314 | 45 | 0.400 |
| random_gate_budget_0.40_seed064 | 0.470 | 0.210 | 0.297 | 46 | 0.407 |
| random_gate_budget_0.40_seed065 | 0.480 | 0.220 | 0.310 | 45 | 0.394 |
| random_gate_budget_0.40_seed066 | 0.490 | 0.220 | 0.312 | 44 | 0.404 |
| random_gate_budget_0.40_seed067 | 0.480 | 0.220 | 0.314 | 45 | 0.402 |
| random_gate_budget_0.40_seed068 | 0.480 | 0.220 | 0.314 | 45 | 0.404 |
| random_gate_budget_0.40_seed069 | 0.490 | 0.220 | 0.314 | 45 | 0.402 |
| random_gate_budget_0.40_seed070 | 0.460 | 0.220 | 0.314 | 46 | 0.397 |
| random_gate_budget_0.40_seed071 | 0.480 | 0.220 | 0.314 | 45 | 0.404 |
| random_gate_budget_0.40_seed072 | 0.470 | 0.210 | 0.304 | 46 | 0.403 |
| random_gate_budget_0.40_seed073 | 0.460 | 0.210 | 0.309 | 47 | 0.398 |
| random_gate_budget_0.40_seed074 | 0.480 | 0.210 | 0.302 | 45 | 0.406 |
| random_gate_budget_0.40_seed075 | 0.490 | 0.220 | 0.318 | 44 | 0.397 |
| random_gate_budget_0.40_seed076 | 0.480 | 0.220 | 0.307 | 45 | 0.402 |
| random_gate_budget_0.40_seed077 | 0.460 | 0.220 | 0.324 | 47 | 0.401 |
| random_gate_budget_0.40_seed078 | 0.480 | 0.250 | 0.341 | 43 | 0.403 |
| random_gate_budget_0.40_seed079 | 0.460 | 0.210 | 0.310 | 47 | 0.397 |
| random_gate_budget_0.40_seed080 | 0.480 | 0.230 | 0.329 | 44 | 0.406 |
| random_gate_budget_0.40_seed081 | 0.470 | 0.220 | 0.319 | 46 | 0.404 |
| random_gate_budget_0.40_seed082 | 0.460 | 0.230 | 0.323 | 46 | 0.400 |
| random_gate_budget_0.40_seed083 | 0.490 | 0.220 | 0.314 | 44 | 0.402 |
| random_gate_budget_0.40_seed084 | 0.480 | 0.230 | 0.322 | 44 | 0.396 |
| random_gate_budget_0.40_seed085 | 0.480 | 0.210 | 0.307 | 46 | 0.408 |
| random_gate_budget_0.40_seed086 | 0.480 | 0.220 | 0.314 | 45 | 0.406 |
| random_gate_budget_0.40_seed087 | 0.470 | 0.230 | 0.324 | 45 | 0.406 |
| random_gate_budget_0.40_seed088 | 0.480 | 0.240 | 0.336 | 43 | 0.403 |
| random_gate_budget_0.40_seed089 | 0.480 | 0.220 | 0.314 | 45 | 0.403 |
| random_gate_budget_0.40_seed090 | 0.480 | 0.210 | 0.304 | 45 | 0.411 |
| random_gate_budget_0.40_seed091 | 0.470 | 0.220 | 0.319 | 46 | 0.402 |
| random_gate_budget_0.40_seed092 | 0.470 | 0.220 | 0.314 | 46 | 0.401 |
| random_gate_budget_0.40_seed093 | 0.480 | 0.220 | 0.314 | 45 | 0.401 |
| random_gate_budget_0.40_seed094 | 0.460 | 0.220 | 0.307 | 46 | 0.402 |
| random_gate_budget_0.40_seed095 | 0.480 | 0.220 | 0.314 | 45 | 0.408 |
| random_gate_budget_0.40_seed096 | 0.480 | 0.230 | 0.324 | 44 | 0.402 |
| random_gate_budget_0.40_seed097 | 0.460 | 0.230 | 0.324 | 46 | 0.408 |
| random_gate_budget_0.40_seed098 | 0.490 | 0.210 | 0.304 | 45 | 0.402 |
| random_gate_budget_0.40_seed099 | 0.490 | 0.210 | 0.305 | 45 | 0.399 |
| risk_guided_doc_patch_k2 | 0.480 | 0.220 | 0.314 | 45 | 0.428 |
| safe_gate_budget_0.10 | 0.420 | 0.230 | 0.313 | 49 | 0.104 |
| safe_gate_budget_0.25 | 0.440 | 0.230 | 0.320 | 47 | 0.241 |
| safe_gate_budget_0.40 | 0.480 | 0.220 | 0.314 | 45 | 0.396 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_2wiki | 1.000 | 0.200 | 0 |
| full_prefill::external_hotpotqa | 1.000 | 0.300 | 0 |
| prefix_conditioned_naive_global::external_2wiki | 0.400 | 0.260 | 23 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed000::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed000::external_hotpotqa | 0.420 | 0.220 | 25 |
| random_gate_budget_0.10_seed001::external_2wiki | 0.400 | 0.220 | 25 |
| random_gate_budget_0.10_seed001::external_hotpotqa | 0.480 | 0.180 | 25 |
| random_gate_budget_0.10_seed002::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.10_seed002::external_hotpotqa | 0.440 | 0.140 | 27 |
| random_gate_budget_0.10_seed003::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed003::external_hotpotqa | 0.400 | 0.200 | 27 |
| random_gate_budget_0.10_seed004::external_2wiki | 0.380 | 0.280 | 23 |
| random_gate_budget_0.10_seed004::external_hotpotqa | 0.420 | 0.220 | 25 |
| random_gate_budget_0.10_seed005::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.10_seed005::external_hotpotqa | 0.420 | 0.220 | 25 |
| random_gate_budget_0.10_seed006::external_2wiki | 0.380 | 0.240 | 25 |
| random_gate_budget_0.10_seed006::external_hotpotqa | 0.460 | 0.240 | 23 |
| random_gate_budget_0.10_seed007::external_2wiki | 0.360 | 0.280 | 24 |
| random_gate_budget_0.10_seed007::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.10_seed008::external_2wiki | 0.400 | 0.220 | 25 |
| random_gate_budget_0.10_seed008::external_hotpotqa | 0.420 | 0.220 | 25 |
| random_gate_budget_0.10_seed009::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed009::external_hotpotqa | 0.440 | 0.180 | 26 |
| random_gate_budget_0.10_seed010::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed010::external_hotpotqa | 0.400 | 0.200 | 27 |
| random_gate_budget_0.10_seed011::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed011::external_hotpotqa | 0.420 | 0.180 | 27 |
| random_gate_budget_0.10_seed012::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.10_seed012::external_hotpotqa | 0.440 | 0.200 | 26 |
| random_gate_budget_0.10_seed013::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.10_seed013::external_hotpotqa | 0.460 | 0.180 | 26 |
| random_gate_budget_0.10_seed014::external_2wiki | 0.420 | 0.280 | 21 |
| random_gate_budget_0.10_seed014::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.10_seed015::external_2wiki | 0.460 | 0.260 | 20 |
| random_gate_budget_0.10_seed015::external_hotpotqa | 0.480 | 0.160 | 26 |
| random_gate_budget_0.10_seed016::external_2wiki | 0.380 | 0.280 | 23 |
| random_gate_budget_0.10_seed016::external_hotpotqa | 0.400 | 0.200 | 26 |
| random_gate_budget_0.10_seed017::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.10_seed017::external_hotpotqa | 0.440 | 0.180 | 26 |
| random_gate_budget_0.10_seed018::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed018::external_hotpotqa | 0.440 | 0.200 | 26 |
| random_gate_budget_0.10_seed019::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.10_seed019::external_hotpotqa | 0.440 | 0.180 | 26 |
| random_gate_budget_0.10_seed020::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.10_seed020::external_hotpotqa | 0.460 | 0.180 | 25 |
| random_gate_budget_0.10_seed021::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed021::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.10_seed022::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.10_seed022::external_hotpotqa | 0.420 | 0.200 | 25 |
| random_gate_budget_0.10_seed023::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed023::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.10_seed024::external_2wiki | 0.380 | 0.240 | 25 |
| random_gate_budget_0.10_seed024::external_hotpotqa | 0.440 | 0.260 | 24 |
| random_gate_budget_0.10_seed025::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.10_seed025::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed026::external_2wiki | 0.360 | 0.280 | 24 |
| random_gate_budget_0.10_seed026::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed027::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.10_seed027::external_hotpotqa | 0.420 | 0.180 | 27 |
| random_gate_budget_0.10_seed028::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.10_seed028::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.10_seed029::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.10_seed029::external_hotpotqa | 0.440 | 0.180 | 26 |
| random_gate_budget_0.10_seed030::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed030::external_hotpotqa | 0.460 | 0.160 | 26 |
| random_gate_budget_0.10_seed031::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed031::external_hotpotqa | 0.420 | 0.180 | 27 |
| random_gate_budget_0.10_seed032::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.10_seed032::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed033::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.10_seed033::external_hotpotqa | 0.440 | 0.200 | 25 |
| random_gate_budget_0.10_seed034::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed034::external_hotpotqa | 0.460 | 0.180 | 25 |
| random_gate_budget_0.10_seed035::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.10_seed035::external_hotpotqa | 0.440 | 0.240 | 25 |
| random_gate_budget_0.10_seed036::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.10_seed036::external_hotpotqa | 0.400 | 0.200 | 26 |
| random_gate_budget_0.10_seed037::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.10_seed037::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.10_seed038::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed038::external_hotpotqa | 0.440 | 0.140 | 27 |
| random_gate_budget_0.10_seed039::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.10_seed039::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed040::external_2wiki | 0.380 | 0.280 | 23 |
| random_gate_budget_0.10_seed040::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed041::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed041::external_hotpotqa | 0.440 | 0.180 | 26 |
| random_gate_budget_0.10_seed042::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed042::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.10_seed043::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed043::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.10_seed044::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.10_seed044::external_hotpotqa | 0.400 | 0.220 | 27 |
| random_gate_budget_0.10_seed045::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.10_seed045::external_hotpotqa | 0.400 | 0.220 | 26 |
| random_gate_budget_0.10_seed046::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.10_seed046::external_hotpotqa | 0.480 | 0.220 | 23 |
| random_gate_budget_0.10_seed047::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed047::external_hotpotqa | 0.380 | 0.180 | 29 |
| random_gate_budget_0.10_seed048::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.10_seed048::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.10_seed049::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.10_seed049::external_hotpotqa | 0.420 | 0.240 | 25 |
| random_gate_budget_0.10_seed050::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.10_seed050::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.10_seed051::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed051::external_hotpotqa | 0.440 | 0.200 | 25 |
| random_gate_budget_0.10_seed052::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.10_seed052::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.10_seed053::external_2wiki | 0.420 | 0.280 | 21 |
| random_gate_budget_0.10_seed053::external_hotpotqa | 0.380 | 0.200 | 27 |
| random_gate_budget_0.10_seed054::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.10_seed054::external_hotpotqa | 0.440 | 0.180 | 26 |
| random_gate_budget_0.10_seed055::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.10_seed055::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.10_seed056::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.10_seed056::external_hotpotqa | 0.440 | 0.200 | 25 |
| random_gate_budget_0.10_seed057::external_2wiki | 0.380 | 0.280 | 23 |
| random_gate_budget_0.10_seed057::external_hotpotqa | 0.400 | 0.200 | 26 |
| random_gate_budget_0.10_seed058::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed058::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed059::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.10_seed059::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.10_seed060::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed060::external_hotpotqa | 0.420 | 0.240 | 25 |
| random_gate_budget_0.10_seed061::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.10_seed061::external_hotpotqa | 0.440 | 0.200 | 26 |
| random_gate_budget_0.10_seed062::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed062::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.10_seed063::external_2wiki | 0.400 | 0.280 | 22 |
| random_gate_budget_0.10_seed063::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.10_seed064::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.10_seed064::external_hotpotqa | 0.420 | 0.160 | 27 |
| random_gate_budget_0.10_seed065::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.10_seed065::external_hotpotqa | 0.440 | 0.160 | 26 |
| random_gate_budget_0.10_seed066::external_2wiki | 0.400 | 0.220 | 25 |
| random_gate_budget_0.10_seed066::external_hotpotqa | 0.460 | 0.180 | 25 |
| random_gate_budget_0.10_seed067::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.10_seed067::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed068::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed068::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed069::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.10_seed069::external_hotpotqa | 0.420 | 0.180 | 27 |
| random_gate_budget_0.10_seed070::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.10_seed070::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.10_seed071::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.10_seed071::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed072::external_2wiki | 0.400 | 0.220 | 25 |
| random_gate_budget_0.10_seed072::external_hotpotqa | 0.460 | 0.160 | 25 |
| random_gate_budget_0.10_seed073::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed073::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.10_seed074::external_2wiki | 0.360 | 0.280 | 24 |
| random_gate_budget_0.10_seed074::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed075::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed075::external_hotpotqa | 0.400 | 0.200 | 27 |
| random_gate_budget_0.10_seed076::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.10_seed076::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.10_seed077::external_2wiki | 0.380 | 0.280 | 23 |
| random_gate_budget_0.10_seed077::external_hotpotqa | 0.400 | 0.220 | 26 |
| random_gate_budget_0.10_seed078::external_2wiki | 0.460 | 0.200 | 23 |
| random_gate_budget_0.10_seed078::external_hotpotqa | 0.380 | 0.240 | 27 |
| random_gate_budget_0.10_seed079::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed079::external_hotpotqa | 0.460 | 0.160 | 26 |
| random_gate_budget_0.10_seed080::external_2wiki | 0.400 | 0.280 | 22 |
| random_gate_budget_0.10_seed080::external_hotpotqa | 0.440 | 0.240 | 24 |
| random_gate_budget_0.10_seed081::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.10_seed081::external_hotpotqa | 0.480 | 0.220 | 23 |
| random_gate_budget_0.10_seed082::external_2wiki | 0.380 | 0.280 | 23 |
| random_gate_budget_0.10_seed082::external_hotpotqa | 0.440 | 0.200 | 25 |
| random_gate_budget_0.10_seed083::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.10_seed083::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.10_seed084::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.10_seed084::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.10_seed085::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.10_seed085::external_hotpotqa | 0.420 | 0.140 | 28 |
| random_gate_budget_0.10_seed086::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.10_seed086::external_hotpotqa | 0.440 | 0.180 | 26 |
| random_gate_budget_0.10_seed087::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.10_seed087::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.10_seed088::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed088::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.10_seed089::external_2wiki | 0.500 | 0.220 | 20 |
| random_gate_budget_0.10_seed089::external_hotpotqa | 0.440 | 0.180 | 26 |
| random_gate_budget_0.10_seed090::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.10_seed090::external_hotpotqa | 0.400 | 0.200 | 26 |
| random_gate_budget_0.10_seed091::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed091::external_hotpotqa | 0.480 | 0.240 | 22 |
| random_gate_budget_0.10_seed092::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.10_seed092::external_hotpotqa | 0.400 | 0.240 | 26 |
| random_gate_budget_0.10_seed093::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.10_seed093::external_hotpotqa | 0.480 | 0.220 | 23 |
| random_gate_budget_0.10_seed094::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.10_seed094::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.10_seed095::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed095::external_hotpotqa | 0.420 | 0.220 | 26 |
| random_gate_budget_0.10_seed096::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.10_seed096::external_hotpotqa | 0.400 | 0.200 | 27 |
| random_gate_budget_0.10_seed097::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.10_seed097::external_hotpotqa | 0.420 | 0.180 | 27 |
| random_gate_budget_0.10_seed098::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.10_seed098::external_hotpotqa | 0.480 | 0.220 | 23 |
| random_gate_budget_0.10_seed099::external_2wiki | 0.400 | 0.220 | 25 |
| random_gate_budget_0.10_seed099::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.25_seed000::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.25_seed000::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.25_seed001::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.25_seed001::external_hotpotqa | 0.460 | 0.180 | 26 |
| random_gate_budget_0.25_seed002::external_2wiki | 0.420 | 0.280 | 21 |
| random_gate_budget_0.25_seed002::external_hotpotqa | 0.500 | 0.200 | 24 |
| random_gate_budget_0.25_seed003::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed003::external_hotpotqa | 0.440 | 0.240 | 25 |
| random_gate_budget_0.25_seed004::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.25_seed004::external_hotpotqa | 0.440 | 0.240 | 24 |
| random_gate_budget_0.25_seed005::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed005::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.25_seed006::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.25_seed006::external_hotpotqa | 0.520 | 0.240 | 22 |
| random_gate_budget_0.25_seed007::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.25_seed007::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.25_seed008::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.25_seed008::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.25_seed009::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.25_seed009::external_hotpotqa | 0.480 | 0.160 | 26 |
| random_gate_budget_0.25_seed010::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.25_seed010::external_hotpotqa | 0.400 | 0.220 | 27 |
| random_gate_budget_0.25_seed011::external_2wiki | 0.460 | 0.260 | 20 |
| random_gate_budget_0.25_seed011::external_hotpotqa | 0.460 | 0.240 | 25 |
| random_gate_budget_0.25_seed012::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.25_seed012::external_hotpotqa | 0.480 | 0.140 | 26 |
| random_gate_budget_0.25_seed013::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.25_seed013::external_hotpotqa | 0.440 | 0.240 | 25 |
| random_gate_budget_0.25_seed014::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.25_seed014::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.25_seed015::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.25_seed015::external_hotpotqa | 0.420 | 0.180 | 27 |
| random_gate_budget_0.25_seed016::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.25_seed016::external_hotpotqa | 0.440 | 0.240 | 24 |
| random_gate_budget_0.25_seed017::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed017::external_hotpotqa | 0.460 | 0.180 | 25 |
| random_gate_budget_0.25_seed018::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.25_seed018::external_hotpotqa | 0.420 | 0.200 | 27 |
| random_gate_budget_0.25_seed019::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed019::external_hotpotqa | 0.480 | 0.180 | 25 |
| random_gate_budget_0.25_seed020::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.25_seed020::external_hotpotqa | 0.480 | 0.200 | 24 |
| random_gate_budget_0.25_seed021::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.25_seed021::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.25_seed022::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed022::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.25_seed023::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.25_seed023::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.25_seed024::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.25_seed024::external_hotpotqa | 0.440 | 0.240 | 24 |
| random_gate_budget_0.25_seed025::external_2wiki | 0.420 | 0.200 | 25 |
| random_gate_budget_0.25_seed025::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.25_seed026::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.25_seed026::external_hotpotqa | 0.460 | 0.160 | 26 |
| random_gate_budget_0.25_seed027::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.25_seed027::external_hotpotqa | 0.460 | 0.200 | 26 |
| random_gate_budget_0.25_seed028::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.25_seed028::external_hotpotqa | 0.460 | 0.200 | 26 |
| random_gate_budget_0.25_seed029::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.25_seed029::external_hotpotqa | 0.480 | 0.200 | 24 |
| random_gate_budget_0.25_seed030::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.25_seed030::external_hotpotqa | 0.480 | 0.180 | 25 |
| random_gate_budget_0.25_seed031::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.25_seed031::external_hotpotqa | 0.480 | 0.160 | 25 |
| random_gate_budget_0.25_seed032::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed032::external_hotpotqa | 0.440 | 0.220 | 26 |
| random_gate_budget_0.25_seed033::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.25_seed033::external_hotpotqa | 0.440 | 0.200 | 26 |
| random_gate_budget_0.25_seed034::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.25_seed034::external_hotpotqa | 0.480 | 0.220 | 23 |
| random_gate_budget_0.25_seed035::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed035::external_hotpotqa | 0.460 | 0.260 | 24 |
| random_gate_budget_0.25_seed036::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.25_seed036::external_hotpotqa | 0.360 | 0.200 | 28 |
| random_gate_budget_0.25_seed037::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.25_seed037::external_hotpotqa | 0.500 | 0.200 | 24 |
| random_gate_budget_0.25_seed038::external_2wiki | 0.380 | 0.260 | 24 |
| random_gate_budget_0.25_seed038::external_hotpotqa | 0.460 | 0.180 | 26 |
| random_gate_budget_0.25_seed039::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.25_seed039::external_hotpotqa | 0.420 | 0.220 | 26 |
| random_gate_budget_0.25_seed040::external_2wiki | 0.460 | 0.260 | 20 |
| random_gate_budget_0.25_seed040::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.25_seed041::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.25_seed041::external_hotpotqa | 0.500 | 0.220 | 22 |
| random_gate_budget_0.25_seed042::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.25_seed042::external_hotpotqa | 0.520 | 0.220 | 22 |
| random_gate_budget_0.25_seed043::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.25_seed043::external_hotpotqa | 0.460 | 0.260 | 23 |
| random_gate_budget_0.25_seed044::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.25_seed044::external_hotpotqa | 0.460 | 0.240 | 25 |
| random_gate_budget_0.25_seed045::external_2wiki | 0.420 | 0.280 | 21 |
| random_gate_budget_0.25_seed045::external_hotpotqa | 0.480 | 0.240 | 23 |
| random_gate_budget_0.25_seed046::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.25_seed046::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.25_seed047::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.25_seed047::external_hotpotqa | 0.460 | 0.160 | 27 |
| random_gate_budget_0.25_seed048::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.25_seed048::external_hotpotqa | 0.440 | 0.260 | 24 |
| random_gate_budget_0.25_seed049::external_2wiki | 0.460 | 0.200 | 23 |
| random_gate_budget_0.25_seed049::external_hotpotqa | 0.420 | 0.220 | 26 |
| random_gate_budget_0.25_seed050::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.25_seed050::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.25_seed051::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed051::external_hotpotqa | 0.420 | 0.240 | 25 |
| random_gate_budget_0.25_seed052::external_2wiki | 0.480 | 0.280 | 18 |
| random_gate_budget_0.25_seed052::external_hotpotqa | 0.460 | 0.140 | 27 |
| random_gate_budget_0.25_seed053::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.25_seed053::external_hotpotqa | 0.460 | 0.200 | 24 |
| random_gate_budget_0.25_seed054::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.25_seed054::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.25_seed055::external_2wiki | 0.440 | 0.200 | 24 |
| random_gate_budget_0.25_seed055::external_hotpotqa | 0.480 | 0.260 | 22 |
| random_gate_budget_0.25_seed056::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.25_seed056::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.25_seed057::external_2wiki | 0.420 | 0.280 | 21 |
| random_gate_budget_0.25_seed057::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.25_seed058::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.25_seed058::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.25_seed059::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.25_seed059::external_hotpotqa | 0.500 | 0.260 | 22 |
| random_gate_budget_0.25_seed060::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed060::external_hotpotqa | 0.480 | 0.240 | 23 |
| random_gate_budget_0.25_seed061::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed061::external_hotpotqa | 0.460 | 0.180 | 26 |
| random_gate_budget_0.25_seed062::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.25_seed062::external_hotpotqa | 0.440 | 0.200 | 26 |
| random_gate_budget_0.25_seed063::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed063::external_hotpotqa | 0.500 | 0.180 | 24 |
| random_gate_budget_0.25_seed064::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.25_seed064::external_hotpotqa | 0.480 | 0.160 | 25 |
| random_gate_budget_0.25_seed065::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.25_seed065::external_hotpotqa | 0.460 | 0.160 | 26 |
| random_gate_budget_0.25_seed066::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed066::external_hotpotqa | 0.520 | 0.180 | 24 |
| random_gate_budget_0.25_seed067::external_2wiki | 0.460 | 0.260 | 20 |
| random_gate_budget_0.25_seed067::external_hotpotqa | 0.440 | 0.240 | 24 |
| random_gate_budget_0.25_seed068::external_2wiki | 0.380 | 0.240 | 25 |
| random_gate_budget_0.25_seed068::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.25_seed069::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed069::external_hotpotqa | 0.480 | 0.160 | 26 |
| random_gate_budget_0.25_seed070::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.25_seed070::external_hotpotqa | 0.420 | 0.220 | 26 |
| random_gate_budget_0.25_seed071::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.25_seed071::external_hotpotqa | 0.480 | 0.240 | 23 |
| random_gate_budget_0.25_seed072::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed072::external_hotpotqa | 0.480 | 0.160 | 25 |
| random_gate_budget_0.25_seed073::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.25_seed073::external_hotpotqa | 0.460 | 0.180 | 25 |
| random_gate_budget_0.25_seed074::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.25_seed074::external_hotpotqa | 0.460 | 0.180 | 25 |
| random_gate_budget_0.25_seed075::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.25_seed075::external_hotpotqa | 0.500 | 0.240 | 22 |
| random_gate_budget_0.25_seed076::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed076::external_hotpotqa | 0.500 | 0.240 | 23 |
| random_gate_budget_0.25_seed077::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.25_seed077::external_hotpotqa | 0.440 | 0.200 | 26 |
| random_gate_budget_0.25_seed078::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.25_seed078::external_hotpotqa | 0.400 | 0.240 | 26 |
| random_gate_budget_0.25_seed079::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed079::external_hotpotqa | 0.520 | 0.200 | 23 |
| random_gate_budget_0.25_seed080::external_2wiki | 0.460 | 0.260 | 20 |
| random_gate_budget_0.25_seed080::external_hotpotqa | 0.460 | 0.220 | 25 |
| random_gate_budget_0.25_seed081::external_2wiki | 0.400 | 0.260 | 23 |
| random_gate_budget_0.25_seed081::external_hotpotqa | 0.480 | 0.260 | 22 |
| random_gate_budget_0.25_seed082::external_2wiki | 0.400 | 0.240 | 24 |
| random_gate_budget_0.25_seed082::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.25_seed083::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.25_seed083::external_hotpotqa | 0.440 | 0.200 | 25 |
| random_gate_budget_0.25_seed084::external_2wiki | 0.420 | 0.260 | 22 |
| random_gate_budget_0.25_seed084::external_hotpotqa | 0.480 | 0.200 | 25 |
| random_gate_budget_0.25_seed085::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.25_seed085::external_hotpotqa | 0.420 | 0.180 | 27 |
| random_gate_budget_0.25_seed086::external_2wiki | 0.420 | 0.240 | 23 |
| random_gate_budget_0.25_seed086::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.25_seed087::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.25_seed087::external_hotpotqa | 0.440 | 0.160 | 26 |
| random_gate_budget_0.25_seed088::external_2wiki | 0.460 | 0.260 | 20 |
| random_gate_budget_0.25_seed088::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.25_seed089::external_2wiki | 0.520 | 0.200 | 20 |
| random_gate_budget_0.25_seed089::external_hotpotqa | 0.420 | 0.200 | 26 |
| random_gate_budget_0.25_seed090::external_2wiki | 0.420 | 0.220 | 24 |
| random_gate_budget_0.25_seed090::external_hotpotqa | 0.480 | 0.180 | 24 |
| random_gate_budget_0.25_seed091::external_2wiki | 0.440 | 0.260 | 21 |
| random_gate_budget_0.25_seed091::external_hotpotqa | 0.440 | 0.240 | 24 |
| random_gate_budget_0.25_seed092::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.25_seed092::external_hotpotqa | 0.460 | 0.220 | 24 |
| random_gate_budget_0.25_seed093::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed093::external_hotpotqa | 0.460 | 0.160 | 26 |
| random_gate_budget_0.25_seed094::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed094::external_hotpotqa | 0.460 | 0.200 | 24 |
| random_gate_budget_0.25_seed095::external_2wiki | 0.500 | 0.220 | 20 |
| random_gate_budget_0.25_seed095::external_hotpotqa | 0.480 | 0.280 | 22 |
| random_gate_budget_0.25_seed096::external_2wiki | 0.500 | 0.220 | 20 |
| random_gate_budget_0.25_seed096::external_hotpotqa | 0.440 | 0.160 | 27 |
| random_gate_budget_0.25_seed097::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.25_seed097::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.25_seed098::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed098::external_hotpotqa | 0.460 | 0.220 | 25 |
| random_gate_budget_0.25_seed099::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.25_seed099::external_hotpotqa | 0.520 | 0.220 | 22 |
| random_gate_budget_0.40_seed000::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.40_seed000::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed001::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed001::external_hotpotqa | 0.460 | 0.180 | 26 |
| random_gate_budget_0.40_seed002::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed002::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.40_seed003::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed003::external_hotpotqa | 0.460 | 0.220 | 25 |
| random_gate_budget_0.40_seed004::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.40_seed004::external_hotpotqa | 0.440 | 0.240 | 25 |
| random_gate_budget_0.40_seed005::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed005::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed006::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed006::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed007::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.40_seed007::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed008::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed008::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed009::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed009::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed010::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.40_seed010::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed011::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed011::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed012::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed012::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed013::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed013::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed014::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.40_seed014::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed015::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed015::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.40_seed016::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed016::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed017::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed017::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed018::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed018::external_hotpotqa | 0.460 | 0.180 | 26 |
| random_gate_budget_0.40_seed019::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.40_seed019::external_hotpotqa | 0.460 | 0.160 | 26 |
| random_gate_budget_0.40_seed020::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed020::external_hotpotqa | 0.480 | 0.240 | 23 |
| random_gate_budget_0.40_seed021::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed021::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed022::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed022::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed023::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed023::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed024::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed024::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed025::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed025::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.40_seed026::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed026::external_hotpotqa | 0.480 | 0.180 | 25 |
| random_gate_budget_0.40_seed027::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed027::external_hotpotqa | 0.500 | 0.200 | 24 |
| random_gate_budget_0.40_seed028::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed028::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed029::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed029::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.40_seed030::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed030::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed031::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.40_seed031::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed032::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed032::external_hotpotqa | 0.440 | 0.240 | 25 |
| random_gate_budget_0.40_seed033::external_2wiki | 0.520 | 0.200 | 20 |
| random_gate_budget_0.40_seed033::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed034::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.40_seed034::external_hotpotqa | 0.480 | 0.200 | 25 |
| random_gate_budget_0.40_seed035::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.40_seed035::external_hotpotqa | 0.480 | 0.240 | 23 |
| random_gate_budget_0.40_seed036::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed036::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed037::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed037::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.40_seed038::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.40_seed038::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed039::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.40_seed039::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.40_seed040::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed040::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed041::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.40_seed041::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed042::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed042::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed043::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed043::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed044::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed044::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed045::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.40_seed045::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed046::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.40_seed046::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed047::external_2wiki | 0.480 | 0.200 | 22 |
| random_gate_budget_0.40_seed047::external_hotpotqa | 0.480 | 0.200 | 25 |
| random_gate_budget_0.40_seed048::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed048::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed049::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed049::external_hotpotqa | 0.440 | 0.180 | 27 |
| random_gate_budget_0.40_seed050::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed050::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed051::external_2wiki | 0.440 | 0.220 | 23 |
| random_gate_budget_0.40_seed051::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed052::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed052::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed053::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed053::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed054::external_2wiki | 0.460 | 0.240 | 21 |
| random_gate_budget_0.40_seed054::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed055::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed055::external_hotpotqa | 0.500 | 0.240 | 22 |
| random_gate_budget_0.40_seed056::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed056::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed057::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed057::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed058::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed058::external_hotpotqa | 0.480 | 0.180 | 25 |
| random_gate_budget_0.40_seed059::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed059::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed060::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.40_seed060::external_hotpotqa | 0.500 | 0.240 | 22 |
| random_gate_budget_0.40_seed061::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed061::external_hotpotqa | 0.460 | 0.220 | 25 |
| random_gate_budget_0.40_seed062::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.40_seed062::external_hotpotqa | 0.480 | 0.200 | 25 |
| random_gate_budget_0.40_seed063::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed063::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed064::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed064::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.40_seed065::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed065::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed066::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed066::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.40_seed067::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed067::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed068::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed068::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed069::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed069::external_hotpotqa | 0.500 | 0.220 | 24 |
| random_gate_budget_0.40_seed070::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed070::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.40_seed071::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed071::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed072::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed072::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.40_seed073::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed073::external_hotpotqa | 0.460 | 0.200 | 25 |
| random_gate_budget_0.40_seed074::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed074::external_hotpotqa | 0.480 | 0.200 | 24 |
| random_gate_budget_0.40_seed075::external_2wiki | 0.500 | 0.220 | 20 |
| random_gate_budget_0.40_seed075::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed076::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed076::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed077::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed077::external_hotpotqa | 0.440 | 0.220 | 26 |
| random_gate_budget_0.40_seed078::external_2wiki | 0.500 | 0.220 | 20 |
| random_gate_budget_0.40_seed078::external_hotpotqa | 0.460 | 0.280 | 23 |
| random_gate_budget_0.40_seed079::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed079::external_hotpotqa | 0.440 | 0.200 | 26 |
| random_gate_budget_0.40_seed080::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.40_seed080::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed081::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed081::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed082::external_2wiki | 0.440 | 0.240 | 22 |
| random_gate_budget_0.40_seed082::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed083::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed083::external_hotpotqa | 0.500 | 0.220 | 23 |
| random_gate_budget_0.40_seed084::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.40_seed084::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed085::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed085::external_hotpotqa | 0.480 | 0.200 | 25 |
| random_gate_budget_0.40_seed086::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed086::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed087::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed087::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed088::external_2wiki | 0.500 | 0.240 | 19 |
| random_gate_budget_0.40_seed088::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed089::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed089::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed090::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed090::external_hotpotqa | 0.480 | 0.200 | 24 |
| random_gate_budget_0.40_seed091::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed091::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed092::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed092::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed093::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed093::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed094::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed094::external_hotpotqa | 0.440 | 0.220 | 25 |
| random_gate_budget_0.40_seed095::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed095::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed096::external_2wiki | 0.480 | 0.240 | 20 |
| random_gate_budget_0.40_seed096::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed097::external_2wiki | 0.460 | 0.220 | 22 |
| random_gate_budget_0.40_seed097::external_hotpotqa | 0.460 | 0.240 | 24 |
| random_gate_budget_0.40_seed098::external_2wiki | 0.500 | 0.200 | 21 |
| random_gate_budget_0.40_seed098::external_hotpotqa | 0.480 | 0.220 | 24 |
| random_gate_budget_0.40_seed099::external_2wiki | 0.480 | 0.220 | 21 |
| random_gate_budget_0.40_seed099::external_hotpotqa | 0.500 | 0.200 | 24 |
| risk_guided_doc_patch_k2::external_2wiki | 0.480 | 0.220 | 21 |
| risk_guided_doc_patch_k2::external_hotpotqa | 0.480 | 0.220 | 24 |
| safe_gate_budget_0.10::external_2wiki | 0.380 | 0.240 | 25 |
| safe_gate_budget_0.10::external_hotpotqa | 0.460 | 0.220 | 24 |
| safe_gate_budget_0.25::external_2wiki | 0.420 | 0.240 | 23 |
| safe_gate_budget_0.25::external_hotpotqa | 0.460 | 0.220 | 24 |
| safe_gate_budget_0.40::external_2wiki | 0.480 | 0.220 | 21 |
| safe_gate_budget_0.40::external_hotpotqa | 0.480 | 0.220 | 24 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_4c1772720bb011ebab90acde48001122 | external_2wiki | 5.31846 | `Maximilian Eugen` | `Princess Leopodine of Löwenstein- Wertheim- Roch` | `Charles I of Austria` |
| hotpotqa_4835 | external_hotpotqa | 4.42292 | `Wren` | `Thalassery` | `East Knoyle` |
| 2wiki_350ec8b80bde11eba7f7acde48001122 | external_2wiki | 4.21525 | `Harold R. Atteridge` | `Atlantic City, New Jersey` | `Atlantic City, New Jersey` |
| 2wiki_34c3dd940bde11eba7f7acde48001122 | external_2wiki | 3.77263 | `Loiret department, north-central France` | `Allada` | `Allada` |
| 2wiki_21832f3c0bde11eba7f7acde48001122 | external_2wiki | 3.70964 | `Italy` | `Burgundian castle` | `Italy` |
| hotpotqa_2482 | external_hotpotqa | 3.64245 | `Chuck Long played for the Detroit Lions and the Los Angeles Rams professionally.` | `The 2007 San Diego State Aztecs played for the San` | `Detroit Lions and the Los Angeles Rams` |
| 2wiki_9b8278a20bdd11eba7f7acde48001122 | external_2wiki | 2.89492 | `Hastings, Minnesota` | `Fredrikstad` | `Hastings, Minnesota` |
| 2wiki_d60529440baf11ebab90acde48001122 | external_2wiki | 2.66488 | `Andrzej Gawroński` | `The uncle of Nawrahta of Kanni is the late actor.` | `Yazathingyan` |
| hotpotqa_0638 | external_hotpotqa | 2.50483 | `GSN Live` | `National Geographic Channel` | `SBS` |
| hotpotqa_1991 | external_hotpotqa | 2.4865 | `24` | `Four` | `24` |

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
