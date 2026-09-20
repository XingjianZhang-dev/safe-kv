# Budget Gate Failure Analysis

## Pareto Summary

| target | actual | safe equiv | random mean | percentile | changed+wrong |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.099 | 0.740 | 0.771 | 0.050 | 20 |
| 0.25 | 0.251 | 0.830 | 0.825 | 0.660 | 14 |
| 0.40 | 0.401 | 0.910 | 0.878 | 1.000 | 6 |

# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.830 | 0.859 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.740 | 0.760 | 0.797 | 20 | 0.000 |
| random_gate_budget_0.10_seed000 | 0.780 | 0.770 | 0.803 | 17 | 0.105 |
| random_gate_budget_0.10_seed001 | 0.760 | 0.760 | 0.791 | 18 | 0.103 |
| random_gate_budget_0.10_seed002 | 0.760 | 0.770 | 0.803 | 18 | 0.118 |
| random_gate_budget_0.10_seed003 | 0.790 | 0.750 | 0.783 | 17 | 0.118 |
| random_gate_budget_0.10_seed004 | 0.760 | 0.760 | 0.800 | 19 | 0.105 |
| random_gate_budget_0.10_seed005 | 0.780 | 0.740 | 0.777 | 18 | 0.101 |
| random_gate_budget_0.10_seed006 | 0.770 | 0.760 | 0.796 | 18 | 0.109 |
| random_gate_budget_0.10_seed007 | 0.770 | 0.750 | 0.782 | 18 | 0.107 |
| random_gate_budget_0.10_seed008 | 0.790 | 0.780 | 0.822 | 16 | 0.116 |
| random_gate_budget_0.10_seed009 | 0.750 | 0.750 | 0.783 | 19 | 0.110 |
| random_gate_budget_0.10_seed010 | 0.760 | 0.770 | 0.806 | 18 | 0.105 |
| random_gate_budget_0.10_seed011 | 0.810 | 0.780 | 0.811 | 14 | 0.110 |
| random_gate_budget_0.10_seed012 | 0.740 | 0.760 | 0.797 | 20 | 0.102 |
| random_gate_budget_0.10_seed013 | 0.770 | 0.770 | 0.807 | 18 | 0.113 |
| random_gate_budget_0.10_seed014 | 0.760 | 0.770 | 0.806 | 18 | 0.115 |
| random_gate_budget_0.10_seed015 | 0.760 | 0.780 | 0.815 | 18 | 0.107 |
| random_gate_budget_0.10_seed016 | 0.750 | 0.750 | 0.789 | 20 | 0.104 |
| random_gate_budget_0.10_seed017 | 0.790 | 0.760 | 0.792 | 16 | 0.105 |
| random_gate_budget_0.10_seed018 | 0.770 | 0.780 | 0.810 | 17 | 0.105 |
| random_gate_budget_0.10_seed019 | 0.770 | 0.750 | 0.788 | 19 | 0.120 |
| random_gate_budget_0.10_seed020 | 0.770 | 0.760 | 0.793 | 18 | 0.113 |
| random_gate_budget_0.10_seed021 | 0.760 | 0.770 | 0.804 | 18 | 0.096 |
| random_gate_budget_0.10_seed022 | 0.770 | 0.790 | 0.827 | 17 | 0.100 |
| random_gate_budget_0.10_seed023 | 0.790 | 0.760 | 0.796 | 17 | 0.106 |
| random_gate_budget_0.10_seed024 | 0.800 | 0.770 | 0.802 | 16 | 0.101 |
| random_gate_budget_0.10_seed025 | 0.760 | 0.760 | 0.800 | 19 | 0.109 |
| random_gate_budget_0.10_seed026 | 0.790 | 0.740 | 0.782 | 18 | 0.102 |
| random_gate_budget_0.10_seed027 | 0.740 | 0.760 | 0.792 | 20 | 0.102 |
| random_gate_budget_0.10_seed028 | 0.790 | 0.780 | 0.809 | 16 | 0.111 |
| random_gate_budget_0.10_seed029 | 0.750 | 0.750 | 0.787 | 20 | 0.100 |
| random_gate_budget_0.10_seed030 | 0.800 | 0.780 | 0.820 | 16 | 0.100 |
| random_gate_budget_0.10_seed031 | 0.780 | 0.760 | 0.794 | 17 | 0.105 |
| random_gate_budget_0.10_seed032 | 0.760 | 0.780 | 0.817 | 18 | 0.104 |
| random_gate_budget_0.10_seed033 | 0.770 | 0.740 | 0.781 | 19 | 0.107 |
| random_gate_budget_0.10_seed034 | 0.750 | 0.770 | 0.806 | 19 | 0.103 |
| random_gate_budget_0.10_seed035 | 0.770 | 0.740 | 0.777 | 19 | 0.106 |
| random_gate_budget_0.10_seed036 | 0.770 | 0.750 | 0.789 | 19 | 0.115 |
| random_gate_budget_0.10_seed037 | 0.770 | 0.770 | 0.805 | 18 | 0.107 |
| random_gate_budget_0.10_seed038 | 0.770 | 0.740 | 0.786 | 19 | 0.110 |
| random_gate_budget_0.10_seed039 | 0.770 | 0.760 | 0.796 | 18 | 0.104 |
| random_gate_budget_0.10_seed040 | 0.770 | 0.790 | 0.827 | 17 | 0.093 |
| random_gate_budget_0.10_seed041 | 0.770 | 0.750 | 0.789 | 19 | 0.113 |
| random_gate_budget_0.10_seed042 | 0.770 | 0.740 | 0.777 | 19 | 0.115 |
| random_gate_budget_0.10_seed043 | 0.770 | 0.790 | 0.827 | 17 | 0.112 |
| random_gate_budget_0.10_seed044 | 0.770 | 0.770 | 0.809 | 17 | 0.114 |
| random_gate_budget_0.10_seed045 | 0.790 | 0.770 | 0.798 | 16 | 0.101 |
| random_gate_budget_0.10_seed046 | 0.760 | 0.750 | 0.783 | 19 | 0.114 |
| random_gate_budget_0.10_seed047 | 0.750 | 0.770 | 0.807 | 19 | 0.109 |
| random_gate_budget_0.10_seed048 | 0.800 | 0.760 | 0.795 | 16 | 0.111 |
| random_gate_budget_0.10_seed049 | 0.760 | 0.760 | 0.795 | 18 | 0.105 |
| random_gate_budget_0.10_seed050 | 0.780 | 0.750 | 0.786 | 18 | 0.110 |
| random_gate_budget_0.10_seed051 | 0.750 | 0.730 | 0.769 | 21 | 0.104 |
| random_gate_budget_0.10_seed052 | 0.760 | 0.780 | 0.816 | 18 | 0.115 |
| random_gate_budget_0.10_seed053 | 0.760 | 0.780 | 0.817 | 18 | 0.113 |
| random_gate_budget_0.10_seed054 | 0.760 | 0.750 | 0.783 | 19 | 0.110 |
| random_gate_budget_0.10_seed055 | 0.780 | 0.770 | 0.800 | 17 | 0.115 |
| random_gate_budget_0.10_seed056 | 0.780 | 0.780 | 0.811 | 17 | 0.104 |
| random_gate_budget_0.10_seed057 | 0.760 | 0.750 | 0.786 | 19 | 0.109 |
| random_gate_budget_0.10_seed058 | 0.770 | 0.780 | 0.820 | 17 | 0.104 |
| random_gate_budget_0.10_seed059 | 0.780 | 0.750 | 0.788 | 17 | 0.099 |
| random_gate_budget_0.10_seed060 | 0.790 | 0.790 | 0.824 | 16 | 0.116 |
| random_gate_budget_0.10_seed061 | 0.790 | 0.780 | 0.807 | 15 | 0.109 |
| random_gate_budget_0.10_seed062 | 0.750 | 0.760 | 0.794 | 19 | 0.114 |
| random_gate_budget_0.10_seed063 | 0.810 | 0.740 | 0.777 | 16 | 0.105 |
| random_gate_budget_0.10_seed064 | 0.740 | 0.760 | 0.792 | 20 | 0.114 |
| random_gate_budget_0.10_seed065 | 0.780 | 0.760 | 0.798 | 18 | 0.112 |
| random_gate_budget_0.10_seed066 | 0.750 | 0.720 | 0.757 | 21 | 0.096 |
| random_gate_budget_0.10_seed067 | 0.760 | 0.760 | 0.799 | 19 | 0.096 |
| random_gate_budget_0.10_seed068 | 0.770 | 0.760 | 0.796 | 18 | 0.104 |
| random_gate_budget_0.10_seed069 | 0.780 | 0.770 | 0.808 | 17 | 0.112 |
| random_gate_budget_0.10_seed070 | 0.770 | 0.770 | 0.807 | 18 | 0.104 |
| random_gate_budget_0.10_seed071 | 0.770 | 0.770 | 0.810 | 17 | 0.109 |
| random_gate_budget_0.10_seed072 | 0.780 | 0.780 | 0.817 | 16 | 0.103 |
| random_gate_budget_0.10_seed073 | 0.770 | 0.780 | 0.814 | 17 | 0.105 |
| random_gate_budget_0.10_seed074 | 0.770 | 0.780 | 0.814 | 17 | 0.095 |
| random_gate_budget_0.10_seed075 | 0.760 | 0.770 | 0.805 | 18 | 0.104 |
| random_gate_budget_0.10_seed076 | 0.740 | 0.760 | 0.797 | 20 | 0.107 |
| random_gate_budget_0.10_seed077 | 0.760 | 0.780 | 0.812 | 18 | 0.099 |
| random_gate_budget_0.10_seed078 | 0.760 | 0.770 | 0.804 | 18 | 0.111 |
| random_gate_budget_0.10_seed079 | 0.760 | 0.750 | 0.785 | 19 | 0.104 |
| random_gate_budget_0.10_seed080 | 0.770 | 0.760 | 0.794 | 18 | 0.106 |
| random_gate_budget_0.10_seed081 | 0.770 | 0.760 | 0.800 | 18 | 0.103 |
| random_gate_budget_0.10_seed082 | 0.770 | 0.780 | 0.814 | 17 | 0.109 |
| random_gate_budget_0.10_seed083 | 0.740 | 0.760 | 0.797 | 20 | 0.108 |
| random_gate_budget_0.10_seed084 | 0.790 | 0.780 | 0.805 | 15 | 0.111 |
| random_gate_budget_0.10_seed085 | 0.760 | 0.750 | 0.786 | 19 | 0.110 |
| random_gate_budget_0.10_seed086 | 0.780 | 0.760 | 0.795 | 18 | 0.109 |
| random_gate_budget_0.10_seed087 | 0.800 | 0.790 | 0.828 | 15 | 0.113 |
| random_gate_budget_0.10_seed088 | 0.760 | 0.770 | 0.803 | 18 | 0.113 |
| random_gate_budget_0.10_seed089 | 0.800 | 0.790 | 0.823 | 15 | 0.113 |
| random_gate_budget_0.10_seed090 | 0.770 | 0.750 | 0.783 | 18 | 0.101 |
| random_gate_budget_0.10_seed091 | 0.780 | 0.780 | 0.814 | 16 | 0.104 |
| random_gate_budget_0.10_seed092 | 0.790 | 0.760 | 0.802 | 17 | 0.115 |
| random_gate_budget_0.10_seed093 | 0.790 | 0.770 | 0.799 | 15 | 0.105 |
| random_gate_budget_0.10_seed094 | 0.800 | 0.770 | 0.811 | 15 | 0.116 |
| random_gate_budget_0.10_seed095 | 0.800 | 0.780 | 0.814 | 15 | 0.108 |
| random_gate_budget_0.10_seed096 | 0.770 | 0.770 | 0.804 | 18 | 0.113 |
| random_gate_budget_0.10_seed097 | 0.780 | 0.760 | 0.794 | 17 | 0.109 |
| random_gate_budget_0.10_seed098 | 0.770 | 0.760 | 0.799 | 18 | 0.109 |
| random_gate_budget_0.10_seed099 | 0.770 | 0.760 | 0.796 | 18 | 0.105 |
| random_gate_budget_0.25_seed000 | 0.800 | 0.770 | 0.801 | 15 | 0.262 |
| random_gate_budget_0.25_seed001 | 0.800 | 0.750 | 0.782 | 16 | 0.268 |
| random_gate_budget_0.25_seed002 | 0.810 | 0.750 | 0.776 | 15 | 0.275 |
| random_gate_budget_0.25_seed003 | 0.820 | 0.750 | 0.778 | 15 | 0.274 |
| random_gate_budget_0.25_seed004 | 0.820 | 0.770 | 0.812 | 14 | 0.266 |
| random_gate_budget_0.25_seed005 | 0.810 | 0.750 | 0.787 | 16 | 0.271 |
| random_gate_budget_0.25_seed006 | 0.800 | 0.760 | 0.793 | 16 | 0.263 |
| random_gate_budget_0.25_seed007 | 0.820 | 0.770 | 0.802 | 14 | 0.268 |
| random_gate_budget_0.25_seed008 | 0.840 | 0.810 | 0.848 | 12 | 0.277 |
| random_gate_budget_0.25_seed009 | 0.800 | 0.780 | 0.807 | 14 | 0.270 |
| random_gate_budget_0.25_seed010 | 0.800 | 0.770 | 0.800 | 15 | 0.260 |
| random_gate_budget_0.25_seed011 | 0.820 | 0.780 | 0.804 | 13 | 0.270 |
| random_gate_budget_0.25_seed012 | 0.830 | 0.770 | 0.799 | 14 | 0.263 |
| random_gate_budget_0.25_seed013 | 0.800 | 0.750 | 0.787 | 16 | 0.283 |
| random_gate_budget_0.25_seed014 | 0.840 | 0.800 | 0.825 | 10 | 0.275 |
| random_gate_budget_0.25_seed015 | 0.820 | 0.800 | 0.833 | 13 | 0.270 |
| random_gate_budget_0.25_seed016 | 0.800 | 0.790 | 0.821 | 15 | 0.273 |
| random_gate_budget_0.25_seed017 | 0.860 | 0.770 | 0.809 | 12 | 0.270 |
| random_gate_budget_0.25_seed018 | 0.810 | 0.790 | 0.821 | 13 | 0.265 |
| random_gate_budget_0.25_seed019 | 0.850 | 0.790 | 0.828 | 12 | 0.270 |
| random_gate_budget_0.25_seed020 | 0.860 | 0.800 | 0.831 | 10 | 0.275 |
| random_gate_budget_0.25_seed021 | 0.810 | 0.750 | 0.786 | 16 | 0.259 |
| random_gate_budget_0.25_seed022 | 0.810 | 0.790 | 0.829 | 15 | 0.270 |
| random_gate_budget_0.25_seed023 | 0.830 | 0.780 | 0.812 | 13 | 0.266 |
| random_gate_budget_0.25_seed024 | 0.860 | 0.770 | 0.805 | 12 | 0.267 |
| random_gate_budget_0.25_seed025 | 0.860 | 0.800 | 0.830 | 10 | 0.266 |
| random_gate_budget_0.25_seed026 | 0.820 | 0.740 | 0.781 | 16 | 0.281 |
| random_gate_budget_0.25_seed027 | 0.800 | 0.790 | 0.822 | 15 | 0.260 |
| random_gate_budget_0.25_seed028 | 0.850 | 0.790 | 0.824 | 12 | 0.275 |
| random_gate_budget_0.25_seed029 | 0.810 | 0.770 | 0.805 | 15 | 0.264 |
| random_gate_budget_0.25_seed030 | 0.840 | 0.780 | 0.812 | 13 | 0.266 |
| random_gate_budget_0.25_seed031 | 0.840 | 0.790 | 0.819 | 12 | 0.270 |
| random_gate_budget_0.25_seed032 | 0.820 | 0.780 | 0.809 | 13 | 0.264 |
| random_gate_budget_0.25_seed033 | 0.830 | 0.770 | 0.805 | 14 | 0.264 |
| random_gate_budget_0.25_seed034 | 0.820 | 0.780 | 0.818 | 14 | 0.271 |
| random_gate_budget_0.25_seed035 | 0.880 | 0.760 | 0.795 | 10 | 0.265 |
| random_gate_budget_0.25_seed036 | 0.820 | 0.780 | 0.817 | 14 | 0.261 |
| random_gate_budget_0.25_seed037 | 0.820 | 0.770 | 0.802 | 14 | 0.274 |
| random_gate_budget_0.25_seed038 | 0.820 | 0.760 | 0.800 | 15 | 0.265 |
| random_gate_budget_0.25_seed039 | 0.840 | 0.780 | 0.818 | 12 | 0.265 |
| random_gate_budget_0.25_seed040 | 0.870 | 0.830 | 0.860 | 9 | 0.258 |
| random_gate_budget_0.25_seed041 | 0.840 | 0.780 | 0.815 | 13 | 0.267 |
| random_gate_budget_0.25_seed042 | 0.810 | 0.750 | 0.778 | 15 | 0.277 |
| random_gate_budget_0.25_seed043 | 0.870 | 0.790 | 0.827 | 10 | 0.273 |
| random_gate_budget_0.25_seed044 | 0.840 | 0.780 | 0.813 | 12 | 0.283 |
| random_gate_budget_0.25_seed045 | 0.860 | 0.800 | 0.833 | 11 | 0.262 |
| random_gate_budget_0.25_seed046 | 0.820 | 0.790 | 0.820 | 13 | 0.269 |
| random_gate_budget_0.25_seed047 | 0.800 | 0.780 | 0.812 | 15 | 0.274 |
| random_gate_budget_0.25_seed048 | 0.870 | 0.790 | 0.823 | 10 | 0.271 |
| random_gate_budget_0.25_seed049 | 0.810 | 0.770 | 0.800 | 14 | 0.269 |
| random_gate_budget_0.25_seed050 | 0.840 | 0.770 | 0.800 | 13 | 0.272 |
| random_gate_budget_0.25_seed051 | 0.790 | 0.760 | 0.792 | 17 | 0.261 |
| random_gate_budget_0.25_seed052 | 0.790 | 0.770 | 0.803 | 17 | 0.275 |
| random_gate_budget_0.25_seed053 | 0.830 | 0.800 | 0.833 | 13 | 0.274 |
| random_gate_budget_0.25_seed054 | 0.840 | 0.770 | 0.798 | 13 | 0.255 |
| random_gate_budget_0.25_seed055 | 0.820 | 0.780 | 0.816 | 14 | 0.281 |
| random_gate_budget_0.25_seed056 | 0.810 | 0.780 | 0.811 | 15 | 0.273 |
| random_gate_budget_0.25_seed057 | 0.820 | 0.750 | 0.782 | 14 | 0.266 |
| random_gate_budget_0.25_seed058 | 0.830 | 0.790 | 0.821 | 12 | 0.267 |
| random_gate_budget_0.25_seed059 | 0.840 | 0.770 | 0.807 | 12 | 0.268 |
| random_gate_budget_0.25_seed060 | 0.820 | 0.810 | 0.842 | 13 | 0.256 |
| random_gate_budget_0.25_seed061 | 0.830 | 0.770 | 0.801 | 13 | 0.272 |
| random_gate_budget_0.25_seed062 | 0.810 | 0.760 | 0.794 | 14 | 0.265 |
| random_gate_budget_0.25_seed063 | 0.840 | 0.770 | 0.804 | 13 | 0.270 |
| random_gate_budget_0.25_seed064 | 0.820 | 0.770 | 0.797 | 14 | 0.271 |
| random_gate_budget_0.25_seed065 | 0.810 | 0.780 | 0.813 | 15 | 0.273 |
| random_gate_budget_0.25_seed066 | 0.830 | 0.780 | 0.812 | 13 | 0.262 |
| random_gate_budget_0.25_seed067 | 0.850 | 0.770 | 0.804 | 13 | 0.264 |
| random_gate_budget_0.25_seed068 | 0.850 | 0.770 | 0.806 | 12 | 0.263 |
| random_gate_budget_0.25_seed069 | 0.830 | 0.780 | 0.823 | 14 | 0.275 |
| random_gate_budget_0.25_seed070 | 0.850 | 0.800 | 0.828 | 11 | 0.273 |
| random_gate_budget_0.25_seed071 | 0.860 | 0.800 | 0.834 | 10 | 0.280 |
| random_gate_budget_0.25_seed072 | 0.840 | 0.790 | 0.818 | 12 | 0.269 |
| random_gate_budget_0.25_seed073 | 0.790 | 0.770 | 0.803 | 16 | 0.268 |
| random_gate_budget_0.25_seed074 | 0.810 | 0.810 | 0.838 | 13 | 0.263 |
| random_gate_budget_0.25_seed075 | 0.800 | 0.780 | 0.814 | 14 | 0.269 |
| random_gate_budget_0.25_seed076 | 0.800 | 0.770 | 0.810 | 16 | 0.273 |
| random_gate_budget_0.25_seed077 | 0.810 | 0.770 | 0.802 | 14 | 0.265 |
| random_gate_budget_0.25_seed078 | 0.840 | 0.790 | 0.823 | 12 | 0.277 |
| random_gate_budget_0.25_seed079 | 0.840 | 0.780 | 0.809 | 13 | 0.263 |
| random_gate_budget_0.25_seed080 | 0.800 | 0.770 | 0.799 | 15 | 0.259 |
| random_gate_budget_0.25_seed081 | 0.800 | 0.760 | 0.793 | 15 | 0.253 |
| random_gate_budget_0.25_seed082 | 0.800 | 0.760 | 0.797 | 16 | 0.261 |
| random_gate_budget_0.25_seed083 | 0.780 | 0.790 | 0.820 | 16 | 0.257 |
| random_gate_budget_0.25_seed084 | 0.840 | 0.790 | 0.813 | 11 | 0.272 |
| random_gate_budget_0.25_seed085 | 0.800 | 0.780 | 0.817 | 15 | 0.276 |
| random_gate_budget_0.25_seed086 | 0.850 | 0.790 | 0.823 | 11 | 0.270 |
| random_gate_budget_0.25_seed087 | 0.830 | 0.790 | 0.831 | 13 | 0.274 |
| random_gate_budget_0.25_seed088 | 0.830 | 0.760 | 0.793 | 14 | 0.287 |
| random_gate_budget_0.25_seed089 | 0.820 | 0.740 | 0.775 | 16 | 0.274 |
| random_gate_budget_0.25_seed090 | 0.850 | 0.790 | 0.813 | 10 | 0.258 |
| random_gate_budget_0.25_seed091 | 0.790 | 0.770 | 0.806 | 16 | 0.270 |
| random_gate_budget_0.25_seed092 | 0.830 | 0.760 | 0.804 | 14 | 0.272 |
| random_gate_budget_0.25_seed093 | 0.850 | 0.800 | 0.832 | 10 | 0.270 |
| random_gate_budget_0.25_seed094 | 0.800 | 0.770 | 0.811 | 15 | 0.273 |
| random_gate_budget_0.25_seed095 | 0.820 | 0.750 | 0.789 | 15 | 0.262 |
| random_gate_budget_0.25_seed096 | 0.840 | 0.780 | 0.813 | 13 | 0.273 |
| random_gate_budget_0.25_seed097 | 0.830 | 0.760 | 0.791 | 14 | 0.267 |
| random_gate_budget_0.25_seed098 | 0.820 | 0.790 | 0.824 | 14 | 0.259 |
| random_gate_budget_0.25_seed099 | 0.820 | 0.750 | 0.792 | 15 | 0.273 |
| random_gate_budget_0.40_seed000 | 0.880 | 0.800 | 0.834 | 9 | 0.420 |
| random_gate_budget_0.40_seed001 | 0.860 | 0.780 | 0.814 | 11 | 0.427 |
| random_gate_budget_0.40_seed002 | 0.870 | 0.760 | 0.791 | 11 | 0.428 |
| random_gate_budget_0.40_seed003 | 0.870 | 0.760 | 0.790 | 11 | 0.437 |
| random_gate_budget_0.40_seed004 | 0.890 | 0.770 | 0.801 | 9 | 0.426 |
| random_gate_budget_0.40_seed005 | 0.890 | 0.790 | 0.817 | 8 | 0.434 |
| random_gate_budget_0.40_seed006 | 0.870 | 0.760 | 0.792 | 11 | 0.422 |
| random_gate_budget_0.40_seed007 | 0.900 | 0.790 | 0.826 | 8 | 0.424 |
| random_gate_budget_0.40_seed008 | 0.880 | 0.800 | 0.831 | 9 | 0.428 |
| random_gate_budget_0.40_seed009 | 0.860 | 0.780 | 0.806 | 10 | 0.428 |
| random_gate_budget_0.40_seed010 | 0.890 | 0.780 | 0.811 | 9 | 0.425 |
| random_gate_budget_0.40_seed011 | 0.880 | 0.800 | 0.828 | 8 | 0.432 |
| random_gate_budget_0.40_seed012 | 0.860 | 0.790 | 0.816 | 11 | 0.432 |
| random_gate_budget_0.40_seed013 | 0.870 | 0.760 | 0.795 | 11 | 0.443 |
| random_gate_budget_0.40_seed014 | 0.870 | 0.810 | 0.836 | 8 | 0.435 |
| random_gate_budget_0.40_seed015 | 0.880 | 0.790 | 0.819 | 9 | 0.430 |
| random_gate_budget_0.40_seed016 | 0.850 | 0.780 | 0.813 | 12 | 0.422 |
| random_gate_budget_0.40_seed017 | 0.870 | 0.770 | 0.806 | 11 | 0.432 |
| random_gate_budget_0.40_seed018 | 0.890 | 0.810 | 0.834 | 7 | 0.430 |
| random_gate_budget_0.40_seed019 | 0.910 | 0.810 | 0.845 | 7 | 0.427 |
| random_gate_budget_0.40_seed020 | 0.900 | 0.810 | 0.839 | 7 | 0.433 |
| random_gate_budget_0.40_seed021 | 0.870 | 0.790 | 0.821 | 10 | 0.419 |
| random_gate_budget_0.40_seed022 | 0.860 | 0.800 | 0.833 | 10 | 0.423 |
| random_gate_budget_0.40_seed023 | 0.870 | 0.800 | 0.822 | 9 | 0.425 |
| random_gate_budget_0.40_seed024 | 0.900 | 0.800 | 0.829 | 8 | 0.436 |
| random_gate_budget_0.40_seed025 | 0.900 | 0.780 | 0.809 | 8 | 0.422 |
| random_gate_budget_0.40_seed026 | 0.890 | 0.780 | 0.817 | 9 | 0.428 |
| random_gate_budget_0.40_seed027 | 0.880 | 0.780 | 0.809 | 9 | 0.430 |
| random_gate_budget_0.40_seed028 | 0.890 | 0.780 | 0.811 | 9 | 0.432 |
| random_gate_budget_0.40_seed029 | 0.890 | 0.800 | 0.829 | 9 | 0.430 |
| random_gate_budget_0.40_seed030 | 0.900 | 0.800 | 0.829 | 7 | 0.426 |
| random_gate_budget_0.40_seed031 | 0.890 | 0.810 | 0.839 | 8 | 0.443 |
| random_gate_budget_0.40_seed032 | 0.890 | 0.770 | 0.802 | 9 | 0.420 |
| random_gate_budget_0.40_seed033 | 0.860 | 0.790 | 0.822 | 11 | 0.430 |
| random_gate_budget_0.40_seed034 | 0.850 | 0.800 | 0.833 | 11 | 0.430 |
| random_gate_budget_0.40_seed035 | 0.910 | 0.790 | 0.824 | 7 | 0.433 |
| random_gate_budget_0.40_seed036 | 0.870 | 0.780 | 0.822 | 11 | 0.424 |
| random_gate_budget_0.40_seed037 | 0.900 | 0.810 | 0.834 | 7 | 0.433 |
| random_gate_budget_0.40_seed038 | 0.870 | 0.770 | 0.803 | 11 | 0.437 |
| random_gate_budget_0.40_seed039 | 0.870 | 0.790 | 0.822 | 10 | 0.424 |
| random_gate_budget_0.40_seed040 | 0.890 | 0.810 | 0.836 | 8 | 0.433 |
| random_gate_budget_0.40_seed041 | 0.890 | 0.800 | 0.829 | 9 | 0.432 |
| random_gate_budget_0.40_seed042 | 0.860 | 0.750 | 0.780 | 12 | 0.435 |
| random_gate_budget_0.40_seed043 | 0.900 | 0.800 | 0.832 | 7 | 0.433 |
| random_gate_budget_0.40_seed044 | 0.870 | 0.760 | 0.794 | 11 | 0.434 |
| random_gate_budget_0.40_seed045 | 0.910 | 0.800 | 0.833 | 7 | 0.421 |
| random_gate_budget_0.40_seed046 | 0.900 | 0.790 | 0.820 | 8 | 0.426 |
| random_gate_budget_0.40_seed047 | 0.840 | 0.800 | 0.835 | 11 | 0.417 |
| random_gate_budget_0.40_seed048 | 0.890 | 0.770 | 0.806 | 9 | 0.431 |
| random_gate_budget_0.40_seed049 | 0.850 | 0.770 | 0.803 | 12 | 0.422 |
| random_gate_budget_0.40_seed050 | 0.900 | 0.790 | 0.821 | 8 | 0.435 |
| random_gate_budget_0.40_seed051 | 0.870 | 0.770 | 0.803 | 11 | 0.431 |
| random_gate_budget_0.40_seed052 | 0.840 | 0.760 | 0.794 | 14 | 0.431 |
| random_gate_budget_0.40_seed053 | 0.870 | 0.820 | 0.846 | 9 | 0.432 |
| random_gate_budget_0.40_seed054 | 0.880 | 0.790 | 0.814 | 9 | 0.419 |
| random_gate_budget_0.40_seed055 | 0.870 | 0.780 | 0.812 | 10 | 0.429 |
| random_gate_budget_0.40_seed056 | 0.870 | 0.770 | 0.803 | 11 | 0.433 |
| random_gate_budget_0.40_seed057 | 0.870 | 0.750 | 0.785 | 11 | 0.428 |
| random_gate_budget_0.40_seed058 | 0.890 | 0.840 | 0.865 | 6 | 0.434 |
| random_gate_budget_0.40_seed059 | 0.890 | 0.790 | 0.819 | 8 | 0.434 |
| random_gate_budget_0.40_seed060 | 0.890 | 0.800 | 0.836 | 9 | 0.429 |
| random_gate_budget_0.40_seed061 | 0.890 | 0.790 | 0.818 | 8 | 0.433 |
| random_gate_budget_0.40_seed062 | 0.890 | 0.790 | 0.817 | 8 | 0.428 |
| random_gate_budget_0.40_seed063 | 0.880 | 0.800 | 0.829 | 9 | 0.438 |
| random_gate_budget_0.40_seed064 | 0.880 | 0.800 | 0.827 | 9 | 0.438 |
| random_gate_budget_0.40_seed065 | 0.880 | 0.800 | 0.830 | 9 | 0.427 |
| random_gate_budget_0.40_seed066 | 0.870 | 0.800 | 0.832 | 9 | 0.414 |
| random_gate_budget_0.40_seed067 | 0.890 | 0.800 | 0.830 | 9 | 0.421 |
| random_gate_budget_0.40_seed068 | 0.880 | 0.770 | 0.801 | 10 | 0.429 |
| random_gate_budget_0.40_seed069 | 0.870 | 0.790 | 0.823 | 11 | 0.430 |
| random_gate_budget_0.40_seed070 | 0.890 | 0.820 | 0.848 | 7 | 0.433 |
| random_gate_budget_0.40_seed071 | 0.910 | 0.820 | 0.850 | 6 | 0.421 |
| random_gate_budget_0.40_seed072 | 0.860 | 0.780 | 0.810 | 11 | 0.433 |
| random_gate_budget_0.40_seed073 | 0.850 | 0.770 | 0.803 | 12 | 0.422 |
| random_gate_budget_0.40_seed074 | 0.840 | 0.800 | 0.822 | 11 | 0.423 |
| random_gate_budget_0.40_seed075 | 0.860 | 0.790 | 0.821 | 10 | 0.436 |
| random_gate_budget_0.40_seed076 | 0.850 | 0.780 | 0.816 | 13 | 0.429 |
| random_gate_budget_0.40_seed077 | 0.890 | 0.790 | 0.820 | 8 | 0.432 |
| random_gate_budget_0.40_seed078 | 0.890 | 0.780 | 0.813 | 9 | 0.439 |
| random_gate_budget_0.40_seed079 | 0.890 | 0.800 | 0.831 | 9 | 0.427 |
| random_gate_budget_0.40_seed080 | 0.870 | 0.770 | 0.804 | 11 | 0.427 |
| random_gate_budget_0.40_seed081 | 0.860 | 0.810 | 0.835 | 9 | 0.422 |
| random_gate_budget_0.40_seed082 | 0.910 | 0.790 | 0.825 | 7 | 0.421 |
| random_gate_budget_0.40_seed083 | 0.870 | 0.810 | 0.841 | 9 | 0.425 |
| random_gate_budget_0.40_seed084 | 0.880 | 0.780 | 0.807 | 9 | 0.423 |
| random_gate_budget_0.40_seed085 | 0.870 | 0.780 | 0.816 | 10 | 0.431 |
| random_gate_budget_0.40_seed086 | 0.880 | 0.790 | 0.822 | 9 | 0.435 |
| random_gate_budget_0.40_seed087 | 0.880 | 0.790 | 0.823 | 9 | 0.433 |
| random_gate_budget_0.40_seed088 | 0.860 | 0.760 | 0.794 | 12 | 0.434 |
| random_gate_budget_0.40_seed089 | 0.860 | 0.760 | 0.795 | 12 | 0.426 |
| random_gate_budget_0.40_seed090 | 0.870 | 0.790 | 0.814 | 9 | 0.433 |
| random_gate_budget_0.40_seed091 | 0.860 | 0.780 | 0.807 | 11 | 0.430 |
| random_gate_budget_0.40_seed092 | 0.900 | 0.790 | 0.821 | 8 | 0.428 |
| random_gate_budget_0.40_seed093 | 0.900 | 0.800 | 0.827 | 7 | 0.433 |
| random_gate_budget_0.40_seed094 | 0.840 | 0.770 | 0.804 | 12 | 0.432 |
| random_gate_budget_0.40_seed095 | 0.900 | 0.780 | 0.809 | 8 | 0.428 |
| random_gate_budget_0.40_seed096 | 0.880 | 0.790 | 0.820 | 9 | 0.436 |
| random_gate_budget_0.40_seed097 | 0.890 | 0.780 | 0.806 | 9 | 0.428 |
| random_gate_budget_0.40_seed098 | 0.880 | 0.800 | 0.834 | 9 | 0.432 |
| random_gate_budget_0.40_seed099 | 0.880 | 0.810 | 0.844 | 9 | 0.428 |
| risk_guided_doc_patch_k2 | 0.920 | 0.800 | 0.829 | 6 | 0.554 |
| safe_gate_budget_0.10 | 0.740 | 0.760 | 0.797 | 20 | 0.071 |
| safe_gate_budget_0.25 | 0.830 | 0.740 | 0.772 | 14 | 0.230 |
| safe_gate_budget_0.40 | 0.910 | 0.810 | 0.841 | 6 | 0.409 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::boundary_sensitive | 1.000 | 0.850 | 0 |
| full_prefill::conflict | 1.000 | 0.450 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.850 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.750 | 0.800 | 3 |
| prefix_conditioned_naive_global::conflict | 0.350 | 0.400 | 10 |
| prefix_conditioned_naive_global::distractor_heavy | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::multi_hop | 0.650 | 0.650 | 6 |
| prefix_conditioned_naive_global::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed000::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed000::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.10_seed000::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed000::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed000::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed001::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed001::conflict | 0.450 | 0.400 | 8 |
| random_gate_budget_0.10_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed001::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed001::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed002::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed002::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed002::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed002::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed003::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.10_seed003::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed004::conflict | 0.400 | 0.350 | 10 |
| random_gate_budget_0.10_seed004::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed004::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed005::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed005::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed005::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed005::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed005::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed006::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed006::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed006::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed006::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed007::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed007::conflict | 0.450 | 0.400 | 8 |
| random_gate_budget_0.10_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed008::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed008::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed009::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::multi_hop | 0.650 | 0.600 | 6 |
| random_gate_budget_0.10_seed009::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed010::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed010::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed010::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed010::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed010::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed011::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed011::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.10_seed011::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed011::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed011::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed012::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed012::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed012::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed012::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed012::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed013::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.10_seed013::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed013::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed013::multi_hop | 0.600 | 0.600 | 7 |
| random_gate_budget_0.10_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed014::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed014::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed014::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed014::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed014::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed015::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed015::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed015::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed015::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.10_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed016::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed016::conflict | 0.400 | 0.350 | 10 |
| random_gate_budget_0.10_seed016::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed016::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed016::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed017::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed017::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.10_seed017::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed017::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed017::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed018::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed018::conflict | 0.500 | 0.500 | 7 |
| random_gate_budget_0.10_seed018::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed018::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed018::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed019::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed019::conflict | 0.400 | 0.350 | 10 |
| random_gate_budget_0.10_seed019::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed019::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed019::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed020::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed020::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed020::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed020::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed020::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed021::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed021::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed021::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed021::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed021::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed022::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed022::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed022::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed022::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed023::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed023::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed023::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed023::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed024::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed024::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.10_seed024::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed024::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed025::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed025::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed025::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed025::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed025::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed026::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed026::conflict | 0.500 | 0.350 | 9 |
| random_gate_budget_0.10_seed026::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed026::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed026::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed027::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed027::conflict | 0.400 | 0.450 | 9 |
| random_gate_budget_0.10_seed027::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed027::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed027::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed028::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.10_seed028::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.10_seed028::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed028::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed028::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed029::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed029::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed029::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed029::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed029::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed030::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed030::conflict | 0.500 | 0.350 | 9 |
| random_gate_budget_0.10_seed030::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed030::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.10_seed030::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed031::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed031::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.10_seed031::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed031::multi_hop | 0.600 | 0.600 | 7 |
| random_gate_budget_0.10_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed032::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed032::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed032::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed032::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.10_seed032::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed033::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed033::conflict | 0.550 | 0.350 | 8 |
| random_gate_budget_0.10_seed033::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed033::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed033::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed034::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed034::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed034::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed034::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed034::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed035::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed035::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed035::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed035::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed035::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed036::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed036::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed036::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed036::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed036::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed037::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed037::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed037::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed037::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.10_seed037::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed038::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed038::conflict | 0.500 | 0.300 | 9 |
| random_gate_budget_0.10_seed038::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed038::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed038::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed039::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed039::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed039::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed039::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed039::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed040::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed040::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed040::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed040::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.10_seed040::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed041::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed041::conflict | 0.400 | 0.350 | 10 |
| random_gate_budget_0.10_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed041::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed041::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed042::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed042::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.10_seed042::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed042::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed042::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed043::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed043::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed043::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed043::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed044::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed044::conflict | 0.450 | 0.400 | 8 |
| random_gate_budget_0.10_seed044::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed044::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed044::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed045::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed045::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.10_seed045::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed045::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed046::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed046::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.10_seed046::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed046::multi_hop | 0.600 | 0.600 | 7 |
| random_gate_budget_0.10_seed046::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed047::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed047::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed047::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed047::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.10_seed047::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed048::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.10_seed048::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.10_seed048::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed048::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed048::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed049::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed049::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed049::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed049::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed049::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed050::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed050::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed050::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed050::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed050::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed051::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed051::conflict | 0.400 | 0.350 | 10 |
| random_gate_budget_0.10_seed051::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed051::multi_hop | 0.600 | 0.600 | 7 |
| random_gate_budget_0.10_seed051::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed052::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed052::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed052::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed052::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed052::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed053::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed053::conflict | 0.400 | 0.450 | 9 |
| random_gate_budget_0.10_seed053::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed053::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed054::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed054::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed054::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed054::multi_hop | 0.650 | 0.600 | 6 |
| random_gate_budget_0.10_seed054::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed055::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.10_seed055::conflict | 0.500 | 0.500 | 7 |
| random_gate_budget_0.10_seed055::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed055::multi_hop | 0.600 | 0.600 | 7 |
| random_gate_budget_0.10_seed055::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed056::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.10_seed056::conflict | 0.400 | 0.450 | 9 |
| random_gate_budget_0.10_seed056::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed056::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed056::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed057::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed057::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed057::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed057::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed057::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed058::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed058::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed058::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed058::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed059::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed059::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.10_seed059::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed059::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed059::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed060::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.10_seed060::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed060::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed060::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed061::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed061::conflict | 0.500 | 0.400 | 7 |
| random_gate_budget_0.10_seed061::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed061::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.10_seed061::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed062::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed062::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.10_seed062::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed062::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed062::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed063::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed063::conflict | 0.650 | 0.250 | 7 |
| random_gate_budget_0.10_seed063::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed063::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed063::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed064::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed064::conflict | 0.400 | 0.450 | 9 |
| random_gate_budget_0.10_seed064::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed064::multi_hop | 0.600 | 0.600 | 7 |
| random_gate_budget_0.10_seed064::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed065::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.10_seed065::conflict | 0.400 | 0.350 | 10 |
| random_gate_budget_0.10_seed065::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed065::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed065::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed066::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed066::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed066::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed066::multi_hop | 0.600 | 0.600 | 7 |
| random_gate_budget_0.10_seed066::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed067::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed067::conflict | 0.400 | 0.350 | 10 |
| random_gate_budget_0.10_seed067::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed067::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed067::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed068::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.10_seed068::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.10_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed068::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed068::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed069::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed069::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed069::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed069::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed070::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed070::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed070::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed070::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed071::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed071::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed071::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed071::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed072::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed072::conflict | 0.450 | 0.400 | 8 |
| random_gate_budget_0.10_seed072::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed072::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed073::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed073::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.10_seed073::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed073::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed074::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.10_seed074::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed074::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed074::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed074::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed075::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed075::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.10_seed075::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed075::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed075::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed076::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed076::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed076::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed076::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed076::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed077::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed077::conflict | 0.400 | 0.450 | 9 |
| random_gate_budget_0.10_seed077::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed077::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed077::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed078::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed078::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed078::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed078::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed078::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed079::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed079::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed079::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed079::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed080::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed080::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed080::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed080::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed080::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed081::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed081::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed081::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed081::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed081::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed082::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed082::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed082::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed082::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed082::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed083::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed083::conflict | 0.350 | 0.400 | 10 |
| random_gate_budget_0.10_seed083::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed083::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed083::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed084::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed084::conflict | 0.600 | 0.500 | 5 |
| random_gate_budget_0.10_seed084::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed084::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed084::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed085::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed085::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed085::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed085::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed085::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed086::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed086::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed086::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed086::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.10_seed086::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed087::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed087::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed087::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed087::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed088::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed088::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.10_seed088::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed088::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed088::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed089::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed089::conflict | 0.500 | 0.450 | 8 |
| random_gate_budget_0.10_seed089::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed089::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed089::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed090::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed090::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed090::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed090::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed090::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed091::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed091::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed091::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed091::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed092::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed092::conflict | 0.450 | 0.300 | 10 |
| random_gate_budget_0.10_seed092::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed092::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed092::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed093::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.10_seed093::conflict | 0.500 | 0.400 | 7 |
| random_gate_budget_0.10_seed093::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed093::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.10_seed093::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed094::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed094::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.10_seed094::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed094::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed095::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed095::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed095::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed095::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.10_seed095::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed096::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed096::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.10_seed096::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed096::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed096::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed097::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed097::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed097::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed097::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed097::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed098::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed098::conflict | 0.400 | 0.350 | 10 |
| random_gate_budget_0.10_seed098::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed098::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.10_seed098::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed099::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.10_seed099::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed099::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed099::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.10_seed099::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed000::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed000::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.25_seed000::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed000::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed000::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed001::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.25_seed001::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.25_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed001::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed001::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed002::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed002::conflict | 0.600 | 0.350 | 6 |
| random_gate_budget_0.25_seed002::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed002::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.25_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed003::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed003::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.25_seed003::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed003::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed004::conflict | 0.550 | 0.300 | 8 |
| random_gate_budget_0.25_seed004::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed004::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed005::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed005::conflict | 0.500 | 0.300 | 9 |
| random_gate_budget_0.25_seed005::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed005::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed006::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed006::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.25_seed006::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed006::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed006::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed007::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed007::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed008::conflict | 0.550 | 0.350 | 8 |
| random_gate_budget_0.25_seed008::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.25_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed009::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed009::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed010::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed010::conflict | 0.600 | 0.450 | 6 |
| random_gate_budget_0.25_seed010::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed010::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed010::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed011::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed011::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.25_seed011::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed011::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.25_seed011::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed012::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed012::conflict | 0.600 | 0.350 | 7 |
| random_gate_budget_0.25_seed012::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed012::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed012::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed013::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed013::conflict | 0.550 | 0.350 | 7 |
| random_gate_budget_0.25_seed013::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed013::multi_hop | 0.600 | 0.600 | 7 |
| random_gate_budget_0.25_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed014::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed014::conflict | 0.700 | 0.500 | 3 |
| random_gate_budget_0.25_seed014::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed014::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed014::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed015::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed015::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed015::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed015::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed016::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed016::conflict | 0.550 | 0.450 | 7 |
| random_gate_budget_0.25_seed016::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed016::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed016::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed017::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed017::conflict | 0.700 | 0.350 | 6 |
| random_gate_budget_0.25_seed017::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed017::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed017::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed018::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed018::conflict | 0.600 | 0.500 | 5 |
| random_gate_budget_0.25_seed018::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed018::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed018::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed019::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed019::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.25_seed019::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed019::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed019::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed020::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed020::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.25_seed020::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed020::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed020::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed021::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed021::conflict | 0.600 | 0.250 | 8 |
| random_gate_budget_0.25_seed021::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed021::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed021::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed022::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed022::conflict | 0.500 | 0.350 | 9 |
| random_gate_budget_0.25_seed022::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed022::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed023::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed023::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed023::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed023::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed024::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed024::conflict | 0.650 | 0.300 | 7 |
| random_gate_budget_0.25_seed024::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed024::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed025::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed025::conflict | 0.650 | 0.450 | 5 |
| random_gate_budget_0.25_seed025::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed025::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed025::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed026::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed026::conflict | 0.600 | 0.300 | 8 |
| random_gate_budget_0.25_seed026::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed026::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed026::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed027::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed027::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.25_seed027::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed027::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed027::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed028::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed028::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.25_seed028::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed028::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.25_seed028::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed029::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed029::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.25_seed029::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed029::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed029::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed030::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed030::conflict | 0.650 | 0.350 | 7 |
| random_gate_budget_0.25_seed030::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed030::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed030::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed031::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed031::conflict | 0.650 | 0.450 | 5 |
| random_gate_budget_0.25_seed031::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed031::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed032::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed032::conflict | 0.600 | 0.350 | 6 |
| random_gate_budget_0.25_seed032::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed032::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed032::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed033::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed033::conflict | 0.700 | 0.350 | 6 |
| random_gate_budget_0.25_seed033::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed033::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed033::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed034::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed034::conflict | 0.600 | 0.350 | 7 |
| random_gate_budget_0.25_seed034::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed034::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed034::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed035::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed035::conflict | 0.750 | 0.250 | 5 |
| random_gate_budget_0.25_seed035::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed035::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed035::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed036::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed036::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.25_seed036::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed036::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed036::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed037::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed037::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed037::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed037::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed037::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed038::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed038::conflict | 0.550 | 0.300 | 8 |
| random_gate_budget_0.25_seed038::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed038::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed038::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed039::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed039::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed039::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed039::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed039::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed040::boundary_sensitive | 0.900 | 0.950 | 0 |
| random_gate_budget_0.25_seed040::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.25_seed040::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed040::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.25_seed040::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed041::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed041::conflict | 0.600 | 0.350 | 7 |
| random_gate_budget_0.25_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed041::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed041::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed042::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed042::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.25_seed042::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed042::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.25_seed042::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed043::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed043::conflict | 0.600 | 0.300 | 7 |
| random_gate_budget_0.25_seed043::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed043::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed044::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed044::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed044::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed044::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed044::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed045::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed045::conflict | 0.550 | 0.350 | 8 |
| random_gate_budget_0.25_seed045::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed045::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed046::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed046::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed046::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed046::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed046::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed047::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed047::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed047::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed047::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed047::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed048::boundary_sensitive | 0.950 | 0.900 | 0 |
| random_gate_budget_0.25_seed048::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.25_seed048::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed048::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed048::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed049::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed049::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed049::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed049::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed049::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed050::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed050::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.25_seed050::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed050::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed050::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed051::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed051::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.25_seed051::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed051::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed051::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed052::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed052::conflict | 0.450 | 0.400 | 9 |
| random_gate_budget_0.25_seed052::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed052::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed052::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed053::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed053::conflict | 0.600 | 0.400 | 7 |
| random_gate_budget_0.25_seed053::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed053::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed054::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed054::conflict | 0.650 | 0.400 | 6 |
| random_gate_budget_0.25_seed054::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed054::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed054::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed055::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed055::conflict | 0.600 | 0.450 | 6 |
| random_gate_budget_0.25_seed055::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed055::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.25_seed055::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed056::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed056::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.25_seed056::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed056::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed056::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed057::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.25_seed057::conflict | 0.700 | 0.300 | 5 |
| random_gate_budget_0.25_seed057::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed057::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed057::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed058::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed058::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed058::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed058::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed059::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed059::conflict | 0.650 | 0.300 | 6 |
| random_gate_budget_0.25_seed059::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed059::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed059::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed060::boundary_sensitive | 0.900 | 0.950 | 0 |
| random_gate_budget_0.25_seed060::conflict | 0.550 | 0.450 | 7 |
| random_gate_budget_0.25_seed060::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed060::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.25_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed061::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed061::conflict | 0.600 | 0.300 | 7 |
| random_gate_budget_0.25_seed061::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed061::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed061::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed062::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.25_seed062::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.25_seed062::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed062::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed062::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed063::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed063::conflict | 0.700 | 0.300 | 6 |
| random_gate_budget_0.25_seed063::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed063::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed063::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed064::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed064::conflict | 0.600 | 0.350 | 7 |
| random_gate_budget_0.25_seed064::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed064::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed064::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed065::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed065::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.25_seed065::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed065::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.25_seed065::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed066::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed066::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed066::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed066::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed066::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed067::boundary_sensitive | 0.950 | 0.900 | 0 |
| random_gate_budget_0.25_seed067::conflict | 0.650 | 0.300 | 7 |
| random_gate_budget_0.25_seed067::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed067::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed067::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed068::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed068::conflict | 0.700 | 0.300 | 6 |
| random_gate_budget_0.25_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed068::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed068::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed069::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed069::conflict | 0.550 | 0.300 | 9 |
| random_gate_budget_0.25_seed069::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed069::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed070::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed070::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed070::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed070::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed071::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed071::conflict | 0.550 | 0.350 | 7 |
| random_gate_budget_0.25_seed071::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed071::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed072::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed072::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed072::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed072::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed073::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed073::conflict | 0.450 | 0.450 | 8 |
| random_gate_budget_0.25_seed073::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed073::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed074::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed074::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.25_seed074::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed074::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed074::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed075::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.25_seed075::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed075::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed075::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed075::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed076::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed076::conflict | 0.500 | 0.300 | 9 |
| random_gate_budget_0.25_seed076::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed076::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.25_seed076::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed077::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed077::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed077::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed077::multi_hop | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed077::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed078::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed078::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed078::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed078::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed078::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed079::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed079::conflict | 0.600 | 0.350 | 7 |
| random_gate_budget_0.25_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed079::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed079::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed080::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed080::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed080::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed080::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed080::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed081::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed081::conflict | 0.550 | 0.400 | 6 |
| random_gate_budget_0.25_seed081::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed081::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed081::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed082::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed082::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.25_seed082::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed082::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed082::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed083::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed083::conflict | 0.500 | 0.500 | 7 |
| random_gate_budget_0.25_seed083::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed083::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.25_seed083::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed084::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed084::conflict | 0.700 | 0.500 | 3 |
| random_gate_budget_0.25_seed084::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed084::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed084::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed085::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed085::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed085::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed085::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.25_seed085::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed086::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed086::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed086::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed086::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed086::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed087::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed087::conflict | 0.550 | 0.350 | 8 |
| random_gate_budget_0.25_seed087::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed087::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed088::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed088::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.25_seed088::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed088::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.25_seed088::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed089::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed089::conflict | 0.650 | 0.350 | 7 |
| random_gate_budget_0.25_seed089::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed089::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed089::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed090::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed090::conflict | 0.650 | 0.450 | 4 |
| random_gate_budget_0.25_seed090::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed090::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed090::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed091::boundary_sensitive | 0.700 | 0.750 | 4 |
| random_gate_budget_0.25_seed091::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.25_seed091::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed091::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed092::boundary_sensitive | 0.750 | 0.800 | 3 |
| random_gate_budget_0.25_seed092::conflict | 0.650 | 0.300 | 7 |
| random_gate_budget_0.25_seed092::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed092::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed092::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed093::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed093::conflict | 0.600 | 0.350 | 6 |
| random_gate_budget_0.25_seed093::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed093::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed093::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed094::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed094::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed094::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed094::multi_hop | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed095::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed095::conflict | 0.550 | 0.300 | 8 |
| random_gate_budget_0.25_seed095::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed095::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed095::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed096::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.25_seed096::conflict | 0.550 | 0.350 | 8 |
| random_gate_budget_0.25_seed096::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed096::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed096::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed097::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.25_seed097::conflict | 0.650 | 0.300 | 7 |
| random_gate_budget_0.25_seed097::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed097::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed097::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed098::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.25_seed098::conflict | 0.500 | 0.450 | 8 |
| random_gate_budget_0.25_seed098::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed098::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.25_seed098::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed099::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.25_seed099::conflict | 0.650 | 0.250 | 7 |
| random_gate_budget_0.25_seed099::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed099::multi_hop | 0.650 | 0.650 | 6 |
| random_gate_budget_0.25_seed099::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed000::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed000::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed000::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed000::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed001::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed001::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed002::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed002::conflict | 0.700 | 0.250 | 6 |
| random_gate_budget_0.40_seed002::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed003::conflict | 0.800 | 0.300 | 4 |
| random_gate_budget_0.40_seed003::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed004::conflict | 0.850 | 0.350 | 3 |
| random_gate_budget_0.40_seed004::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed005::conflict | 0.750 | 0.350 | 4 |
| random_gate_budget_0.40_seed005::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed006::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed006::conflict | 0.750 | 0.300 | 5 |
| random_gate_budget_0.40_seed006::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed006::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed006::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed007::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed007::conflict | 0.750 | 0.300 | 5 |
| random_gate_budget_0.40_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed008::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed008::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.40_seed009::conflict | 0.750 | 0.350 | 4 |
| random_gate_budget_0.40_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed009::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed010::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed010::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed010::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed010::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed010::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed011::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed011::conflict | 0.800 | 0.400 | 3 |
| random_gate_budget_0.40_seed011::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed011::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed011::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed012::boundary_sensitive | 0.950 | 0.900 | 0 |
| random_gate_budget_0.40_seed012::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.40_seed012::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed012::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.40_seed012::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed013::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed013::conflict | 0.800 | 0.300 | 4 |
| random_gate_budget_0.40_seed013::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed013::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.40_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed014::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed014::conflict | 0.750 | 0.450 | 3 |
| random_gate_budget_0.40_seed014::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed014::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed014::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed015::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed015::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed015::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed015::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed016::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed016::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed016::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed016::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.40_seed016::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed017::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed017::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed017::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed017::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed017::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed018::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed018::conflict | 0.750 | 0.450 | 3 |
| random_gate_budget_0.40_seed018::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed018::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed018::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed019::boundary_sensitive | 0.950 | 0.900 | 0 |
| random_gate_budget_0.40_seed019::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed019::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed019::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed019::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed020::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed020::conflict | 0.750 | 0.400 | 4 |
| random_gate_budget_0.40_seed020::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed020::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed020::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed021::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed021::conflict | 0.750 | 0.300 | 5 |
| random_gate_budget_0.40_seed021::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed021::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed021::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed022::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed022::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed022::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed022::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.40_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed023::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed023::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed023::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed023::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed024::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed024::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed024::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed024::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed025::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed025::conflict | 0.850 | 0.350 | 3 |
| random_gate_budget_0.40_seed025::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed025::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed025::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed026::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed026::conflict | 0.750 | 0.300 | 5 |
| random_gate_budget_0.40_seed026::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed026::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed026::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed027::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.40_seed027::conflict | 0.800 | 0.300 | 4 |
| random_gate_budget_0.40_seed027::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed027::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed027::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed028::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed028::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed028::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed028::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed028::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed029::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed029::conflict | 0.700 | 0.350 | 6 |
| random_gate_budget_0.40_seed029::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed029::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed029::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed030::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed030::conflict | 0.850 | 0.350 | 3 |
| random_gate_budget_0.40_seed030::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed030::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed030::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed031::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed031::conflict | 0.750 | 0.400 | 4 |
| random_gate_budget_0.40_seed031::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed031::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed032::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed032::conflict | 0.800 | 0.300 | 4 |
| random_gate_budget_0.40_seed032::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed032::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed032::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed033::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed033::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed033::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed033::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.40_seed033::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed034::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed034::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed034::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed034::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.40_seed034::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed035::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed035::conflict | 0.800 | 0.300 | 4 |
| random_gate_budget_0.40_seed035::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed035::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed035::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed036::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed036::conflict | 0.650 | 0.300 | 7 |
| random_gate_budget_0.40_seed036::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed036::multi_hop | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed036::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed037::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed037::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed037::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed037::multi_hop | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed037::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed038::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed038::conflict | 0.700 | 0.300 | 6 |
| random_gate_budget_0.40_seed038::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed038::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed038::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed039::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed039::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed039::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed039::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed039::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed040::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed040::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed040::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed040::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed040::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed041::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed041::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed041::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed041::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed042::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed042::conflict | 0.850 | 0.350 | 3 |
| random_gate_budget_0.40_seed042::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed042::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.40_seed042::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed043::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed043::conflict | 0.700 | 0.300 | 5 |
| random_gate_budget_0.40_seed043::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed043::multi_hop | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed044::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed044::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed044::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed044::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed044::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed045::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed045::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed045::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed045::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed046::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed046::conflict | 0.850 | 0.350 | 3 |
| random_gate_budget_0.40_seed046::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed046::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed046::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed047::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.40_seed047::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.40_seed047::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed047::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed047::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed048::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed048::conflict | 0.800 | 0.300 | 4 |
| random_gate_budget_0.40_seed048::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed048::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed048::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed049::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed049::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.40_seed049::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed049::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed049::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed050::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed050::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed050::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed050::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed050::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed051::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed051::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed051::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed051::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.40_seed051::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed052::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed052::conflict | 0.600 | 0.300 | 8 |
| random_gate_budget_0.40_seed052::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed052::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed052::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed053::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed053::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed053::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed053::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed054::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed054::conflict | 0.750 | 0.400 | 4 |
| random_gate_budget_0.40_seed054::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed054::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed054::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed055::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed055::conflict | 0.750 | 0.400 | 4 |
| random_gate_budget_0.40_seed055::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed055::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed055::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed056::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed056::conflict | 0.750 | 0.300 | 5 |
| random_gate_budget_0.40_seed056::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed056::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.40_seed056::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed057::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed057::conflict | 0.750 | 0.250 | 5 |
| random_gate_budget_0.40_seed057::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed057::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed057::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed058::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed058::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed058::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed058::multi_hop | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed059::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed059::conflict | 0.800 | 0.400 | 3 |
| random_gate_budget_0.40_seed059::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed059::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed059::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed060::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed060::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed060::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed060::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed061::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed061::conflict | 0.800 | 0.400 | 3 |
| random_gate_budget_0.40_seed061::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed061::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed061::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed062::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed062::conflict | 0.800 | 0.400 | 3 |
| random_gate_budget_0.40_seed062::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed062::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed062::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed063::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed063::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed063::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed063::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed063::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed064::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed064::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed064::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed064::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed064::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed065::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed065::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.40_seed065::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed065::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed065::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed066::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed066::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.40_seed066::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed066::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed066::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed067::boundary_sensitive | 0.950 | 0.900 | 0 |
| random_gate_budget_0.40_seed067::conflict | 0.700 | 0.350 | 6 |
| random_gate_budget_0.40_seed067::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed067::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed067::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed068::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed068::conflict | 0.750 | 0.300 | 5 |
| random_gate_budget_0.40_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed068::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed068::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed069::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed069::conflict | 0.650 | 0.350 | 7 |
| random_gate_budget_0.40_seed069::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed069::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed070::boundary_sensitive | 0.950 | 0.900 | 0 |
| random_gate_budget_0.40_seed070::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed070::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed070::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed071::boundary_sensitive | 0.950 | 0.900 | 0 |
| random_gate_budget_0.40_seed071::conflict | 0.750 | 0.400 | 4 |
| random_gate_budget_0.40_seed071::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed071::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed072::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed072::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed072::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed072::multi_hop | 0.700 | 0.700 | 5 |
| random_gate_budget_0.40_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed073::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed073::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed073::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed073::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed074::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed074::conflict | 0.650 | 0.450 | 5 |
| random_gate_budget_0.40_seed074::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed074::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed074::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed075::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed075::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.40_seed075::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed075::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed075::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed076::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed076::conflict | 0.600 | 0.300 | 8 |
| random_gate_budget_0.40_seed076::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed076::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed076::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed077::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed077::conflict | 0.850 | 0.350 | 3 |
| random_gate_budget_0.40_seed077::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed077::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed077::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed078::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed078::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed078::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed078::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed078::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed079::boundary_sensitive | 0.950 | 0.900 | 0 |
| random_gate_budget_0.40_seed079::conflict | 0.650 | 0.300 | 7 |
| random_gate_budget_0.40_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed079::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed079::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed080::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed080::conflict | 0.700 | 0.300 | 6 |
| random_gate_budget_0.40_seed080::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed080::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed080::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed081::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed081::conflict | 0.650 | 0.500 | 4 |
| random_gate_budget_0.40_seed081::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed081::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed081::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed082::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed082::conflict | 0.800 | 0.300 | 4 |
| random_gate_budget_0.40_seed082::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed082::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed082::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed083::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed083::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed083::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed083::multi_hop | 0.750 | 0.750 | 4 |
| random_gate_budget_0.40_seed083::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed084::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed084::conflict | 0.800 | 0.400 | 3 |
| random_gate_budget_0.40_seed084::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed084::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed084::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed085::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.40_seed085::conflict | 0.750 | 0.300 | 5 |
| random_gate_budget_0.40_seed085::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed085::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed085::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed086::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed086::conflict | 0.750 | 0.400 | 4 |
| random_gate_budget_0.40_seed086::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed086::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed086::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed087::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_gate_budget_0.40_seed087::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed087::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed087::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed088::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed088::conflict | 0.700 | 0.300 | 6 |
| random_gate_budget_0.40_seed088::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed088::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed088::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed089::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed089::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed089::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed089::multi_hop | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed089::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed090::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed090::conflict | 0.700 | 0.400 | 4 |
| random_gate_budget_0.40_seed090::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed090::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed090::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed091::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed091::conflict | 0.650 | 0.350 | 6 |
| random_gate_budget_0.40_seed091::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed091::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed092::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed092::conflict | 0.800 | 0.350 | 4 |
| random_gate_budget_0.40_seed092::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed092::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed092::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed093::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed093::conflict | 0.750 | 0.350 | 4 |
| random_gate_budget_0.40_seed093::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed093::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed093::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed094::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed094::conflict | 0.600 | 0.350 | 6 |
| random_gate_budget_0.40_seed094::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed094::multi_hop | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed095::boundary_sensitive | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed095::conflict | 0.850 | 0.350 | 3 |
| random_gate_budget_0.40_seed095::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed095::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed095::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed096::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed096::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed096::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed096::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed096::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed097::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed097::conflict | 0.750 | 0.300 | 5 |
| random_gate_budget_0.40_seed097::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed097::multi_hop | 0.800 | 0.750 | 3 |
| random_gate_budget_0.40_seed097::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed098::boundary_sensitive | 0.900 | 0.850 | 1 |
| random_gate_budget_0.40_seed098::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.40_seed098::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed098::multi_hop | 0.850 | 0.800 | 2 |
| random_gate_budget_0.40_seed098::single_evidence | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed099::boundary_sensitive | 0.850 | 0.900 | 1 |
| random_gate_budget_0.40_seed099::conflict | 0.750 | 0.350 | 5 |
| random_gate_budget_0.40_seed099::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed099::multi_hop | 0.800 | 0.800 | 3 |
| random_gate_budget_0.40_seed099::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::boundary_sensitive | 0.900 | 0.850 | 1 |
| risk_guided_doc_patch_k2::conflict | 0.850 | 0.350 | 3 |
| risk_guided_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::multi_hop | 0.850 | 0.800 | 2 |
| risk_guided_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.10::boundary_sensitive | 0.750 | 0.800 | 3 |
| safe_gate_budget_0.10::conflict | 0.350 | 0.400 | 10 |
| safe_gate_budget_0.10::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.10::multi_hop | 0.650 | 0.650 | 6 |
| safe_gate_budget_0.10::single_evidence | 0.950 | 0.950 | 1 |
| safe_gate_budget_0.25::boundary_sensitive | 0.750 | 0.800 | 3 |
| safe_gate_budget_0.25::conflict | 0.800 | 0.300 | 4 |
| safe_gate_budget_0.25::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.25::multi_hop | 0.650 | 0.650 | 6 |
| safe_gate_budget_0.25::single_evidence | 0.950 | 0.950 | 1 |
| safe_gate_budget_0.40::boundary_sensitive | 0.900 | 0.950 | 0 |
| safe_gate_budget_0.40::conflict | 0.850 | 0.350 | 3 |
| safe_gate_budget_0.40::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.40::multi_hop | 0.800 | 0.750 | 3 |
| safe_gate_budget_0.40::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| multihop_0008_noisy | multi_hop | 4.71503 | `Velora` | `Nimbar` | `Velora` |
| single_0000_noisy | single_evidence | 3.55488 | `Mira Solen` | `Valen` | `Mira Solen` |
| multihop_0003_noisy | multi_hop | 2.88178 | `Lydora` | `Fenric` | `Lydora` |
| multihop_0009_noisy | multi_hop | 2.73159 | `Project Valen was designed by Priya Holt, who was born in Mariton` | `The designer of Project Valen was born in Mariton.` | `Mariton` |
| boundary_0013_noisy | boundary_sensitive | 2.7126 | `1956` | `2003` | `2003` |
| conflict_0004_noisy | conflict | 2.32223 | `According to the official schedule, the Aster Port observatory opens at 8 AM` | `11 AM` | `8 AM` |
| multihop_0006_noisy | multi_hop | 2.20957 | `Rivenfall` | `Ilya Marr` | `Rivenfall` |
| conflict_0012_noisy | conflict | 1.84323 | `According to the official schedule, the Lydora observatory opens at 8` | `10 AM` | `8 AM` |
| multihop_0007_noisy | multi_hop | 1.75636 | `Vera Noll` | `Norwick` | `Norwick` |
| multihop_0018_noisy | multi_hop | 1.75557 | `Velora` | `The designer of Project Nimbar was born in Velora.` | `Velora` |

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
