# Budget Gate Failure Analysis

## Pareto Summary

| target | actual | safe equiv | random mean | percentile | changed+wrong |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.102 | 0.930 | 0.894 | 0.990 | 5 |
| 0.25 | 0.251 | 0.950 | 0.917 | 0.970 | 3 |
| 0.40 | 0.400 | 0.960 | 0.941 | 0.960 | 3 |

# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.910 | 0.930 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.880 | 0.860 | 0.882 | 11 | 0.000 |
| random_gate_budget_0.10_seed000 | 0.900 | 0.870 | 0.891 | 9 | 0.105 |
| random_gate_budget_0.10_seed001 | 0.900 | 0.860 | 0.883 | 9 | 0.100 |
| random_gate_budget_0.10_seed002 | 0.870 | 0.870 | 0.892 | 11 | 0.115 |
| random_gate_budget_0.10_seed003 | 0.890 | 0.840 | 0.869 | 11 | 0.111 |
| random_gate_budget_0.10_seed004 | 0.880 | 0.860 | 0.884 | 11 | 0.100 |
| random_gate_budget_0.10_seed005 | 0.920 | 0.870 | 0.895 | 8 | 0.100 |
| random_gate_budget_0.10_seed006 | 0.890 | 0.870 | 0.892 | 10 | 0.111 |
| random_gate_budget_0.10_seed007 | 0.880 | 0.870 | 0.888 | 10 | 0.103 |
| random_gate_budget_0.10_seed008 | 0.880 | 0.850 | 0.877 | 11 | 0.113 |
| random_gate_budget_0.10_seed009 | 0.900 | 0.870 | 0.891 | 9 | 0.103 |
| random_gate_budget_0.10_seed010 | 0.890 | 0.870 | 0.892 | 10 | 0.104 |
| random_gate_budget_0.10_seed011 | 0.910 | 0.890 | 0.910 | 7 | 0.106 |
| random_gate_budget_0.10_seed012 | 0.890 | 0.860 | 0.884 | 10 | 0.102 |
| random_gate_budget_0.10_seed013 | 0.880 | 0.860 | 0.882 | 11 | 0.109 |
| random_gate_budget_0.10_seed014 | 0.890 | 0.870 | 0.892 | 10 | 0.110 |
| random_gate_budget_0.10_seed015 | 0.880 | 0.860 | 0.882 | 11 | 0.108 |
| random_gate_budget_0.10_seed016 | 0.870 | 0.850 | 0.874 | 12 | 0.109 |
| random_gate_budget_0.10_seed017 | 0.920 | 0.880 | 0.900 | 7 | 0.105 |
| random_gate_budget_0.10_seed018 | 0.910 | 0.880 | 0.895 | 8 | 0.106 |
| random_gate_budget_0.10_seed019 | 0.880 | 0.860 | 0.882 | 11 | 0.117 |
| random_gate_budget_0.10_seed020 | 0.920 | 0.890 | 0.909 | 7 | 0.110 |
| random_gate_budget_0.10_seed021 | 0.900 | 0.850 | 0.872 | 10 | 0.096 |
| random_gate_budget_0.10_seed022 | 0.880 | 0.860 | 0.882 | 11 | 0.097 |
| random_gate_budget_0.10_seed023 | 0.890 | 0.860 | 0.880 | 10 | 0.099 |
| random_gate_budget_0.10_seed024 | 0.890 | 0.860 | 0.877 | 10 | 0.099 |
| random_gate_budget_0.10_seed025 | 0.890 | 0.870 | 0.892 | 10 | 0.107 |
| random_gate_budget_0.10_seed026 | 0.910 | 0.890 | 0.912 | 8 | 0.100 |
| random_gate_budget_0.10_seed027 | 0.900 | 0.860 | 0.877 | 10 | 0.101 |
| random_gate_budget_0.10_seed028 | 0.910 | 0.860 | 0.877 | 9 | 0.112 |
| random_gate_budget_0.10_seed029 | 0.880 | 0.860 | 0.882 | 11 | 0.100 |
| random_gate_budget_0.10_seed030 | 0.880 | 0.860 | 0.884 | 11 | 0.099 |
| random_gate_budget_0.10_seed031 | 0.880 | 0.870 | 0.890 | 10 | 0.104 |
| random_gate_budget_0.10_seed032 | 0.880 | 0.860 | 0.882 | 11 | 0.100 |
| random_gate_budget_0.10_seed033 | 0.890 | 0.860 | 0.887 | 10 | 0.106 |
| random_gate_budget_0.10_seed034 | 0.880 | 0.860 | 0.884 | 11 | 0.102 |
| random_gate_budget_0.10_seed035 | 0.870 | 0.870 | 0.890 | 11 | 0.102 |
| random_gate_budget_0.10_seed036 | 0.880 | 0.860 | 0.884 | 11 | 0.110 |
| random_gate_budget_0.10_seed037 | 0.880 | 0.860 | 0.882 | 11 | 0.105 |
| random_gate_budget_0.10_seed038 | 0.880 | 0.850 | 0.877 | 11 | 0.108 |
| random_gate_budget_0.10_seed039 | 0.890 | 0.870 | 0.892 | 10 | 0.100 |
| random_gate_budget_0.10_seed040 | 0.880 | 0.860 | 0.882 | 11 | 0.093 |
| random_gate_budget_0.10_seed041 | 0.870 | 0.850 | 0.874 | 12 | 0.107 |
| random_gate_budget_0.10_seed042 | 0.890 | 0.860 | 0.884 | 10 | 0.110 |
| random_gate_budget_0.10_seed043 | 0.880 | 0.860 | 0.882 | 11 | 0.113 |
| random_gate_budget_0.10_seed044 | 0.910 | 0.860 | 0.890 | 8 | 0.107 |
| random_gate_budget_0.10_seed045 | 0.900 | 0.900 | 0.915 | 8 | 0.103 |
| random_gate_budget_0.10_seed046 | 0.890 | 0.870 | 0.894 | 10 | 0.109 |
| random_gate_budget_0.10_seed047 | 0.890 | 0.850 | 0.872 | 11 | 0.102 |
| random_gate_budget_0.10_seed048 | 0.900 | 0.870 | 0.891 | 9 | 0.110 |
| random_gate_budget_0.10_seed049 | 0.910 | 0.870 | 0.897 | 8 | 0.103 |
| random_gate_budget_0.10_seed050 | 0.900 | 0.870 | 0.889 | 9 | 0.108 |
| random_gate_budget_0.10_seed051 | 0.870 | 0.850 | 0.874 | 12 | 0.102 |
| random_gate_budget_0.10_seed052 | 0.880 | 0.860 | 0.884 | 11 | 0.113 |
| random_gate_budget_0.10_seed053 | 0.900 | 0.860 | 0.882 | 10 | 0.108 |
| random_gate_budget_0.10_seed054 | 0.920 | 0.880 | 0.899 | 8 | 0.107 |
| random_gate_budget_0.10_seed055 | 0.920 | 0.880 | 0.897 | 7 | 0.113 |
| random_gate_budget_0.10_seed056 | 0.890 | 0.870 | 0.889 | 10 | 0.103 |
| random_gate_budget_0.10_seed057 | 0.900 | 0.870 | 0.889 | 9 | 0.102 |
| random_gate_budget_0.10_seed058 | 0.900 | 0.870 | 0.892 | 9 | 0.108 |
| random_gate_budget_0.10_seed059 | 0.900 | 0.860 | 0.886 | 9 | 0.099 |
| random_gate_budget_0.10_seed060 | 0.900 | 0.880 | 0.897 | 9 | 0.111 |
| random_gate_budget_0.10_seed061 | 0.910 | 0.860 | 0.877 | 8 | 0.106 |
| random_gate_budget_0.10_seed062 | 0.880 | 0.880 | 0.900 | 10 | 0.109 |
| random_gate_budget_0.10_seed063 | 0.910 | 0.860 | 0.882 | 8 | 0.104 |
| random_gate_budget_0.10_seed064 | 0.900 | 0.860 | 0.877 | 10 | 0.111 |
| random_gate_budget_0.10_seed065 | 0.880 | 0.840 | 0.866 | 12 | 0.111 |
| random_gate_budget_0.10_seed066 | 0.890 | 0.860 | 0.887 | 10 | 0.091 |
| random_gate_budget_0.10_seed067 | 0.890 | 0.870 | 0.892 | 10 | 0.094 |
| random_gate_budget_0.10_seed068 | 0.880 | 0.880 | 0.902 | 10 | 0.108 |
| random_gate_budget_0.10_seed069 | 0.910 | 0.890 | 0.912 | 8 | 0.110 |
| random_gate_budget_0.10_seed070 | 0.890 | 0.870 | 0.887 | 10 | 0.105 |
| random_gate_budget_0.10_seed071 | 0.900 | 0.870 | 0.895 | 9 | 0.107 |
| random_gate_budget_0.10_seed072 | 0.890 | 0.870 | 0.897 | 9 | 0.099 |
| random_gate_budget_0.10_seed073 | 0.880 | 0.880 | 0.900 | 10 | 0.104 |
| random_gate_budget_0.10_seed074 | 0.870 | 0.870 | 0.890 | 11 | 0.095 |
| random_gate_budget_0.10_seed075 | 0.910 | 0.870 | 0.897 | 8 | 0.104 |
| random_gate_budget_0.10_seed076 | 0.880 | 0.860 | 0.882 | 11 | 0.102 |
| random_gate_budget_0.10_seed077 | 0.910 | 0.860 | 0.879 | 9 | 0.099 |
| random_gate_budget_0.10_seed078 | 0.880 | 0.860 | 0.880 | 11 | 0.109 |
| random_gate_budget_0.10_seed079 | 0.890 | 0.850 | 0.879 | 10 | 0.105 |
| random_gate_budget_0.10_seed080 | 0.900 | 0.870 | 0.892 | 9 | 0.104 |
| random_gate_budget_0.10_seed081 | 0.890 | 0.860 | 0.885 | 10 | 0.102 |
| random_gate_budget_0.10_seed082 | 0.890 | 0.860 | 0.879 | 10 | 0.102 |
| random_gate_budget_0.10_seed083 | 0.880 | 0.860 | 0.882 | 11 | 0.105 |
| random_gate_budget_0.10_seed084 | 0.940 | 0.870 | 0.887 | 6 | 0.111 |
| random_gate_budget_0.10_seed085 | 0.910 | 0.870 | 0.891 | 8 | 0.106 |
| random_gate_budget_0.10_seed086 | 0.890 | 0.870 | 0.887 | 10 | 0.104 |
| random_gate_budget_0.10_seed087 | 0.910 | 0.890 | 0.912 | 8 | 0.106 |
| random_gate_budget_0.10_seed088 | 0.910 | 0.870 | 0.892 | 8 | 0.111 |
| random_gate_budget_0.10_seed089 | 0.920 | 0.900 | 0.917 | 7 | 0.110 |
| random_gate_budget_0.10_seed090 | 0.910 | 0.870 | 0.891 | 8 | 0.099 |
| random_gate_budget_0.10_seed091 | 0.900 | 0.870 | 0.897 | 9 | 0.101 |
| random_gate_budget_0.10_seed092 | 0.890 | 0.850 | 0.874 | 11 | 0.114 |
| random_gate_budget_0.10_seed093 | 0.920 | 0.870 | 0.892 | 7 | 0.103 |
| random_gate_budget_0.10_seed094 | 0.910 | 0.870 | 0.899 | 8 | 0.117 |
| random_gate_budget_0.10_seed095 | 0.890 | 0.860 | 0.887 | 10 | 0.106 |
| random_gate_budget_0.10_seed096 | 0.920 | 0.870 | 0.889 | 8 | 0.111 |
| random_gate_budget_0.10_seed097 | 0.910 | 0.880 | 0.905 | 8 | 0.110 |
| random_gate_budget_0.10_seed098 | 0.890 | 0.870 | 0.894 | 10 | 0.107 |
| random_gate_budget_0.10_seed099 | 0.910 | 0.860 | 0.882 | 9 | 0.102 |
| random_gate_budget_0.25_seed000 | 0.920 | 0.880 | 0.899 | 7 | 0.256 |
| random_gate_budget_0.25_seed001 | 0.940 | 0.860 | 0.884 | 6 | 0.261 |
| random_gate_budget_0.25_seed002 | 0.890 | 0.860 | 0.882 | 9 | 0.269 |
| random_gate_budget_0.25_seed003 | 0.930 | 0.860 | 0.879 | 7 | 0.271 |
| random_gate_budget_0.25_seed004 | 0.920 | 0.880 | 0.905 | 7 | 0.258 |
| random_gate_budget_0.25_seed005 | 0.930 | 0.870 | 0.899 | 7 | 0.266 |
| random_gate_budget_0.25_seed006 | 0.880 | 0.860 | 0.882 | 11 | 0.263 |
| random_gate_budget_0.25_seed007 | 0.900 | 0.890 | 0.908 | 8 | 0.262 |
| random_gate_budget_0.25_seed008 | 0.900 | 0.860 | 0.884 | 9 | 0.272 |
| random_gate_budget_0.25_seed009 | 0.950 | 0.870 | 0.889 | 5 | 0.263 |
| random_gate_budget_0.25_seed010 | 0.940 | 0.880 | 0.892 | 6 | 0.258 |
| random_gate_budget_0.25_seed011 | 0.950 | 0.890 | 0.905 | 4 | 0.264 |
| random_gate_budget_0.25_seed012 | 0.890 | 0.870 | 0.894 | 9 | 0.265 |
| random_gate_budget_0.25_seed013 | 0.900 | 0.880 | 0.907 | 8 | 0.279 |
| random_gate_budget_0.25_seed014 | 0.950 | 0.890 | 0.907 | 4 | 0.269 |
| random_gate_budget_0.25_seed015 | 0.910 | 0.870 | 0.887 | 8 | 0.267 |
| random_gate_budget_0.25_seed016 | 0.880 | 0.880 | 0.897 | 10 | 0.268 |
| random_gate_budget_0.25_seed017 | 0.930 | 0.890 | 0.912 | 6 | 0.264 |
| random_gate_budget_0.25_seed018 | 0.950 | 0.880 | 0.902 | 5 | 0.263 |
| random_gate_budget_0.25_seed019 | 0.920 | 0.880 | 0.904 | 7 | 0.267 |
| random_gate_budget_0.25_seed020 | 0.930 | 0.900 | 0.925 | 5 | 0.268 |
| random_gate_budget_0.25_seed021 | 0.890 | 0.860 | 0.882 | 10 | 0.256 |
| random_gate_budget_0.25_seed022 | 0.900 | 0.870 | 0.896 | 9 | 0.269 |
| random_gate_budget_0.25_seed023 | 0.890 | 0.880 | 0.898 | 9 | 0.256 |
| random_gate_budget_0.25_seed024 | 0.920 | 0.880 | 0.900 | 7 | 0.260 |
| random_gate_budget_0.25_seed025 | 0.940 | 0.890 | 0.907 | 5 | 0.265 |
| random_gate_budget_0.25_seed026 | 0.920 | 0.870 | 0.899 | 8 | 0.275 |
| random_gate_budget_0.25_seed027 | 0.920 | 0.860 | 0.877 | 8 | 0.260 |
| random_gate_budget_0.25_seed028 | 0.930 | 0.870 | 0.892 | 7 | 0.266 |
| random_gate_budget_0.25_seed029 | 0.920 | 0.890 | 0.912 | 7 | 0.265 |
| random_gate_budget_0.25_seed030 | 0.930 | 0.890 | 0.909 | 6 | 0.260 |
| random_gate_budget_0.25_seed031 | 0.910 | 0.870 | 0.890 | 8 | 0.267 |
| random_gate_budget_0.25_seed032 | 0.900 | 0.850 | 0.870 | 9 | 0.259 |
| random_gate_budget_0.25_seed033 | 0.920 | 0.880 | 0.900 | 7 | 0.260 |
| random_gate_budget_0.25_seed034 | 0.920 | 0.880 | 0.905 | 7 | 0.264 |
| random_gate_budget_0.25_seed035 | 0.930 | 0.870 | 0.894 | 6 | 0.261 |
| random_gate_budget_0.25_seed036 | 0.910 | 0.860 | 0.887 | 9 | 0.259 |
| random_gate_budget_0.25_seed037 | 0.900 | 0.870 | 0.888 | 9 | 0.266 |
| random_gate_budget_0.25_seed038 | 0.890 | 0.850 | 0.874 | 10 | 0.259 |
| random_gate_budget_0.25_seed039 | 0.930 | 0.880 | 0.905 | 6 | 0.259 |
| random_gate_budget_0.25_seed040 | 0.910 | 0.870 | 0.892 | 8 | 0.255 |
| random_gate_budget_0.25_seed041 | 0.910 | 0.870 | 0.896 | 8 | 0.262 |
| random_gate_budget_0.25_seed042 | 0.920 | 0.870 | 0.887 | 7 | 0.267 |
| random_gate_budget_0.25_seed043 | 0.920 | 0.860 | 0.886 | 7 | 0.266 |
| random_gate_budget_0.25_seed044 | 0.960 | 0.880 | 0.904 | 4 | 0.277 |
| random_gate_budget_0.25_seed045 | 0.910 | 0.900 | 0.918 | 7 | 0.258 |
| random_gate_budget_0.25_seed046 | 0.930 | 0.860 | 0.882 | 7 | 0.263 |
| random_gate_budget_0.25_seed047 | 0.910 | 0.850 | 0.869 | 9 | 0.270 |
| random_gate_budget_0.25_seed048 | 0.920 | 0.870 | 0.889 | 7 | 0.268 |
| random_gate_budget_0.25_seed049 | 0.910 | 0.880 | 0.909 | 7 | 0.261 |
| random_gate_budget_0.25_seed050 | 0.900 | 0.880 | 0.904 | 8 | 0.267 |
| random_gate_budget_0.25_seed051 | 0.900 | 0.850 | 0.874 | 10 | 0.259 |
| random_gate_budget_0.25_seed052 | 0.900 | 0.860 | 0.879 | 10 | 0.267 |
| random_gate_budget_0.25_seed053 | 0.910 | 0.860 | 0.882 | 9 | 0.264 |
| random_gate_budget_0.25_seed054 | 0.920 | 0.890 | 0.906 | 7 | 0.250 |
| random_gate_budget_0.25_seed055 | 0.930 | 0.880 | 0.902 | 6 | 0.271 |
| random_gate_budget_0.25_seed056 | 0.930 | 0.870 | 0.889 | 7 | 0.264 |
| random_gate_budget_0.25_seed057 | 0.920 | 0.860 | 0.884 | 7 | 0.261 |
| random_gate_budget_0.25_seed058 | 0.920 | 0.900 | 0.918 | 6 | 0.258 |
| random_gate_budget_0.25_seed059 | 0.930 | 0.860 | 0.889 | 6 | 0.262 |
| random_gate_budget_0.25_seed060 | 0.920 | 0.890 | 0.905 | 7 | 0.257 |
| random_gate_budget_0.25_seed061 | 0.940 | 0.880 | 0.900 | 5 | 0.269 |
| random_gate_budget_0.25_seed062 | 0.930 | 0.900 | 0.924 | 5 | 0.260 |
| random_gate_budget_0.25_seed063 | 0.920 | 0.870 | 0.894 | 7 | 0.266 |
| random_gate_budget_0.25_seed064 | 0.900 | 0.860 | 0.877 | 9 | 0.264 |
| random_gate_budget_0.25_seed065 | 0.890 | 0.840 | 0.862 | 11 | 0.269 |
| random_gate_budget_0.25_seed066 | 0.900 | 0.860 | 0.887 | 9 | 0.255 |
| random_gate_budget_0.25_seed067 | 0.900 | 0.880 | 0.897 | 8 | 0.259 |
| random_gate_budget_0.25_seed068 | 0.920 | 0.880 | 0.905 | 7 | 0.263 |
| random_gate_budget_0.25_seed069 | 0.900 | 0.880 | 0.904 | 9 | 0.268 |
| random_gate_budget_0.25_seed070 | 0.920 | 0.880 | 0.902 | 7 | 0.268 |
| random_gate_budget_0.25_seed071 | 0.920 | 0.850 | 0.877 | 8 | 0.271 |
| random_gate_budget_0.25_seed072 | 0.900 | 0.870 | 0.891 | 8 | 0.262 |
| random_gate_budget_0.25_seed073 | 0.900 | 0.890 | 0.914 | 8 | 0.259 |
| random_gate_budget_0.25_seed074 | 0.900 | 0.880 | 0.901 | 8 | 0.266 |
| random_gate_budget_0.25_seed075 | 0.920 | 0.890 | 0.920 | 6 | 0.265 |
| random_gate_budget_0.25_seed076 | 0.880 | 0.850 | 0.874 | 11 | 0.263 |
| random_gate_budget_0.25_seed077 | 0.960 | 0.880 | 0.902 | 4 | 0.264 |
| random_gate_budget_0.25_seed078 | 0.920 | 0.890 | 0.910 | 7 | 0.269 |
| random_gate_budget_0.25_seed079 | 0.890 | 0.870 | 0.894 | 9 | 0.260 |
| random_gate_budget_0.25_seed080 | 0.930 | 0.880 | 0.897 | 6 | 0.257 |
| random_gate_budget_0.25_seed081 | 0.920 | 0.860 | 0.885 | 7 | 0.252 |
| random_gate_budget_0.25_seed082 | 0.910 | 0.870 | 0.891 | 8 | 0.257 |
| random_gate_budget_0.25_seed083 | 0.920 | 0.880 | 0.902 | 7 | 0.255 |
| random_gate_budget_0.25_seed084 | 0.940 | 0.880 | 0.899 | 5 | 0.266 |
| random_gate_budget_0.25_seed085 | 0.940 | 0.870 | 0.894 | 6 | 0.267 |
| random_gate_budget_0.25_seed086 | 0.920 | 0.880 | 0.902 | 7 | 0.262 |
| random_gate_budget_0.25_seed087 | 0.910 | 0.880 | 0.907 | 8 | 0.268 |
| random_gate_budget_0.25_seed088 | 0.920 | 0.890 | 0.913 | 6 | 0.280 |
| random_gate_budget_0.25_seed089 | 0.910 | 0.900 | 0.919 | 7 | 0.271 |
| random_gate_budget_0.25_seed090 | 0.940 | 0.890 | 0.909 | 4 | 0.256 |
| random_gate_budget_0.25_seed091 | 0.910 | 0.850 | 0.881 | 9 | 0.266 |
| random_gate_budget_0.25_seed092 | 0.910 | 0.880 | 0.905 | 8 | 0.264 |
| random_gate_budget_0.25_seed093 | 0.960 | 0.870 | 0.897 | 4 | 0.258 |
| random_gate_budget_0.25_seed094 | 0.920 | 0.870 | 0.902 | 7 | 0.272 |
| random_gate_budget_0.25_seed095 | 0.920 | 0.860 | 0.890 | 8 | 0.259 |
| random_gate_budget_0.25_seed096 | 0.940 | 0.880 | 0.902 | 6 | 0.266 |
| random_gate_budget_0.25_seed097 | 0.910 | 0.890 | 0.914 | 7 | 0.262 |
| random_gate_budget_0.25_seed098 | 0.920 | 0.880 | 0.899 | 8 | 0.260 |
| random_gate_budget_0.25_seed099 | 0.930 | 0.850 | 0.876 | 7 | 0.267 |
| random_gate_budget_0.40_seed000 | 0.970 | 0.890 | 0.909 | 3 | 0.414 |
| random_gate_budget_0.40_seed001 | 0.950 | 0.860 | 0.889 | 5 | 0.417 |
| random_gate_budget_0.40_seed002 | 0.910 | 0.880 | 0.902 | 7 | 0.423 |
| random_gate_budget_0.40_seed003 | 0.940 | 0.870 | 0.892 | 5 | 0.430 |
| random_gate_budget_0.40_seed004 | 0.950 | 0.890 | 0.910 | 4 | 0.418 |
| random_gate_budget_0.40_seed005 | 0.960 | 0.890 | 0.910 | 3 | 0.427 |
| random_gate_budget_0.40_seed006 | 0.940 | 0.880 | 0.905 | 5 | 0.414 |
| random_gate_budget_0.40_seed007 | 0.930 | 0.880 | 0.900 | 6 | 0.418 |
| random_gate_budget_0.40_seed008 | 0.940 | 0.850 | 0.874 | 6 | 0.422 |
| random_gate_budget_0.40_seed009 | 0.950 | 0.880 | 0.902 | 4 | 0.422 |
| random_gate_budget_0.40_seed010 | 0.940 | 0.890 | 0.905 | 5 | 0.420 |
| random_gate_budget_0.40_seed011 | 0.960 | 0.890 | 0.912 | 3 | 0.426 |
| random_gate_budget_0.40_seed012 | 0.910 | 0.860 | 0.881 | 8 | 0.421 |
| random_gate_budget_0.40_seed013 | 0.940 | 0.870 | 0.897 | 5 | 0.432 |
| random_gate_budget_0.40_seed014 | 0.970 | 0.900 | 0.920 | 2 | 0.428 |
| random_gate_budget_0.40_seed015 | 0.950 | 0.890 | 0.912 | 4 | 0.421 |
| random_gate_budget_0.40_seed016 | 0.910 | 0.890 | 0.910 | 7 | 0.419 |
| random_gate_budget_0.40_seed017 | 0.950 | 0.880 | 0.899 | 5 | 0.421 |
| random_gate_budget_0.40_seed018 | 0.950 | 0.880 | 0.900 | 4 | 0.431 |
| random_gate_budget_0.40_seed019 | 0.930 | 0.900 | 0.925 | 5 | 0.423 |
| random_gate_budget_0.40_seed020 | 0.950 | 0.890 | 0.914 | 4 | 0.429 |
| random_gate_budget_0.40_seed021 | 0.930 | 0.870 | 0.889 | 6 | 0.414 |
| random_gate_budget_0.40_seed022 | 0.930 | 0.870 | 0.899 | 6 | 0.419 |
| random_gate_budget_0.40_seed023 | 0.940 | 0.900 | 0.917 | 4 | 0.417 |
| random_gate_budget_0.40_seed024 | 0.960 | 0.880 | 0.901 | 4 | 0.427 |
| random_gate_budget_0.40_seed025 | 0.950 | 0.900 | 0.922 | 3 | 0.418 |
| random_gate_budget_0.40_seed026 | 0.940 | 0.880 | 0.910 | 5 | 0.421 |
| random_gate_budget_0.40_seed027 | 0.950 | 0.880 | 0.902 | 4 | 0.419 |
| random_gate_budget_0.40_seed028 | 0.950 | 0.890 | 0.909 | 4 | 0.426 |
| random_gate_budget_0.40_seed029 | 0.930 | 0.890 | 0.907 | 6 | 0.423 |
| random_gate_budget_0.40_seed030 | 0.960 | 0.890 | 0.912 | 3 | 0.420 |
| random_gate_budget_0.40_seed031 | 0.940 | 0.880 | 0.905 | 5 | 0.433 |
| random_gate_budget_0.40_seed032 | 0.950 | 0.880 | 0.900 | 4 | 0.412 |
| random_gate_budget_0.40_seed033 | 0.920 | 0.890 | 0.910 | 6 | 0.424 |
| random_gate_budget_0.40_seed034 | 0.940 | 0.890 | 0.912 | 5 | 0.424 |
| random_gate_budget_0.40_seed035 | 0.940 | 0.880 | 0.905 | 5 | 0.425 |
| random_gate_budget_0.40_seed036 | 0.930 | 0.870 | 0.902 | 7 | 0.417 |
| random_gate_budget_0.40_seed037 | 0.930 | 0.870 | 0.889 | 6 | 0.427 |
| random_gate_budget_0.40_seed038 | 0.920 | 0.880 | 0.897 | 7 | 0.429 |
| random_gate_budget_0.40_seed039 | 0.960 | 0.890 | 0.912 | 4 | 0.423 |
| random_gate_budget_0.40_seed040 | 0.930 | 0.880 | 0.901 | 6 | 0.429 |
| random_gate_budget_0.40_seed041 | 0.950 | 0.870 | 0.891 | 5 | 0.429 |
| random_gate_budget_0.40_seed042 | 0.950 | 0.880 | 0.902 | 4 | 0.425 |
| random_gate_budget_0.40_seed043 | 0.930 | 0.860 | 0.887 | 6 | 0.426 |
| random_gate_budget_0.40_seed044 | 0.950 | 0.890 | 0.914 | 4 | 0.424 |
| random_gate_budget_0.40_seed045 | 0.940 | 0.900 | 0.919 | 4 | 0.418 |
| random_gate_budget_0.40_seed046 | 0.950 | 0.880 | 0.902 | 4 | 0.420 |
| random_gate_budget_0.40_seed047 | 0.950 | 0.870 | 0.894 | 5 | 0.411 |
| random_gate_budget_0.40_seed048 | 0.950 | 0.880 | 0.907 | 4 | 0.423 |
| random_gate_budget_0.40_seed049 | 0.920 | 0.870 | 0.895 | 7 | 0.420 |
| random_gate_budget_0.40_seed050 | 0.940 | 0.890 | 0.912 | 5 | 0.434 |
| random_gate_budget_0.40_seed051 | 0.950 | 0.870 | 0.892 | 5 | 0.424 |
| random_gate_budget_0.40_seed052 | 0.930 | 0.870 | 0.896 | 7 | 0.427 |
| random_gate_budget_0.40_seed053 | 0.910 | 0.870 | 0.889 | 8 | 0.421 |
| random_gate_budget_0.40_seed054 | 0.950 | 0.890 | 0.909 | 4 | 0.415 |
| random_gate_budget_0.40_seed055 | 0.980 | 0.890 | 0.912 | 2 | 0.423 |
| random_gate_budget_0.40_seed056 | 0.930 | 0.870 | 0.889 | 6 | 0.424 |
| random_gate_budget_0.40_seed057 | 0.940 | 0.870 | 0.895 | 5 | 0.426 |
| random_gate_budget_0.40_seed058 | 0.960 | 0.900 | 0.917 | 3 | 0.428 |
| random_gate_budget_0.40_seed059 | 0.950 | 0.880 | 0.902 | 4 | 0.425 |
| random_gate_budget_0.40_seed060 | 0.940 | 0.880 | 0.907 | 5 | 0.421 |
| random_gate_budget_0.40_seed061 | 0.970 | 0.900 | 0.919 | 2 | 0.427 |
| random_gate_budget_0.40_seed062 | 0.960 | 0.910 | 0.930 | 2 | 0.420 |
| random_gate_budget_0.40_seed063 | 0.950 | 0.890 | 0.911 | 4 | 0.428 |
| random_gate_budget_0.40_seed064 | 0.940 | 0.890 | 0.906 | 5 | 0.429 |
| random_gate_budget_0.40_seed065 | 0.920 | 0.870 | 0.891 | 7 | 0.418 |
| random_gate_budget_0.40_seed066 | 0.910 | 0.880 | 0.909 | 7 | 0.411 |
| random_gate_budget_0.40_seed067 | 0.930 | 0.890 | 0.909 | 6 | 0.415 |
| random_gate_budget_0.40_seed068 | 0.930 | 0.880 | 0.902 | 6 | 0.427 |
| random_gate_budget_0.40_seed069 | 0.920 | 0.890 | 0.909 | 7 | 0.421 |
| random_gate_budget_0.40_seed070 | 0.940 | 0.880 | 0.904 | 5 | 0.425 |
| random_gate_budget_0.40_seed071 | 0.930 | 0.880 | 0.900 | 6 | 0.419 |
| random_gate_budget_0.40_seed072 | 0.910 | 0.870 | 0.894 | 7 | 0.427 |
| random_gate_budget_0.40_seed073 | 0.950 | 0.900 | 0.920 | 4 | 0.415 |
| random_gate_budget_0.40_seed074 | 0.920 | 0.890 | 0.911 | 6 | 0.419 |
| random_gate_budget_0.40_seed075 | 0.930 | 0.870 | 0.899 | 6 | 0.426 |
| random_gate_budget_0.40_seed076 | 0.920 | 0.860 | 0.881 | 8 | 0.424 |
| random_gate_budget_0.40_seed077 | 0.960 | 0.890 | 0.910 | 3 | 0.426 |
| random_gate_budget_0.40_seed078 | 0.950 | 0.890 | 0.914 | 4 | 0.433 |
| random_gate_budget_0.40_seed079 | 0.910 | 0.890 | 0.914 | 7 | 0.421 |
| random_gate_budget_0.40_seed080 | 0.940 | 0.870 | 0.889 | 6 | 0.420 |
| random_gate_budget_0.40_seed081 | 0.960 | 0.890 | 0.912 | 3 | 0.414 |
| random_gate_budget_0.40_seed082 | 0.940 | 0.890 | 0.915 | 4 | 0.413 |
| random_gate_budget_0.40_seed083 | 0.930 | 0.890 | 0.914 | 5 | 0.415 |
| random_gate_budget_0.40_seed084 | 0.940 | 0.880 | 0.900 | 5 | 0.422 |
| random_gate_budget_0.40_seed085 | 0.940 | 0.880 | 0.907 | 5 | 0.428 |
| random_gate_budget_0.40_seed086 | 0.930 | 0.880 | 0.904 | 6 | 0.425 |
| random_gate_budget_0.40_seed087 | 0.960 | 0.880 | 0.900 | 4 | 0.424 |
| random_gate_budget_0.40_seed088 | 0.930 | 0.880 | 0.905 | 6 | 0.425 |
| random_gate_budget_0.40_seed089 | 0.940 | 0.890 | 0.911 | 5 | 0.420 |
| random_gate_budget_0.40_seed090 | 0.950 | 0.900 | 0.920 | 3 | 0.427 |
| random_gate_budget_0.40_seed091 | 0.940 | 0.860 | 0.881 | 6 | 0.424 |
| random_gate_budget_0.40_seed092 | 0.950 | 0.890 | 0.909 | 4 | 0.424 |
| random_gate_budget_0.40_seed093 | 0.960 | 0.890 | 0.910 | 3 | 0.422 |
| random_gate_budget_0.40_seed094 | 0.920 | 0.880 | 0.907 | 6 | 0.423 |
| random_gate_budget_0.40_seed095 | 0.950 | 0.890 | 0.910 | 4 | 0.423 |
| random_gate_budget_0.40_seed096 | 0.950 | 0.890 | 0.914 | 4 | 0.427 |
| random_gate_budget_0.40_seed097 | 0.920 | 0.890 | 0.912 | 6 | 0.417 |
| random_gate_budget_0.40_seed098 | 0.960 | 0.890 | 0.907 | 4 | 0.425 |
| random_gate_budget_0.40_seed099 | 0.940 | 0.860 | 0.881 | 6 | 0.417 |
| risk_guided_doc_patch_k2 | 0.960 | 0.890 | 0.912 | 3 | 0.546 |
| safe_gate_budget_0.10 | 0.930 | 0.890 | 0.910 | 5 | 0.117 |
| safe_gate_budget_0.25 | 0.950 | 0.900 | 0.922 | 3 | 0.293 |
| safe_gate_budget_0.40 | 0.960 | 0.890 | 0.912 | 3 | 0.432 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::boundary_sensitive | 1.000 | 1.000 | 0 |
| full_prefill::conflict | 1.000 | 0.600 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.950 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::conflict | 0.500 | 0.350 | 10 |
| prefix_conditioned_naive_global::distractor_heavy | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::multi_hop | 0.900 | 0.950 | 1 |
| prefix_conditioned_naive_global::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed000::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed000::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed000::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed000::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed001::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed001::conflict | 0.600 | 0.350 | 8 |
| random_gate_budget_0.10_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed001::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed002::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed002::conflict | 0.450 | 0.400 | 10 |
| random_gate_budget_0.10_seed002::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed002::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::conflict | 0.500 | 0.300 | 10 |
| random_gate_budget_0.10_seed003::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed004::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed005::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed005::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed005::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed005::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.10_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed006::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::conflict | 0.500 | 0.400 | 9 |
| random_gate_budget_0.10_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::conflict | 0.500 | 0.300 | 10 |
| random_gate_budget_0.10_seed008::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed010::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed010::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed010::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed010::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed010::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed011::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed011::conflict | 0.650 | 0.500 | 6 |
| random_gate_budget_0.10_seed011::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed011::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed011::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed012::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed012::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed012::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed012::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed012::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed013::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed013::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed013::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed013::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed014::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed014::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed014::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed014::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed014::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed015::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed015::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed015::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed015::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed016::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed016::conflict | 0.450 | 0.300 | 11 |
| random_gate_budget_0.10_seed016::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed016::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed016::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed017::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed017::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.10_seed017::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed017::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed017::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed018::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed018::conflict | 0.650 | 0.450 | 7 |
| random_gate_budget_0.10_seed018::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed018::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed018::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed019::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed019::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed019::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed019::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed019::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed020::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed020::conflict | 0.650 | 0.450 | 7 |
| random_gate_budget_0.10_seed020::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed020::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed020::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed021::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed021::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed021::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed021::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed021::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed022::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed022::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed022::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed022::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed023::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed023::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed023::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed023::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed024::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed024::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed024::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed024::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed025::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed025::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed025::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed025::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed025::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed026::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed026::conflict | 0.600 | 0.450 | 8 |
| random_gate_budget_0.10_seed026::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed026::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed026::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed027::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed027::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed027::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed027::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed027::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed028::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed028::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed028::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed028::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed028::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed029::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed029::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed029::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed029::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed029::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed030::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed030::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed030::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed030::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed030::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed031::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed031::conflict | 0.500 | 0.400 | 9 |
| random_gate_budget_0.10_seed031::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed031::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed032::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed032::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed032::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed032::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed032::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed033::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed033::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed033::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed033::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed033::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed034::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed034::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed034::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed034::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed034::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed035::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed035::conflict | 0.450 | 0.400 | 10 |
| random_gate_budget_0.10_seed035::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed035::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed035::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed036::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed036::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed036::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed036::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed036::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed037::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed037::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed037::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed037::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed037::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed038::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed038::conflict | 0.500 | 0.300 | 10 |
| random_gate_budget_0.10_seed038::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed038::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed038::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed039::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed039::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed039::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed039::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed039::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed040::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed040::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed040::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed040::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed040::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed041::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed041::conflict | 0.450 | 0.300 | 11 |
| random_gate_budget_0.10_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed041::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed041::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed042::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed042::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed042::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed042::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed042::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed043::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed043::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed043::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed043::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed044::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed044::conflict | 0.650 | 0.350 | 7 |
| random_gate_budget_0.10_seed044::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed044::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed044::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed045::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed045::conflict | 0.550 | 0.500 | 8 |
| random_gate_budget_0.10_seed045::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed045::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed046::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed046::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed046::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed046::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed046::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed047::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed047::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed047::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed047::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed047::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed048::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed048::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed048::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed048::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed048::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed049::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed049::conflict | 0.600 | 0.350 | 8 |
| random_gate_budget_0.10_seed049::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed049::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed049::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed050::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed050::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed050::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed050::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed050::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed051::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed051::conflict | 0.450 | 0.300 | 11 |
| random_gate_budget_0.10_seed051::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed051::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed051::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed052::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed052::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed052::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed052::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed052::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed053::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed053::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed053::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed053::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed054::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed054::conflict | 0.600 | 0.450 | 8 |
| random_gate_budget_0.10_seed054::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed054::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.10_seed054::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed055::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed055::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.10_seed055::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed055::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed055::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed056::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed056::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed056::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed056::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed056::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed057::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed057::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed057::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed057::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed057::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed058::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed058::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed058::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed058::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed059::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed059::conflict | 0.550 | 0.300 | 9 |
| random_gate_budget_0.10_seed059::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed059::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed059::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed060::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed060::conflict | 0.600 | 0.450 | 8 |
| random_gate_budget_0.10_seed060::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed060::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed061::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed061::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.10_seed061::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed061::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed061::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed062::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed062::conflict | 0.500 | 0.450 | 9 |
| random_gate_budget_0.10_seed062::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed062::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed062::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed063::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed063::conflict | 0.650 | 0.350 | 7 |
| random_gate_budget_0.10_seed063::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed063::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed063::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed064::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed064::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed064::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed064::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed064::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed065::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed065::conflict | 0.450 | 0.300 | 11 |
| random_gate_budget_0.10_seed065::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed065::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed065::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed066::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed066::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed066::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed066::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed066::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed067::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed067::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed067::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed067::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed067::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed068::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed068::conflict | 0.450 | 0.400 | 10 |
| random_gate_budget_0.10_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed068::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed068::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed069::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed069::conflict | 0.600 | 0.450 | 8 |
| random_gate_budget_0.10_seed069::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed069::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed070::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed070::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed070::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed070::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed071::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed071::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed071::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed071::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed072::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed072::conflict | 0.550 | 0.400 | 8 |
| random_gate_budget_0.10_seed072::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed072::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed073::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed073::conflict | 0.500 | 0.450 | 9 |
| random_gate_budget_0.10_seed073::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed073::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed074::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed074::conflict | 0.450 | 0.400 | 10 |
| random_gate_budget_0.10_seed074::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed074::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed074::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed075::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed075::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.10_seed075::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed075::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed075::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed076::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed076::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed076::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed076::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed076::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed077::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed077::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed077::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed077::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed077::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed078::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed078::conflict | 0.450 | 0.400 | 10 |
| random_gate_budget_0.10_seed078::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed078::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed078::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed079::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed079::conflict | 0.550 | 0.300 | 9 |
| random_gate_budget_0.10_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed079::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed079::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed080::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed080::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed080::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed080::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed080::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed081::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed081::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed081::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed081::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed081::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed082::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed082::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed082::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed082::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed082::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed083::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed083::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed083::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed083::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed083::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed084::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed084::conflict | 0.750 | 0.450 | 5 |
| random_gate_budget_0.10_seed084::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed084::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed084::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed085::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed085::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.10_seed085::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed085::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed085::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed086::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed086::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.10_seed086::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed086::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed086::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed087::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed087::conflict | 0.600 | 0.450 | 8 |
| random_gate_budget_0.10_seed087::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed087::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed088::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed088::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.10_seed088::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed088::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.10_seed088::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed089::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed089::conflict | 0.650 | 0.500 | 7 |
| random_gate_budget_0.10_seed089::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed089::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed089::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed090::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed090::conflict | 0.600 | 0.350 | 8 |
| random_gate_budget_0.10_seed090::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed090::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed090::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed091::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed091::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.10_seed091::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed091::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed092::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed092::conflict | 0.450 | 0.300 | 11 |
| random_gate_budget_0.10_seed092::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed092::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.10_seed092::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed093::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed093::conflict | 0.650 | 0.350 | 7 |
| random_gate_budget_0.10_seed093::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed093::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed093::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed094::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed094::conflict | 0.600 | 0.350 | 8 |
| random_gate_budget_0.10_seed094::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed094::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed095::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed095::conflict | 0.500 | 0.300 | 10 |
| random_gate_budget_0.10_seed095::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed095::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed095::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed096::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed096::conflict | 0.650 | 0.450 | 7 |
| random_gate_budget_0.10_seed096::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed096::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed096::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed097::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed097::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed097::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed097::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed097::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed098::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed098::conflict | 0.500 | 0.350 | 10 |
| random_gate_budget_0.10_seed098::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed098::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.10_seed098::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed099::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed099::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.10_seed099::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed099::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.10_seed099::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed000::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed000::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.25_seed000::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed000::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed001::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed001::conflict | 0.750 | 0.400 | 5 |
| random_gate_budget_0.25_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed001::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed002::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed002::conflict | 0.550 | 0.350 | 8 |
| random_gate_budget_0.25_seed002::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed002::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed003::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed003::conflict | 0.700 | 0.400 | 6 |
| random_gate_budget_0.25_seed003::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed003::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.25_seed004::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.25_seed005::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed006::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed006::conflict | 0.400 | 0.350 | 11 |
| random_gate_budget_0.25_seed006::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed006::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::conflict | 0.550 | 0.450 | 8 |
| random_gate_budget_0.25_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::conflict | 0.600 | 0.350 | 8 |
| random_gate_budget_0.25_seed008::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::conflict | 0.750 | 0.400 | 5 |
| random_gate_budget_0.25_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed009::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed010::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed010::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed010::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed010::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed010::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed011::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed011::conflict | 0.800 | 0.550 | 3 |
| random_gate_budget_0.25_seed011::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed011::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed011::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed012::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed012::conflict | 0.550 | 0.400 | 8 |
| random_gate_budget_0.25_seed012::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed012::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed012::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed013::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed013::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed013::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed013::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed014::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed014::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.25_seed014::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed014::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed014::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed015::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed015::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.25_seed015::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed015::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed016::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed016::conflict | 0.500 | 0.450 | 9 |
| random_gate_budget_0.25_seed016::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed016::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed016::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed017::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed017::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed017::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed017::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed017::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed018::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed018::conflict | 0.750 | 0.450 | 5 |
| random_gate_budget_0.25_seed018::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed018::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed018::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed019::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed019::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.25_seed019::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed019::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed019::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed020::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed020::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.25_seed020::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed020::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed020::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed021::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed021::conflict | 0.500 | 0.400 | 9 |
| random_gate_budget_0.25_seed021::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed021::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed021::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed022::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed022::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.25_seed022::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed022::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed023::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed023::conflict | 0.500 | 0.400 | 9 |
| random_gate_budget_0.25_seed023::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed023::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed024::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed024::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.25_seed024::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed024::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed025::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed025::conflict | 0.750 | 0.450 | 5 |
| random_gate_budget_0.25_seed025::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed025::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed025::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed026::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed026::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.25_seed026::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed026::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed026::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed027::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed027::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.25_seed027::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed027::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed027::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed028::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed028::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed028::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed028::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed028::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed029::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed029::conflict | 0.600 | 0.500 | 7 |
| random_gate_budget_0.25_seed029::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed029::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed029::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed030::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed030::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed030::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed030::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed030::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed031::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed031::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed031::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed031::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed032::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed032::conflict | 0.550 | 0.350 | 8 |
| random_gate_budget_0.25_seed032::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed032::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed032::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed033::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed033::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed033::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed033::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed033::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed034::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed034::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed034::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed034::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed034::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed035::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed035::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.25_seed035::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed035::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed035::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed036::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed036::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.25_seed036::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed036::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed036::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed037::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed037::conflict | 0.500 | 0.400 | 9 |
| random_gate_budget_0.25_seed037::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed037::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed037::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed038::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed038::conflict | 0.550 | 0.300 | 9 |
| random_gate_budget_0.25_seed038::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed038::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed038::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed039::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed039::conflict | 0.700 | 0.400 | 6 |
| random_gate_budget_0.25_seed039::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed039::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed039::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed040::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed040::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed040::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed040::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed040::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed041::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed041::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.25_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed041::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed041::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed042::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed042::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.25_seed042::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed042::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed042::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed043::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed043::conflict | 0.650 | 0.300 | 7 |
| random_gate_budget_0.25_seed043::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed043::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed044::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed044::conflict | 0.800 | 0.450 | 4 |
| random_gate_budget_0.25_seed044::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed044::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed044::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed045::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed045::conflict | 0.600 | 0.500 | 7 |
| random_gate_budget_0.25_seed045::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed045::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed046::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed046::conflict | 0.700 | 0.400 | 6 |
| random_gate_budget_0.25_seed046::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed046::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed046::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed047::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed047::conflict | 0.600 | 0.350 | 8 |
| random_gate_budget_0.25_seed047::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed047::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed047::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed048::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed048::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.25_seed048::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed048::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed048::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed049::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed049::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.25_seed049::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed049::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed049::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed050::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed050::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed050::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed050::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed050::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed051::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed051::conflict | 0.550 | 0.350 | 9 |
| random_gate_budget_0.25_seed051::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed051::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed051::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed052::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed052::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.25_seed052::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed052::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed052::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed053::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed053::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.25_seed053::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed053::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed054::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed054::conflict | 0.600 | 0.500 | 7 |
| random_gate_budget_0.25_seed054::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed054::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed054::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed055::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed055::conflict | 0.750 | 0.450 | 5 |
| random_gate_budget_0.25_seed055::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed055::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed055::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed056::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed056::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed056::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed056::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed056::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed057::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed057::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.25_seed057::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed057::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed057::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed058::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed058::conflict | 0.650 | 0.500 | 6 |
| random_gate_budget_0.25_seed058::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed058::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed059::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed059::conflict | 0.700 | 0.300 | 6 |
| random_gate_budget_0.25_seed059::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed059::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed059::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed060::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed060::conflict | 0.700 | 0.500 | 6 |
| random_gate_budget_0.25_seed060::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed060::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed061::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed061::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.25_seed061::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed061::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed061::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed062::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed062::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.25_seed062::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed062::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed062::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed063::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed063::conflict | 0.700 | 0.400 | 6 |
| random_gate_budget_0.25_seed063::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed063::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed063::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed064::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed064::conflict | 0.550 | 0.400 | 8 |
| random_gate_budget_0.25_seed064::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed064::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed064::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed065::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed065::conflict | 0.500 | 0.300 | 10 |
| random_gate_budget_0.25_seed065::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed065::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed065::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed066::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed066::conflict | 0.550 | 0.300 | 9 |
| random_gate_budget_0.25_seed066::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed066::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed066::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed067::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed067::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed067::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed067::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed067::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed068::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed068::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed068::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed068::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed069::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed069::conflict | 0.550 | 0.400 | 9 |
| random_gate_budget_0.25_seed069::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed069::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed070::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed070::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed070::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed070::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed071::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed071::conflict | 0.600 | 0.300 | 8 |
| random_gate_budget_0.25_seed071::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed071::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed072::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed072::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.25_seed072::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed072::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed073::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed073::conflict | 0.550 | 0.450 | 8 |
| random_gate_budget_0.25_seed073::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed073::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed074::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed074::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed074::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed074::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed074::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed075::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed075::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.25_seed075::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed075::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed075::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed076::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed076::conflict | 0.500 | 0.300 | 10 |
| random_gate_budget_0.25_seed076::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed076::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed076::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed077::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed077::conflict | 0.800 | 0.450 | 4 |
| random_gate_budget_0.25_seed077::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed077::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed077::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed078::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed078::conflict | 0.600 | 0.500 | 7 |
| random_gate_budget_0.25_seed078::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed078::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed078::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed079::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed079::conflict | 0.550 | 0.400 | 8 |
| random_gate_budget_0.25_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed079::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed079::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed080::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed080::conflict | 0.750 | 0.450 | 5 |
| random_gate_budget_0.25_seed080::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed080::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed080::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed081::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed081::conflict | 0.700 | 0.350 | 6 |
| random_gate_budget_0.25_seed081::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed081::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed081::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed082::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed082::conflict | 0.600 | 0.350 | 8 |
| random_gate_budget_0.25_seed082::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed082::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed082::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed083::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed083::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed083::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed083::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed083::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed084::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed084::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.25_seed084::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed084::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed084::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed085::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed085::conflict | 0.750 | 0.450 | 5 |
| random_gate_budget_0.25_seed085::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed085::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed085::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed086::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed086::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed086::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed086::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed086::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed087::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed087::conflict | 0.600 | 0.400 | 8 |
| random_gate_budget_0.25_seed087::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed087::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed088::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed088::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.25_seed088::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed088::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.25_seed088::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed089::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed089::conflict | 0.600 | 0.500 | 7 |
| random_gate_budget_0.25_seed089::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed089::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed089::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed090::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed090::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.25_seed090::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed090::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed090::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed091::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed091::conflict | 0.550 | 0.300 | 9 |
| random_gate_budget_0.25_seed091::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed091::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed092::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed092::conflict | 0.550 | 0.450 | 8 |
| random_gate_budget_0.25_seed092::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed092::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed092::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed093::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed093::conflict | 0.800 | 0.400 | 4 |
| random_gate_budget_0.25_seed093::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed093::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed093::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed094::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed094::conflict | 0.650 | 0.350 | 7 |
| random_gate_budget_0.25_seed094::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed094::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed095::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed095::conflict | 0.600 | 0.350 | 8 |
| random_gate_budget_0.25_seed095::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed095::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed095::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed096::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed096::conflict | 0.700 | 0.450 | 6 |
| random_gate_budget_0.25_seed096::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed096::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed096::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed097::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed097::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.25_seed097::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed097::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.25_seed097::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed098::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed098::conflict | 0.600 | 0.450 | 8 |
| random_gate_budget_0.25_seed098::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed098::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.25_seed098::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed099::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed099::conflict | 0.700 | 0.350 | 6 |
| random_gate_budget_0.25_seed099::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed099::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.25_seed099::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed000::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed000::conflict | 0.850 | 0.500 | 3 |
| random_gate_budget_0.40_seed000::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed000::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::conflict | 0.800 | 0.400 | 4 |
| random_gate_budget_0.40_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.40_seed002::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed003::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed004::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed005::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed006::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed006::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed006::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed006::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.40_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed008::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed009::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed010::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed010::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.40_seed010::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed010::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed010::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed011::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed011::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed011::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed011::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed011::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed012::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed012::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.40_seed012::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed012::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed012::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed013::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed013::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed013::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed013::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed014::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed014::conflict | 0.850 | 0.550 | 2 |
| random_gate_budget_0.40_seed014::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed014::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed014::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed015::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed015::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed015::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed015::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed016::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed016::conflict | 0.650 | 0.500 | 6 |
| random_gate_budget_0.40_seed016::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed016::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.40_seed016::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed017::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed017::conflict | 0.750 | 0.450 | 5 |
| random_gate_budget_0.40_seed017::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed017::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed017::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed018::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed018::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed018::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed018::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed018::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed019::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed019::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.40_seed019::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed019::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed019::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed020::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed020::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed020::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed020::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed020::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed021::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed021::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed021::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed021::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed021::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed022::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed022::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed022::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed022::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed023::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed023::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed023::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed023::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed024::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed024::conflict | 0.800 | 0.450 | 4 |
| random_gate_budget_0.40_seed024::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed024::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed025::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed025::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed025::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed025::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed025::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed026::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed026::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed026::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed026::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed026::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed027::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed027::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed027::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed027::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed027::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed028::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed028::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed028::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed028::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed028::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed029::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed029::conflict | 0.650 | 0.500 | 6 |
| random_gate_budget_0.40_seed029::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed029::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed029::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed030::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed030::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed030::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed030::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed030::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed031::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed031::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed031::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed031::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed032::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed032::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed032::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed032::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed032::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed033::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed033::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.40_seed033::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed033::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.40_seed033::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed034::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed034::conflict | 0.800 | 0.500 | 4 |
| random_gate_budget_0.40_seed034::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed034::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.40_seed034::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed035::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed035::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed035::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed035::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed035::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed036::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed036::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.40_seed036::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed036::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed036::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed037::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed037::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.40_seed037::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed037::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed037::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed038::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed038::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.40_seed038::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed038::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed038::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed039::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed039::conflict | 0.800 | 0.500 | 4 |
| random_gate_budget_0.40_seed039::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed039::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed039::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed040::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed040::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.40_seed040::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed040::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed040::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed041::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed041::conflict | 0.800 | 0.450 | 4 |
| random_gate_budget_0.40_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed041::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed041::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed042::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed042::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed042::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed042::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed042::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed043::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed043::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.40_seed043::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed043::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed044::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed044::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed044::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed044::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed044::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed045::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed045::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed045::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed045::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed046::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed046::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed046::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed046::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed046::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed047::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed047::conflict | 0.750 | 0.400 | 5 |
| random_gate_budget_0.40_seed047::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed047::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed047::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed048::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed048::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed048::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed048::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed048::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed049::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed049::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.40_seed049::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed049::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed049::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed050::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed050::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.40_seed050::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed050::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed050::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed051::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed051::conflict | 0.800 | 0.450 | 4 |
| random_gate_budget_0.40_seed051::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed051::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed051::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed052::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed052::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.40_seed052::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed052::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed052::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed053::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed053::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.40_seed053::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed053::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed054::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed054::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed054::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed054::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed054::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed055::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed055::conflict | 0.900 | 0.500 | 2 |
| random_gate_budget_0.40_seed055::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed055::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed055::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed056::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed056::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed056::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed056::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed056::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed057::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed057::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed057::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed057::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed057::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed058::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed058::conflict | 0.800 | 0.550 | 3 |
| random_gate_budget_0.40_seed058::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed058::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed059::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed059::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed059::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed059::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed059::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed060::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed060::conflict | 0.800 | 0.450 | 4 |
| random_gate_budget_0.40_seed060::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed060::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.40_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed061::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed061::conflict | 0.850 | 0.550 | 2 |
| random_gate_budget_0.40_seed061::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed061::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed061::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed062::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed062::conflict | 0.850 | 0.550 | 2 |
| random_gate_budget_0.40_seed062::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed062::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed062::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed063::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed063::conflict | 0.800 | 0.450 | 4 |
| random_gate_budget_0.40_seed063::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed063::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed063::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed064::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed064::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.40_seed064::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed064::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed064::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed065::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed065::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.40_seed065::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed065::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed065::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed066::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed066::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.40_seed066::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed066::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed066::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed067::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed067::conflict | 0.650 | 0.500 | 6 |
| random_gate_budget_0.40_seed067::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed067::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed067::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed068::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed068::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.40_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed068::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed068::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed069::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed069::conflict | 0.600 | 0.500 | 7 |
| random_gate_budget_0.40_seed069::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed069::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed070::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed070::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed070::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed070::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed071::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed071::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.40_seed071::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed071::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed072::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed072::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.40_seed072::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed072::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.40_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed073::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed073::conflict | 0.750 | 0.550 | 4 |
| random_gate_budget_0.40_seed073::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed073::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed074::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed074::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.40_seed074::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed074::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed074::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed075::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed075::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.40_seed075::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed075::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed075::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed076::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed076::conflict | 0.650 | 0.400 | 7 |
| random_gate_budget_0.40_seed076::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed076::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed076::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed077::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed077::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed077::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed077::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed077::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed078::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed078::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed078::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed078::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed078::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed079::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed079::conflict | 0.600 | 0.450 | 7 |
| random_gate_budget_0.40_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed079::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed079::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed080::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed080::conflict | 0.700 | 0.400 | 6 |
| random_gate_budget_0.40_seed080::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed080::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed080::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed081::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed081::conflict | 0.850 | 0.450 | 3 |
| random_gate_budget_0.40_seed081::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed081::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed081::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed082::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed082::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed082::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed082::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed082::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed083::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed083::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed083::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed083::multi_hop | 0.900 | 0.950 | 1 |
| random_gate_budget_0.40_seed083::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed084::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed084::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed084::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed084::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed084::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed085::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed085::conflict | 0.700 | 0.450 | 5 |
| random_gate_budget_0.40_seed085::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed085::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed085::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed086::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed086::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.40_seed086::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed086::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed086::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed087::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed087::conflict | 0.800 | 0.450 | 4 |
| random_gate_budget_0.40_seed087::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed087::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed088::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed088::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.40_seed088::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed088::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed088::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed089::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed089::conflict | 0.700 | 0.500 | 5 |
| random_gate_budget_0.40_seed089::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed089::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed089::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed090::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed090::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed090::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed090::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed090::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed091::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed091::conflict | 0.700 | 0.350 | 6 |
| random_gate_budget_0.40_seed091::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed091::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed092::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed092::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed092::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed092::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed092::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed093::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed093::conflict | 0.800 | 0.500 | 3 |
| random_gate_budget_0.40_seed093::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed093::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed093::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed094::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed094::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.40_seed094::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed094::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed095::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed095::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed095::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed095::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed095::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed096::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed096::conflict | 0.750 | 0.500 | 4 |
| random_gate_budget_0.40_seed096::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed096::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed096::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed097::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed097::conflict | 0.650 | 0.450 | 6 |
| random_gate_budget_0.40_seed097::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed097::multi_hop | 0.950 | 1.000 | 0 |
| random_gate_budget_0.40_seed097::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed098::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed098::conflict | 0.800 | 0.500 | 4 |
| random_gate_budget_0.40_seed098::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed098::multi_hop | 1.000 | 0.950 | 0 |
| random_gate_budget_0.40_seed098::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed099::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed099::conflict | 0.750 | 0.400 | 5 |
| random_gate_budget_0.40_seed099::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed099::multi_hop | 0.950 | 0.900 | 1 |
| random_gate_budget_0.40_seed099::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::boundary_sensitive | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::conflict | 0.800 | 0.500 | 3 |
| risk_guided_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::multi_hop | 1.000 | 0.950 | 0 |
| risk_guided_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.10::boundary_sensitive | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.10::conflict | 0.750 | 0.500 | 4 |
| safe_gate_budget_0.10::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.10::multi_hop | 0.900 | 0.950 | 1 |
| safe_gate_budget_0.10::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.25::boundary_sensitive | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.25::conflict | 0.800 | 0.500 | 3 |
| safe_gate_budget_0.25::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.25::multi_hop | 0.950 | 1.000 | 0 |
| safe_gate_budget_0.25::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.40::boundary_sensitive | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.40::conflict | 0.800 | 0.500 | 3 |
| safe_gate_budget_0.40::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.40::multi_hop | 1.000 | 0.950 | 0 |
| safe_gate_budget_0.40::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| conflict_0004 | conflict | 3.30391 | `According to the official schedule, the Aster Port observatory opens at 8 AM` | `11 AM` | `8 AM` |
| multihop_0009 | multi_hop | 2.73932 | `Mariton` | `Priya Holt` | `Mariton` |
| conflict_0013 | conflict | 2.26899 | `According to the official schedule, the Kelminster observatory opens at 9 AM` | `According to the official schedule, the Kelminster observatory opens at 11` | `9 AM` |
| conflict_0012 | conflict | 2.02657 | `According to the official schedule, the Lydora observatory opens at 8` | `10 AM` | `8 AM` |
| conflict_0001 | conflict | 1.63146 | `9 AM` | `According to the official schedule, the Brevic observatory opens at 1` | `9 AM` |
| conflict_0016 | conflict | 1.06975 | `According to the official schedule, the Norwick observatory opens at 8 AM` | `According to the official schedule, the Norwick observatory opens at 11` | `8 AM` |
| conflict_0006 | conflict | 0.302249 | `According to the official schedule, the Norwick observatory opens at 10` | `1 PM` | `10 AM` |
| conflict_0018 | conflict | 0.219297 | `10 AM` | `1 PM` | `10 AM` |
| conflict_0015 | conflict | 0.123849 | `11 AM` | `10 AM` | `11 AM` |
| multihop_0019 | multi_hop | 0.0614844 | `Vera Noll` | `Mariton` | `Mariton` |

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
