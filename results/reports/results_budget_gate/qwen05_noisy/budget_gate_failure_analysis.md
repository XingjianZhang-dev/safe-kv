# Budget Gate Failure Analysis

## Pareto Summary

| target | actual | safe equiv | random mean | percentile | changed+wrong |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.099 | 0.680 | 0.724 | 0.020 | 24 |
| 0.25 | 0.251 | 0.780 | 0.775 | 0.700 | 17 |
| 0.40 | 0.401 | 0.860 | 0.822 | 0.980 | 10 |

# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.830 | 0.865 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.690 | 0.740 | 0.784 | 23 | 0.000 |
| random_gate_budget_0.10_seed000 | 0.730 | 0.750 | 0.794 | 20 | 0.105 |
| random_gate_budget_0.10_seed001 | 0.730 | 0.760 | 0.795 | 20 | 0.103 |
| random_gate_budget_0.10_seed002 | 0.730 | 0.760 | 0.797 | 19 | 0.118 |
| random_gate_budget_0.10_seed003 | 0.730 | 0.770 | 0.802 | 19 | 0.118 |
| random_gate_budget_0.10_seed004 | 0.720 | 0.720 | 0.767 | 22 | 0.105 |
| random_gate_budget_0.10_seed005 | 0.720 | 0.750 | 0.790 | 21 | 0.101 |
| random_gate_budget_0.10_seed006 | 0.720 | 0.750 | 0.795 | 21 | 0.109 |
| random_gate_budget_0.10_seed007 | 0.730 | 0.770 | 0.804 | 19 | 0.107 |
| random_gate_budget_0.10_seed008 | 0.760 | 0.770 | 0.804 | 18 | 0.116 |
| random_gate_budget_0.10_seed009 | 0.720 | 0.730 | 0.770 | 22 | 0.110 |
| random_gate_budget_0.10_seed010 | 0.730 | 0.730 | 0.777 | 22 | 0.105 |
| random_gate_budget_0.10_seed011 | 0.740 | 0.750 | 0.795 | 19 | 0.110 |
| random_gate_budget_0.10_seed012 | 0.710 | 0.740 | 0.785 | 22 | 0.102 |
| random_gate_budget_0.10_seed013 | 0.690 | 0.720 | 0.764 | 24 | 0.113 |
| random_gate_budget_0.10_seed014 | 0.720 | 0.760 | 0.804 | 21 | 0.115 |
| random_gate_budget_0.10_seed015 | 0.720 | 0.720 | 0.769 | 23 | 0.107 |
| random_gate_budget_0.10_seed016 | 0.740 | 0.750 | 0.790 | 20 | 0.104 |
| random_gate_budget_0.10_seed017 | 0.740 | 0.760 | 0.802 | 19 | 0.105 |
| random_gate_budget_0.10_seed018 | 0.710 | 0.740 | 0.779 | 22 | 0.105 |
| random_gate_budget_0.10_seed019 | 0.730 | 0.730 | 0.784 | 21 | 0.120 |
| random_gate_budget_0.10_seed020 | 0.730 | 0.750 | 0.795 | 20 | 0.113 |
| random_gate_budget_0.10_seed021 | 0.720 | 0.740 | 0.779 | 21 | 0.096 |
| random_gate_budget_0.10_seed022 | 0.710 | 0.710 | 0.761 | 24 | 0.100 |
| random_gate_budget_0.10_seed023 | 0.730 | 0.750 | 0.789 | 20 | 0.106 |
| random_gate_budget_0.10_seed024 | 0.720 | 0.770 | 0.800 | 20 | 0.101 |
| random_gate_budget_0.10_seed025 | 0.730 | 0.750 | 0.797 | 20 | 0.109 |
| random_gate_budget_0.10_seed026 | 0.760 | 0.750 | 0.794 | 18 | 0.102 |
| random_gate_budget_0.10_seed027 | 0.710 | 0.760 | 0.804 | 21 | 0.102 |
| random_gate_budget_0.10_seed028 | 0.750 | 0.750 | 0.797 | 19 | 0.111 |
| random_gate_budget_0.10_seed029 | 0.690 | 0.700 | 0.752 | 25 | 0.100 |
| random_gate_budget_0.10_seed030 | 0.760 | 0.780 | 0.814 | 17 | 0.100 |
| random_gate_budget_0.10_seed031 | 0.720 | 0.760 | 0.794 | 20 | 0.105 |
| random_gate_budget_0.10_seed032 | 0.710 | 0.720 | 0.773 | 23 | 0.104 |
| random_gate_budget_0.10_seed033 | 0.740 | 0.760 | 0.802 | 19 | 0.107 |
| random_gate_budget_0.10_seed034 | 0.730 | 0.730 | 0.774 | 21 | 0.103 |
| random_gate_budget_0.10_seed035 | 0.710 | 0.740 | 0.779 | 21 | 0.106 |
| random_gate_budget_0.10_seed036 | 0.700 | 0.720 | 0.764 | 24 | 0.115 |
| random_gate_budget_0.10_seed037 | 0.720 | 0.730 | 0.779 | 22 | 0.107 |
| random_gate_budget_0.10_seed038 | 0.760 | 0.780 | 0.812 | 17 | 0.110 |
| random_gate_budget_0.10_seed039 | 0.720 | 0.770 | 0.810 | 20 | 0.104 |
| random_gate_budget_0.10_seed040 | 0.740 | 0.750 | 0.795 | 20 | 0.093 |
| random_gate_budget_0.10_seed041 | 0.730 | 0.740 | 0.780 | 21 | 0.113 |
| random_gate_budget_0.10_seed042 | 0.720 | 0.760 | 0.792 | 20 | 0.115 |
| random_gate_budget_0.10_seed043 | 0.730 | 0.730 | 0.780 | 22 | 0.112 |
| random_gate_budget_0.10_seed044 | 0.710 | 0.740 | 0.779 | 22 | 0.114 |
| random_gate_budget_0.10_seed045 | 0.690 | 0.750 | 0.789 | 22 | 0.101 |
| random_gate_budget_0.10_seed046 | 0.730 | 0.750 | 0.797 | 20 | 0.114 |
| random_gate_budget_0.10_seed047 | 0.700 | 0.740 | 0.784 | 23 | 0.109 |
| random_gate_budget_0.10_seed048 | 0.710 | 0.740 | 0.784 | 22 | 0.111 |
| random_gate_budget_0.10_seed049 | 0.730 | 0.740 | 0.782 | 21 | 0.105 |
| random_gate_budget_0.10_seed050 | 0.710 | 0.750 | 0.795 | 21 | 0.110 |
| random_gate_budget_0.10_seed051 | 0.690 | 0.730 | 0.773 | 24 | 0.104 |
| random_gate_budget_0.10_seed052 | 0.700 | 0.700 | 0.750 | 24 | 0.115 |
| random_gate_budget_0.10_seed053 | 0.700 | 0.730 | 0.783 | 23 | 0.113 |
| random_gate_budget_0.10_seed054 | 0.720 | 0.750 | 0.794 | 20 | 0.110 |
| random_gate_budget_0.10_seed055 | 0.710 | 0.760 | 0.799 | 21 | 0.115 |
| random_gate_budget_0.10_seed056 | 0.700 | 0.720 | 0.767 | 23 | 0.104 |
| random_gate_budget_0.10_seed057 | 0.680 | 0.720 | 0.765 | 24 | 0.109 |
| random_gate_budget_0.10_seed058 | 0.740 | 0.760 | 0.802 | 19 | 0.104 |
| random_gate_budget_0.10_seed059 | 0.720 | 0.740 | 0.782 | 21 | 0.099 |
| random_gate_budget_0.10_seed060 | 0.720 | 0.740 | 0.792 | 21 | 0.116 |
| random_gate_budget_0.10_seed061 | 0.720 | 0.760 | 0.799 | 20 | 0.109 |
| random_gate_budget_0.10_seed062 | 0.750 | 0.750 | 0.792 | 19 | 0.114 |
| random_gate_budget_0.10_seed063 | 0.760 | 0.770 | 0.801 | 17 | 0.105 |
| random_gate_budget_0.10_seed064 | 0.710 | 0.740 | 0.784 | 22 | 0.114 |
| random_gate_budget_0.10_seed065 | 0.720 | 0.720 | 0.764 | 22 | 0.112 |
| random_gate_budget_0.10_seed066 | 0.750 | 0.730 | 0.765 | 20 | 0.096 |
| random_gate_budget_0.10_seed067 | 0.720 | 0.740 | 0.787 | 21 | 0.096 |
| random_gate_budget_0.10_seed068 | 0.730 | 0.770 | 0.805 | 19 | 0.104 |
| random_gate_budget_0.10_seed069 | 0.740 | 0.760 | 0.805 | 19 | 0.112 |
| random_gate_budget_0.10_seed070 | 0.710 | 0.740 | 0.785 | 22 | 0.104 |
| random_gate_budget_0.10_seed071 | 0.740 | 0.720 | 0.772 | 22 | 0.109 |
| random_gate_budget_0.10_seed072 | 0.720 | 0.770 | 0.802 | 19 | 0.103 |
| random_gate_budget_0.10_seed073 | 0.720 | 0.730 | 0.770 | 22 | 0.105 |
| random_gate_budget_0.10_seed074 | 0.690 | 0.730 | 0.774 | 23 | 0.095 |
| random_gate_budget_0.10_seed075 | 0.730 | 0.760 | 0.804 | 20 | 0.104 |
| random_gate_budget_0.10_seed076 | 0.730 | 0.730 | 0.777 | 22 | 0.107 |
| random_gate_budget_0.10_seed077 | 0.680 | 0.730 | 0.774 | 24 | 0.099 |
| random_gate_budget_0.10_seed078 | 0.700 | 0.750 | 0.789 | 22 | 0.111 |
| random_gate_budget_0.10_seed079 | 0.760 | 0.730 | 0.772 | 20 | 0.104 |
| random_gate_budget_0.10_seed080 | 0.720 | 0.750 | 0.789 | 20 | 0.106 |
| random_gate_budget_0.10_seed081 | 0.740 | 0.750 | 0.795 | 20 | 0.103 |
| random_gate_budget_0.10_seed082 | 0.720 | 0.730 | 0.775 | 22 | 0.109 |
| random_gate_budget_0.10_seed083 | 0.730 | 0.720 | 0.772 | 22 | 0.108 |
| random_gate_budget_0.10_seed084 | 0.750 | 0.750 | 0.784 | 19 | 0.111 |
| random_gate_budget_0.10_seed085 | 0.690 | 0.710 | 0.757 | 24 | 0.110 |
| random_gate_budget_0.10_seed086 | 0.720 | 0.760 | 0.802 | 20 | 0.109 |
| random_gate_budget_0.10_seed087 | 0.720 | 0.740 | 0.795 | 21 | 0.113 |
| random_gate_budget_0.10_seed088 | 0.730 | 0.770 | 0.809 | 20 | 0.113 |
| random_gate_budget_0.10_seed089 | 0.730 | 0.750 | 0.800 | 20 | 0.113 |
| random_gate_budget_0.10_seed090 | 0.730 | 0.710 | 0.761 | 23 | 0.101 |
| random_gate_budget_0.10_seed091 | 0.730 | 0.770 | 0.807 | 19 | 0.104 |
| random_gate_budget_0.10_seed092 | 0.750 | 0.750 | 0.794 | 19 | 0.115 |
| random_gate_budget_0.10_seed093 | 0.740 | 0.760 | 0.797 | 19 | 0.105 |
| random_gate_budget_0.10_seed094 | 0.730 | 0.770 | 0.802 | 19 | 0.116 |
| random_gate_budget_0.10_seed095 | 0.710 | 0.740 | 0.775 | 22 | 0.108 |
| random_gate_budget_0.10_seed096 | 0.720 | 0.740 | 0.785 | 21 | 0.113 |
| random_gate_budget_0.10_seed097 | 0.750 | 0.750 | 0.794 | 19 | 0.109 |
| random_gate_budget_0.10_seed098 | 0.770 | 0.760 | 0.808 | 17 | 0.109 |
| random_gate_budget_0.10_seed099 | 0.750 | 0.760 | 0.799 | 18 | 0.105 |
| random_gate_budget_0.25_seed000 | 0.750 | 0.730 | 0.775 | 20 | 0.262 |
| random_gate_budget_0.25_seed001 | 0.770 | 0.770 | 0.802 | 17 | 0.268 |
| random_gate_budget_0.25_seed002 | 0.760 | 0.770 | 0.798 | 17 | 0.275 |
| random_gate_budget_0.25_seed003 | 0.780 | 0.770 | 0.803 | 16 | 0.274 |
| random_gate_budget_0.25_seed004 | 0.770 | 0.760 | 0.799 | 17 | 0.266 |
| random_gate_budget_0.25_seed005 | 0.800 | 0.750 | 0.794 | 16 | 0.271 |
| random_gate_budget_0.25_seed006 | 0.760 | 0.770 | 0.815 | 18 | 0.263 |
| random_gate_budget_0.25_seed007 | 0.740 | 0.750 | 0.792 | 19 | 0.268 |
| random_gate_budget_0.25_seed008 | 0.780 | 0.750 | 0.792 | 18 | 0.277 |
| random_gate_budget_0.25_seed009 | 0.780 | 0.790 | 0.820 | 16 | 0.270 |
| random_gate_budget_0.25_seed010 | 0.790 | 0.740 | 0.782 | 18 | 0.260 |
| random_gate_budget_0.25_seed011 | 0.770 | 0.750 | 0.797 | 18 | 0.270 |
| random_gate_budget_0.25_seed012 | 0.750 | 0.730 | 0.759 | 19 | 0.263 |
| random_gate_budget_0.25_seed013 | 0.740 | 0.740 | 0.777 | 20 | 0.283 |
| random_gate_budget_0.25_seed014 | 0.760 | 0.810 | 0.834 | 16 | 0.275 |
| random_gate_budget_0.25_seed015 | 0.780 | 0.770 | 0.809 | 17 | 0.270 |
| random_gate_budget_0.25_seed016 | 0.780 | 0.730 | 0.782 | 19 | 0.273 |
| random_gate_budget_0.25_seed017 | 0.780 | 0.750 | 0.787 | 17 | 0.270 |
| random_gate_budget_0.25_seed018 | 0.740 | 0.750 | 0.785 | 20 | 0.265 |
| random_gate_budget_0.25_seed019 | 0.800 | 0.780 | 0.820 | 15 | 0.270 |
| random_gate_budget_0.25_seed020 | 0.820 | 0.830 | 0.854 | 11 | 0.275 |
| random_gate_budget_0.25_seed021 | 0.780 | 0.750 | 0.778 | 16 | 0.259 |
| random_gate_budget_0.25_seed022 | 0.780 | 0.750 | 0.803 | 18 | 0.270 |
| random_gate_budget_0.25_seed023 | 0.760 | 0.780 | 0.818 | 17 | 0.266 |
| random_gate_budget_0.25_seed024 | 0.790 | 0.820 | 0.845 | 13 | 0.267 |
| random_gate_budget_0.25_seed025 | 0.760 | 0.750 | 0.792 | 18 | 0.266 |
| random_gate_budget_0.25_seed026 | 0.820 | 0.760 | 0.798 | 14 | 0.281 |
| random_gate_budget_0.25_seed027 | 0.770 | 0.750 | 0.789 | 18 | 0.260 |
| random_gate_budget_0.25_seed028 | 0.800 | 0.780 | 0.815 | 15 | 0.275 |
| random_gate_budget_0.25_seed029 | 0.760 | 0.730 | 0.780 | 19 | 0.264 |
| random_gate_budget_0.25_seed030 | 0.820 | 0.770 | 0.808 | 14 | 0.266 |
| random_gate_budget_0.25_seed031 | 0.780 | 0.780 | 0.805 | 16 | 0.270 |
| random_gate_budget_0.25_seed032 | 0.790 | 0.740 | 0.778 | 18 | 0.264 |
| random_gate_budget_0.25_seed033 | 0.780 | 0.740 | 0.780 | 18 | 0.264 |
| random_gate_budget_0.25_seed034 | 0.760 | 0.740 | 0.774 | 18 | 0.271 |
| random_gate_budget_0.25_seed035 | 0.790 | 0.770 | 0.800 | 15 | 0.265 |
| random_gate_budget_0.25_seed036 | 0.770 | 0.750 | 0.792 | 19 | 0.261 |
| random_gate_budget_0.25_seed037 | 0.780 | 0.740 | 0.781 | 18 | 0.274 |
| random_gate_budget_0.25_seed038 | 0.770 | 0.770 | 0.800 | 17 | 0.265 |
| random_gate_budget_0.25_seed039 | 0.780 | 0.790 | 0.820 | 16 | 0.265 |
| random_gate_budget_0.25_seed040 | 0.800 | 0.770 | 0.805 | 15 | 0.258 |
| random_gate_budget_0.25_seed041 | 0.810 | 0.760 | 0.802 | 15 | 0.267 |
| random_gate_budget_0.25_seed042 | 0.760 | 0.780 | 0.800 | 17 | 0.277 |
| random_gate_budget_0.25_seed043 | 0.820 | 0.760 | 0.796 | 15 | 0.273 |
| random_gate_budget_0.25_seed044 | 0.800 | 0.810 | 0.842 | 14 | 0.283 |
| random_gate_budget_0.25_seed045 | 0.740 | 0.760 | 0.805 | 18 | 0.262 |
| random_gate_budget_0.25_seed046 | 0.760 | 0.780 | 0.817 | 17 | 0.269 |
| random_gate_budget_0.25_seed047 | 0.750 | 0.750 | 0.792 | 19 | 0.274 |
| random_gate_budget_0.25_seed048 | 0.750 | 0.770 | 0.802 | 18 | 0.271 |
| random_gate_budget_0.25_seed049 | 0.750 | 0.740 | 0.777 | 20 | 0.269 |
| random_gate_budget_0.25_seed050 | 0.790 | 0.800 | 0.830 | 14 | 0.272 |
| random_gate_budget_0.25_seed051 | 0.740 | 0.730 | 0.774 | 21 | 0.261 |
| random_gate_budget_0.25_seed052 | 0.740 | 0.680 | 0.734 | 23 | 0.275 |
| random_gate_budget_0.25_seed053 | 0.750 | 0.740 | 0.780 | 20 | 0.274 |
| random_gate_budget_0.25_seed054 | 0.780 | 0.780 | 0.817 | 15 | 0.255 |
| random_gate_budget_0.25_seed055 | 0.770 | 0.770 | 0.803 | 17 | 0.281 |
| random_gate_budget_0.25_seed056 | 0.780 | 0.750 | 0.802 | 17 | 0.273 |
| random_gate_budget_0.25_seed057 | 0.760 | 0.750 | 0.774 | 18 | 0.266 |
| random_gate_budget_0.25_seed058 | 0.790 | 0.790 | 0.826 | 14 | 0.267 |
| random_gate_budget_0.25_seed059 | 0.760 | 0.750 | 0.782 | 18 | 0.268 |
| random_gate_budget_0.25_seed060 | 0.780 | 0.720 | 0.775 | 19 | 0.256 |
| random_gate_budget_0.25_seed061 | 0.760 | 0.770 | 0.809 | 17 | 0.272 |
| random_gate_budget_0.25_seed062 | 0.820 | 0.790 | 0.829 | 13 | 0.265 |
| random_gate_budget_0.25_seed063 | 0.790 | 0.730 | 0.766 | 17 | 0.270 |
| random_gate_budget_0.25_seed064 | 0.800 | 0.750 | 0.790 | 16 | 0.271 |
| random_gate_budget_0.25_seed065 | 0.760 | 0.720 | 0.774 | 20 | 0.273 |
| random_gate_budget_0.25_seed066 | 0.790 | 0.760 | 0.790 | 17 | 0.262 |
| random_gate_budget_0.25_seed067 | 0.760 | 0.770 | 0.805 | 17 | 0.264 |
| random_gate_budget_0.25_seed068 | 0.810 | 0.820 | 0.844 | 11 | 0.263 |
| random_gate_budget_0.25_seed069 | 0.780 | 0.750 | 0.797 | 17 | 0.275 |
| random_gate_budget_0.25_seed070 | 0.780 | 0.770 | 0.805 | 17 | 0.273 |
| random_gate_budget_0.25_seed071 | 0.770 | 0.750 | 0.792 | 19 | 0.280 |
| random_gate_budget_0.25_seed072 | 0.760 | 0.750 | 0.792 | 18 | 0.269 |
| random_gate_budget_0.25_seed073 | 0.760 | 0.740 | 0.777 | 19 | 0.268 |
| random_gate_budget_0.25_seed074 | 0.740 | 0.730 | 0.774 | 20 | 0.263 |
| random_gate_budget_0.25_seed075 | 0.790 | 0.760 | 0.795 | 16 | 0.269 |
| random_gate_budget_0.25_seed076 | 0.810 | 0.750 | 0.790 | 16 | 0.273 |
| random_gate_budget_0.25_seed077 | 0.760 | 0.730 | 0.779 | 20 | 0.265 |
| random_gate_budget_0.25_seed078 | 0.750 | 0.780 | 0.819 | 17 | 0.277 |
| random_gate_budget_0.25_seed079 | 0.790 | 0.720 | 0.756 | 18 | 0.263 |
| random_gate_budget_0.25_seed080 | 0.770 | 0.740 | 0.785 | 18 | 0.259 |
| random_gate_budget_0.25_seed081 | 0.760 | 0.740 | 0.778 | 19 | 0.253 |
| random_gate_budget_0.25_seed082 | 0.740 | 0.700 | 0.755 | 22 | 0.261 |
| random_gate_budget_0.25_seed083 | 0.740 | 0.720 | 0.771 | 22 | 0.257 |
| random_gate_budget_0.25_seed084 | 0.800 | 0.790 | 0.820 | 14 | 0.272 |
| random_gate_budget_0.25_seed085 | 0.740 | 0.720 | 0.773 | 21 | 0.276 |
| random_gate_budget_0.25_seed086 | 0.780 | 0.780 | 0.813 | 15 | 0.270 |
| random_gate_budget_0.25_seed087 | 0.770 | 0.740 | 0.788 | 19 | 0.274 |
| random_gate_budget_0.25_seed088 | 0.800 | 0.790 | 0.826 | 14 | 0.287 |
| random_gate_budget_0.25_seed089 | 0.760 | 0.740 | 0.785 | 18 | 0.274 |
| random_gate_budget_0.25_seed090 | 0.790 | 0.740 | 0.778 | 18 | 0.258 |
| random_gate_budget_0.25_seed091 | 0.770 | 0.770 | 0.814 | 17 | 0.270 |
| random_gate_budget_0.25_seed092 | 0.770 | 0.750 | 0.791 | 17 | 0.272 |
| random_gate_budget_0.25_seed093 | 0.770 | 0.760 | 0.796 | 17 | 0.270 |
| random_gate_budget_0.25_seed094 | 0.800 | 0.740 | 0.780 | 17 | 0.273 |
| random_gate_budget_0.25_seed095 | 0.760 | 0.740 | 0.787 | 19 | 0.262 |
| random_gate_budget_0.25_seed096 | 0.770 | 0.730 | 0.775 | 19 | 0.273 |
| random_gate_budget_0.25_seed097 | 0.780 | 0.760 | 0.795 | 16 | 0.267 |
| random_gate_budget_0.25_seed098 | 0.800 | 0.770 | 0.820 | 15 | 0.259 |
| random_gate_budget_0.25_seed099 | 0.810 | 0.780 | 0.813 | 14 | 0.273 |
| random_gate_budget_0.40_seed000 | 0.810 | 0.750 | 0.792 | 15 | 0.420 |
| random_gate_budget_0.40_seed001 | 0.830 | 0.750 | 0.789 | 15 | 0.427 |
| random_gate_budget_0.40_seed002 | 0.820 | 0.750 | 0.787 | 14 | 0.428 |
| random_gate_budget_0.40_seed003 | 0.820 | 0.770 | 0.806 | 13 | 0.437 |
| random_gate_budget_0.40_seed004 | 0.840 | 0.780 | 0.807 | 12 | 0.426 |
| random_gate_budget_0.40_seed005 | 0.860 | 0.780 | 0.813 | 11 | 0.434 |
| random_gate_budget_0.40_seed006 | 0.840 | 0.800 | 0.830 | 11 | 0.422 |
| random_gate_budget_0.40_seed007 | 0.830 | 0.790 | 0.824 | 12 | 0.424 |
| random_gate_budget_0.40_seed008 | 0.820 | 0.780 | 0.810 | 14 | 0.428 |
| random_gate_budget_0.40_seed009 | 0.810 | 0.780 | 0.807 | 14 | 0.428 |
| random_gate_budget_0.40_seed010 | 0.820 | 0.770 | 0.804 | 14 | 0.425 |
| random_gate_budget_0.40_seed011 | 0.830 | 0.780 | 0.817 | 13 | 0.432 |
| random_gate_budget_0.40_seed012 | 0.770 | 0.700 | 0.740 | 20 | 0.432 |
| random_gate_budget_0.40_seed013 | 0.850 | 0.770 | 0.802 | 12 | 0.443 |
| random_gate_budget_0.40_seed014 | 0.870 | 0.820 | 0.852 | 9 | 0.435 |
| random_gate_budget_0.40_seed015 | 0.840 | 0.780 | 0.816 | 12 | 0.430 |
| random_gate_budget_0.40_seed016 | 0.820 | 0.750 | 0.789 | 15 | 0.422 |
| random_gate_budget_0.40_seed017 | 0.830 | 0.780 | 0.815 | 13 | 0.432 |
| random_gate_budget_0.40_seed018 | 0.810 | 0.760 | 0.797 | 16 | 0.430 |
| random_gate_budget_0.40_seed019 | 0.850 | 0.790 | 0.829 | 11 | 0.427 |
| random_gate_budget_0.40_seed020 | 0.840 | 0.810 | 0.839 | 11 | 0.433 |
| random_gate_budget_0.40_seed021 | 0.810 | 0.760 | 0.788 | 14 | 0.419 |
| random_gate_budget_0.40_seed022 | 0.830 | 0.780 | 0.817 | 13 | 0.423 |
| random_gate_budget_0.40_seed023 | 0.800 | 0.770 | 0.805 | 15 | 0.425 |
| random_gate_budget_0.40_seed024 | 0.840 | 0.780 | 0.822 | 12 | 0.436 |
| random_gate_budget_0.40_seed025 | 0.830 | 0.790 | 0.815 | 12 | 0.422 |
| random_gate_budget_0.40_seed026 | 0.830 | 0.770 | 0.797 | 13 | 0.428 |
| random_gate_budget_0.40_seed027 | 0.830 | 0.770 | 0.797 | 13 | 0.430 |
| random_gate_budget_0.40_seed028 | 0.840 | 0.780 | 0.817 | 12 | 0.432 |
| random_gate_budget_0.40_seed029 | 0.820 | 0.740 | 0.787 | 15 | 0.430 |
| random_gate_budget_0.40_seed030 | 0.870 | 0.790 | 0.822 | 10 | 0.426 |
| random_gate_budget_0.40_seed031 | 0.850 | 0.780 | 0.809 | 12 | 0.443 |
| random_gate_budget_0.40_seed032 | 0.840 | 0.770 | 0.804 | 13 | 0.420 |
| random_gate_budget_0.40_seed033 | 0.790 | 0.720 | 0.762 | 18 | 0.430 |
| random_gate_budget_0.40_seed034 | 0.800 | 0.760 | 0.800 | 15 | 0.430 |
| random_gate_budget_0.40_seed035 | 0.830 | 0.780 | 0.814 | 12 | 0.433 |
| random_gate_budget_0.40_seed036 | 0.840 | 0.750 | 0.796 | 14 | 0.424 |
| random_gate_budget_0.40_seed037 | 0.790 | 0.740 | 0.774 | 17 | 0.433 |
| random_gate_budget_0.40_seed038 | 0.790 | 0.740 | 0.779 | 17 | 0.437 |
| random_gate_budget_0.40_seed039 | 0.820 | 0.770 | 0.812 | 14 | 0.424 |
| random_gate_budget_0.40_seed040 | 0.820 | 0.760 | 0.800 | 14 | 0.433 |
| random_gate_budget_0.40_seed041 | 0.830 | 0.770 | 0.806 | 13 | 0.432 |
| random_gate_budget_0.40_seed042 | 0.840 | 0.780 | 0.803 | 12 | 0.435 |
| random_gate_budget_0.40_seed043 | 0.830 | 0.760 | 0.790 | 14 | 0.433 |
| random_gate_budget_0.40_seed044 | 0.850 | 0.790 | 0.817 | 11 | 0.434 |
| random_gate_budget_0.40_seed045 | 0.820 | 0.760 | 0.795 | 14 | 0.421 |
| random_gate_budget_0.40_seed046 | 0.820 | 0.790 | 0.819 | 12 | 0.426 |
| random_gate_budget_0.40_seed047 | 0.810 | 0.770 | 0.812 | 15 | 0.417 |
| random_gate_budget_0.40_seed048 | 0.830 | 0.790 | 0.816 | 12 | 0.431 |
| random_gate_budget_0.40_seed049 | 0.780 | 0.740 | 0.775 | 18 | 0.422 |
| random_gate_budget_0.40_seed050 | 0.840 | 0.800 | 0.831 | 11 | 0.435 |
| random_gate_budget_0.40_seed051 | 0.830 | 0.780 | 0.814 | 13 | 0.431 |
| random_gate_budget_0.40_seed052 | 0.810 | 0.720 | 0.771 | 17 | 0.431 |
| random_gate_budget_0.40_seed053 | 0.810 | 0.740 | 0.780 | 16 | 0.432 |
| random_gate_budget_0.40_seed054 | 0.810 | 0.760 | 0.797 | 15 | 0.419 |
| random_gate_budget_0.40_seed055 | 0.810 | 0.780 | 0.810 | 14 | 0.429 |
| random_gate_budget_0.40_seed056 | 0.800 | 0.740 | 0.775 | 16 | 0.433 |
| random_gate_budget_0.40_seed057 | 0.810 | 0.750 | 0.784 | 15 | 0.428 |
| random_gate_budget_0.40_seed058 | 0.830 | 0.810 | 0.844 | 11 | 0.434 |
| random_gate_budget_0.40_seed059 | 0.830 | 0.790 | 0.819 | 12 | 0.434 |
| random_gate_budget_0.40_seed060 | 0.850 | 0.760 | 0.797 | 13 | 0.429 |
| random_gate_budget_0.40_seed061 | 0.820 | 0.770 | 0.803 | 14 | 0.433 |
| random_gate_budget_0.40_seed062 | 0.860 | 0.780 | 0.817 | 11 | 0.428 |
| random_gate_budget_0.40_seed063 | 0.830 | 0.740 | 0.786 | 15 | 0.438 |
| random_gate_budget_0.40_seed064 | 0.830 | 0.770 | 0.806 | 13 | 0.438 |
| random_gate_budget_0.40_seed065 | 0.820 | 0.770 | 0.809 | 14 | 0.427 |
| random_gate_budget_0.40_seed066 | 0.840 | 0.780 | 0.812 | 13 | 0.414 |
| random_gate_budget_0.40_seed067 | 0.820 | 0.760 | 0.797 | 14 | 0.421 |
| random_gate_budget_0.40_seed068 | 0.860 | 0.790 | 0.823 | 10 | 0.429 |
| random_gate_budget_0.40_seed069 | 0.790 | 0.740 | 0.784 | 17 | 0.430 |
| random_gate_budget_0.40_seed070 | 0.800 | 0.790 | 0.816 | 15 | 0.433 |
| random_gate_budget_0.40_seed071 | 0.810 | 0.770 | 0.807 | 15 | 0.421 |
| random_gate_budget_0.40_seed072 | 0.800 | 0.750 | 0.784 | 16 | 0.433 |
| random_gate_budget_0.40_seed073 | 0.820 | 0.770 | 0.804 | 14 | 0.422 |
| random_gate_budget_0.40_seed074 | 0.780 | 0.740 | 0.780 | 18 | 0.423 |
| random_gate_budget_0.40_seed075 | 0.800 | 0.770 | 0.805 | 15 | 0.436 |
| random_gate_budget_0.40_seed076 | 0.830 | 0.740 | 0.787 | 15 | 0.429 |
| random_gate_budget_0.40_seed077 | 0.810 | 0.760 | 0.797 | 15 | 0.432 |
| random_gate_budget_0.40_seed078 | 0.820 | 0.800 | 0.827 | 12 | 0.439 |
| random_gate_budget_0.40_seed079 | 0.840 | 0.760 | 0.798 | 13 | 0.427 |
| random_gate_budget_0.40_seed080 | 0.810 | 0.740 | 0.777 | 16 | 0.427 |
| random_gate_budget_0.40_seed081 | 0.780 | 0.750 | 0.788 | 18 | 0.422 |
| random_gate_budget_0.40_seed082 | 0.830 | 0.770 | 0.804 | 13 | 0.421 |
| random_gate_budget_0.40_seed083 | 0.810 | 0.760 | 0.795 | 15 | 0.425 |
| random_gate_budget_0.40_seed084 | 0.840 | 0.810 | 0.834 | 11 | 0.423 |
| random_gate_budget_0.40_seed085 | 0.830 | 0.790 | 0.829 | 12 | 0.431 |
| random_gate_budget_0.40_seed086 | 0.820 | 0.780 | 0.812 | 13 | 0.435 |
| random_gate_budget_0.40_seed087 | 0.830 | 0.770 | 0.809 | 14 | 0.433 |
| random_gate_budget_0.40_seed088 | 0.810 | 0.780 | 0.820 | 14 | 0.434 |
| random_gate_budget_0.40_seed089 | 0.830 | 0.750 | 0.792 | 14 | 0.426 |
| random_gate_budget_0.40_seed090 | 0.830 | 0.760 | 0.799 | 14 | 0.433 |
| random_gate_budget_0.40_seed091 | 0.810 | 0.770 | 0.805 | 15 | 0.430 |
| random_gate_budget_0.40_seed092 | 0.810 | 0.760 | 0.799 | 14 | 0.428 |
| random_gate_budget_0.40_seed093 | 0.820 | 0.770 | 0.802 | 13 | 0.433 |
| random_gate_budget_0.40_seed094 | 0.800 | 0.750 | 0.785 | 16 | 0.432 |
| random_gate_budget_0.40_seed095 | 0.820 | 0.760 | 0.796 | 14 | 0.428 |
| random_gate_budget_0.40_seed096 | 0.800 | 0.760 | 0.794 | 15 | 0.436 |
| random_gate_budget_0.40_seed097 | 0.810 | 0.790 | 0.820 | 13 | 0.428 |
| random_gate_budget_0.40_seed098 | 0.830 | 0.740 | 0.787 | 15 | 0.432 |
| random_gate_budget_0.40_seed099 | 0.830 | 0.760 | 0.797 | 14 | 0.428 |
| risk_guided_doc_patch_k2 | 0.860 | 0.780 | 0.812 | 11 | 0.554 |
| safe_gate_budget_0.10 | 0.680 | 0.730 | 0.778 | 24 | 0.071 |
| safe_gate_budget_0.25 | 0.780 | 0.730 | 0.766 | 17 | 0.230 |
| safe_gate_budget_0.40 | 0.860 | 0.790 | 0.822 | 10 | 0.409 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::boundary_sensitive | 1.000 | 0.800 | 0 |
| full_prefill::conflict | 1.000 | 0.500 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.850 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.550 | 0.550 | 7 |
| prefix_conditioned_naive_global::conflict | 0.250 | 0.450 | 10 |
| prefix_conditioned_naive_global::distractor_heavy | 0.950 | 0.950 | 1 |
| prefix_conditioned_naive_global::multi_hop | 0.700 | 0.750 | 5 |
| prefix_conditioned_naive_global::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed000::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed000::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed000::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed000::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed001::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed001::conflict | 0.400 | 0.500 | 8 |
| random_gate_budget_0.10_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed001::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed002::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed002::conflict | 0.300 | 0.500 | 8 |
| random_gate_budget_0.10_seed002::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed002::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed003::conflict | 0.400 | 0.550 | 7 |
| random_gate_budget_0.10_seed003::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed003::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed004::conflict | 0.400 | 0.400 | 8 |
| random_gate_budget_0.10_seed004::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed004::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed005::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed005::conflict | 0.350 | 0.500 | 8 |
| random_gate_budget_0.10_seed005::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed005::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed006::conflict | 0.250 | 0.350 | 11 |
| random_gate_budget_0.10_seed006::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed006::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.10_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed007::conflict | 0.300 | 0.550 | 8 |
| random_gate_budget_0.10_seed007::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed007::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed008::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed008::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.10_seed009::conflict | 0.350 | 0.400 | 9 |
| random_gate_budget_0.10_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed009::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed010::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.10_seed010::conflict | 0.350 | 0.350 | 10 |
| random_gate_budget_0.10_seed010::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed010::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.10_seed010::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed011::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed011::conflict | 0.500 | 0.500 | 6 |
| random_gate_budget_0.10_seed011::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed011::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed011::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed012::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed012::conflict | 0.300 | 0.400 | 10 |
| random_gate_budget_0.10_seed012::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed012::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed012::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed013::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed013::conflict | 0.200 | 0.400 | 11 |
| random_gate_budget_0.10_seed013::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed013::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed014::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.10_seed014::conflict | 0.250 | 0.450 | 10 |
| random_gate_budget_0.10_seed014::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed014::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed014::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed015::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed015::conflict | 0.300 | 0.400 | 10 |
| random_gate_budget_0.10_seed015::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed015::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed016::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed016::conflict | 0.350 | 0.450 | 9 |
| random_gate_budget_0.10_seed016::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed016::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.10_seed016::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed017::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed017::conflict | 0.450 | 0.500 | 7 |
| random_gate_budget_0.10_seed017::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed017::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed017::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed018::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed018::conflict | 0.300 | 0.500 | 9 |
| random_gate_budget_0.10_seed018::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed018::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed018::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed019::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed019::conflict | 0.350 | 0.300 | 10 |
| random_gate_budget_0.10_seed019::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed019::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed019::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed020::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed020::conflict | 0.300 | 0.450 | 9 |
| random_gate_budget_0.10_seed020::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed020::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed020::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed021::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed021::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed021::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed021::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed021::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed022::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.10_seed022::conflict | 0.300 | 0.300 | 11 |
| random_gate_budget_0.10_seed022::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed022::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed023::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed023::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed023::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed023::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed024::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed024::conflict | 0.350 | 0.550 | 8 |
| random_gate_budget_0.10_seed024::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed024::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed025::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed025::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed025::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed025::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed025::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed026::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed026::conflict | 0.500 | 0.400 | 7 |
| random_gate_budget_0.10_seed026::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed026::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed026::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed027::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed027::conflict | 0.250 | 0.450 | 10 |
| random_gate_budget_0.10_seed027::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed027::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed027::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed028::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed028::conflict | 0.450 | 0.400 | 8 |
| random_gate_budget_0.10_seed028::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed028::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.10_seed028::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed029::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed029::conflict | 0.300 | 0.300 | 11 |
| random_gate_budget_0.10_seed029::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed029::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed029::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed030::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed030::conflict | 0.400 | 0.550 | 7 |
| random_gate_budget_0.10_seed030::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed030::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed030::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed031::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed031::conflict | 0.350 | 0.500 | 8 |
| random_gate_budget_0.10_seed031::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed031::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed032::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed032::conflict | 0.300 | 0.400 | 10 |
| random_gate_budget_0.10_seed032::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed032::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.10_seed032::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed033::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed033::conflict | 0.500 | 0.550 | 6 |
| random_gate_budget_0.10_seed033::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed033::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed033::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed034::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed034::conflict | 0.350 | 0.400 | 9 |
| random_gate_budget_0.10_seed034::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed034::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.10_seed034::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed035::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed035::conflict | 0.300 | 0.400 | 9 |
| random_gate_budget_0.10_seed035::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed035::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed035::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed036::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.10_seed036::conflict | 0.350 | 0.450 | 9 |
| random_gate_budget_0.10_seed036::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed036::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed036::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed037::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed037::conflict | 0.300 | 0.400 | 10 |
| random_gate_budget_0.10_seed037::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed037::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed037::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed038::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed038::conflict | 0.400 | 0.550 | 7 |
| random_gate_budget_0.10_seed038::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed038::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed038::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed039::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed039::conflict | 0.250 | 0.450 | 10 |
| random_gate_budget_0.10_seed039::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed039::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.10_seed039::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed040::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed040::conflict | 0.300 | 0.400 | 10 |
| random_gate_budget_0.10_seed040::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed040::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed040::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed041::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed041::conflict | 0.350 | 0.450 | 9 |
| random_gate_budget_0.10_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed041::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.10_seed041::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed042::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed042::conflict | 0.400 | 0.550 | 7 |
| random_gate_budget_0.10_seed042::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed042::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed042::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed043::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed043::conflict | 0.350 | 0.350 | 10 |
| random_gate_budget_0.10_seed043::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed043::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed044::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed044::conflict | 0.400 | 0.500 | 8 |
| random_gate_budget_0.10_seed044::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed044::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed044::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed045::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed045::conflict | 0.200 | 0.450 | 10 |
| random_gate_budget_0.10_seed045::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed045::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed046::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed046::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed046::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed046::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed046::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed047::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed047::conflict | 0.250 | 0.450 | 10 |
| random_gate_budget_0.10_seed047::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed047::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed047::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed048::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed048::conflict | 0.350 | 0.450 | 9 |
| random_gate_budget_0.10_seed048::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed048::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed048::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed049::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed049::conflict | 0.350 | 0.350 | 10 |
| random_gate_budget_0.10_seed049::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed049::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.10_seed049::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed050::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed050::conflict | 0.300 | 0.450 | 9 |
| random_gate_budget_0.10_seed050::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed050::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed050::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed051::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.10_seed051::conflict | 0.300 | 0.500 | 9 |
| random_gate_budget_0.10_seed051::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed051::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed051::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed052::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed052::conflict | 0.350 | 0.300 | 10 |
| random_gate_budget_0.10_seed052::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed052::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed052::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed053::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed053::conflict | 0.350 | 0.450 | 9 |
| random_gate_budget_0.10_seed053::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed053::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed054::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed054::conflict | 0.350 | 0.450 | 8 |
| random_gate_budget_0.10_seed054::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed054::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed054::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed055::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed055::conflict | 0.350 | 0.550 | 8 |
| random_gate_budget_0.10_seed055::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed055::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed055::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed056::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed056::conflict | 0.300 | 0.350 | 10 |
| random_gate_budget_0.10_seed056::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed056::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed056::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed057::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed057::conflict | 0.250 | 0.400 | 10 |
| random_gate_budget_0.10_seed057::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed057::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed057::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed058::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed058::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed058::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed058::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed059::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed059::conflict | 0.450 | 0.500 | 7 |
| random_gate_budget_0.10_seed059::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed059::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed059::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed060::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed060::conflict | 0.350 | 0.400 | 9 |
| random_gate_budget_0.10_seed060::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed060::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed061::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed061::conflict | 0.350 | 0.500 | 8 |
| random_gate_budget_0.10_seed061::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed061::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed061::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed062::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed062::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed062::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed062::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed062::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed063::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed063::conflict | 0.550 | 0.550 | 5 |
| random_gate_budget_0.10_seed063::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed063::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed063::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed064::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed064::conflict | 0.200 | 0.400 | 11 |
| random_gate_budget_0.10_seed064::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed064::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed064::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed065::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed065::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed065::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed065::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.10_seed065::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed066::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed066::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.10_seed066::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed066::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.10_seed066::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed067::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed067::conflict | 0.350 | 0.400 | 9 |
| random_gate_budget_0.10_seed067::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed067::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed067::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed068::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed068::conflict | 0.400 | 0.550 | 7 |
| random_gate_budget_0.10_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed068::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed068::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed069::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed069::conflict | 0.350 | 0.500 | 8 |
| random_gate_budget_0.10_seed069::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed069::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed070::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed070::conflict | 0.300 | 0.400 | 10 |
| random_gate_budget_0.10_seed070::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed070::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed071::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed071::conflict | 0.450 | 0.350 | 9 |
| random_gate_budget_0.10_seed071::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed071::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed072::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed072::conflict | 0.350 | 0.550 | 7 |
| random_gate_budget_0.10_seed072::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed072::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed073::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.10_seed073::conflict | 0.350 | 0.500 | 8 |
| random_gate_budget_0.10_seed073::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed073::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed074::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed074::conflict | 0.250 | 0.400 | 10 |
| random_gate_budget_0.10_seed074::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed074::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed074::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed075::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed075::conflict | 0.400 | 0.500 | 8 |
| random_gate_budget_0.10_seed075::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed075::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed075::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed076::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed076::conflict | 0.350 | 0.350 | 10 |
| random_gate_budget_0.10_seed076::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed076::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed076::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed077::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed077::conflict | 0.250 | 0.450 | 10 |
| random_gate_budget_0.10_seed077::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed077::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.10_seed077::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed078::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed078::conflict | 0.250 | 0.500 | 9 |
| random_gate_budget_0.10_seed078::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed078::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed078::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed079::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed079::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.10_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed079::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed079::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed080::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed080::conflict | 0.350 | 0.450 | 8 |
| random_gate_budget_0.10_seed080::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed080::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed080::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed081::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed081::conflict | 0.400 | 0.400 | 9 |
| random_gate_budget_0.10_seed081::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed081::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed081::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed082::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed082::conflict | 0.250 | 0.350 | 11 |
| random_gate_budget_0.10_seed082::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed082::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed082::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed083::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed083::conflict | 0.400 | 0.300 | 10 |
| random_gate_budget_0.10_seed083::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed083::multi_hop | 0.600 | 0.650 | 7 |
| random_gate_budget_0.10_seed083::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed084::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed084::conflict | 0.500 | 0.550 | 6 |
| random_gate_budget_0.10_seed084::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed084::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.10_seed084::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed085::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed085::conflict | 0.350 | 0.400 | 9 |
| random_gate_budget_0.10_seed085::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed085::multi_hop | 0.600 | 0.650 | 7 |
| random_gate_budget_0.10_seed085::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed086::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed086::conflict | 0.300 | 0.450 | 9 |
| random_gate_budget_0.10_seed086::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed086::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.10_seed086::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed087::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed087::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed087::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed087::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed088::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.10_seed088::conflict | 0.350 | 0.550 | 8 |
| random_gate_budget_0.10_seed088::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed088::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed088::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed089::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed089::conflict | 0.350 | 0.500 | 8 |
| random_gate_budget_0.10_seed089::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.10_seed089::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed089::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed090::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.10_seed090::conflict | 0.350 | 0.350 | 10 |
| random_gate_budget_0.10_seed090::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed090::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.10_seed090::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed091::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed091::conflict | 0.350 | 0.500 | 8 |
| random_gate_budget_0.10_seed091::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed091::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.10_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed092::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed092::conflict | 0.450 | 0.400 | 8 |
| random_gate_budget_0.10_seed092::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed092::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.10_seed092::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed093::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed093::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.10_seed093::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed093::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed093::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed094::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed094::conflict | 0.400 | 0.550 | 7 |
| random_gate_budget_0.10_seed094::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed094::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed095::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.10_seed095::conflict | 0.350 | 0.450 | 9 |
| random_gate_budget_0.10_seed095::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed095::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed095::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed096::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed096::conflict | 0.300 | 0.450 | 9 |
| random_gate_budget_0.10_seed096::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed096::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.10_seed096::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed097::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.10_seed097::conflict | 0.450 | 0.400 | 8 |
| random_gate_budget_0.10_seed097::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed097::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.10_seed097::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed098::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.10_seed098::conflict | 0.450 | 0.350 | 8 |
| random_gate_budget_0.10_seed098::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed098::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.10_seed098::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed099::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.10_seed099::conflict | 0.400 | 0.500 | 7 |
| random_gate_budget_0.10_seed099::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.10_seed099::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.10_seed099::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed000::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.25_seed000::conflict | 0.450 | 0.400 | 8 |
| random_gate_budget_0.25_seed000::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed000::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed001::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed001::conflict | 0.550 | 0.600 | 5 |
| random_gate_budget_0.25_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed001::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed002::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed002::conflict | 0.500 | 0.600 | 5 |
| random_gate_budget_0.25_seed002::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed002::multi_hop | 0.650 | 0.600 | 7 |
| random_gate_budget_0.25_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed003::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed003::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed003::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed003::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed004::conflict | 0.500 | 0.450 | 6 |
| random_gate_budget_0.25_seed004::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed004::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed005::conflict | 0.550 | 0.400 | 6 |
| random_gate_budget_0.25_seed005::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed006::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed006::conflict | 0.350 | 0.400 | 9 |
| random_gate_budget_0.25_seed006::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed006::multi_hop | 0.850 | 0.900 | 2 |
| random_gate_budget_0.25_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed007::conflict | 0.400 | 0.500 | 7 |
| random_gate_budget_0.25_seed007::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed007::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed008::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed008::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed008::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed009::conflict | 0.450 | 0.500 | 7 |
| random_gate_budget_0.25_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed009::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed010::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.25_seed010::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed010::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed010::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.25_seed010::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed011::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed011::conflict | 0.600 | 0.500 | 5 |
| random_gate_budget_0.25_seed011::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed011::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed011::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed012::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.25_seed012::conflict | 0.500 | 0.450 | 6 |
| random_gate_budget_0.25_seed012::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed012::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed012::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed013::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed013::conflict | 0.400 | 0.500 | 7 |
| random_gate_budget_0.25_seed013::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed013::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed014::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed014::conflict | 0.450 | 0.700 | 5 |
| random_gate_budget_0.25_seed014::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed014::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed014::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed015::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed015::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.25_seed015::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed015::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed016::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.25_seed016::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed016::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed016::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.25_seed016::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed017::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed017::conflict | 0.600 | 0.550 | 4 |
| random_gate_budget_0.25_seed017::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed017::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed017::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed018::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed018::conflict | 0.450 | 0.550 | 7 |
| random_gate_budget_0.25_seed018::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed018::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed018::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed019::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed019::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.25_seed019::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed019::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.25_seed019::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed020::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed020::conflict | 0.550 | 0.650 | 4 |
| random_gate_budget_0.25_seed020::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed020::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.25_seed020::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed021::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed021::conflict | 0.600 | 0.500 | 4 |
| random_gate_budget_0.25_seed021::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed021::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed021::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed022::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed022::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed022::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed022::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed023::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed023::conflict | 0.400 | 0.500 | 7 |
| random_gate_budget_0.25_seed023::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed023::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed024::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.25_seed024::conflict | 0.500 | 0.600 | 5 |
| random_gate_budget_0.25_seed024::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed024::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed025::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed025::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed025::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed025::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed025::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed026::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed026::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.25_seed026::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed026::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed026::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed027::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed027::conflict | 0.400 | 0.400 | 8 |
| random_gate_budget_0.25_seed027::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed027::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed027::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed028::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.25_seed028::conflict | 0.650 | 0.550 | 4 |
| random_gate_budget_0.25_seed028::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed028::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed028::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed029::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed029::conflict | 0.450 | 0.350 | 8 |
| random_gate_budget_0.25_seed029::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed029::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed029::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed030::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed030::conflict | 0.600 | 0.450 | 5 |
| random_gate_budget_0.25_seed030::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed030::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed030::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed031::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed031::conflict | 0.550 | 0.550 | 5 |
| random_gate_budget_0.25_seed031::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed031::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed032::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed032::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed032::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed032::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed032::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed033::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed033::conflict | 0.600 | 0.500 | 5 |
| random_gate_budget_0.25_seed033::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed033::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed033::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed034::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed034::conflict | 0.500 | 0.450 | 6 |
| random_gate_budget_0.25_seed034::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed034::multi_hop | 0.650 | 0.600 | 7 |
| random_gate_budget_0.25_seed034::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed035::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed035::conflict | 0.600 | 0.550 | 4 |
| random_gate_budget_0.25_seed035::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed035::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed035::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed036::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed036::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.25_seed036::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed036::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed036::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed037::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed037::conflict | 0.450 | 0.350 | 8 |
| random_gate_budget_0.25_seed037::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed037::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.25_seed037::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed038::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed038::conflict | 0.450 | 0.500 | 7 |
| random_gate_budget_0.25_seed038::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed038::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed038::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed039::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.25_seed039::conflict | 0.500 | 0.550 | 6 |
| random_gate_budget_0.25_seed039::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed039::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed039::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed040::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed040::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed040::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed040::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed040::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed041::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed041::conflict | 0.650 | 0.450 | 5 |
| random_gate_budget_0.25_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed041::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed041::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed042::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.25_seed042::conflict | 0.500 | 0.600 | 5 |
| random_gate_budget_0.25_seed042::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed042::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed042::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed043::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.25_seed043::conflict | 0.700 | 0.400 | 5 |
| random_gate_budget_0.25_seed043::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed043::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed044::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.25_seed044::conflict | 0.500 | 0.550 | 6 |
| random_gate_budget_0.25_seed044::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed044::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed044::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed045::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed045::conflict | 0.350 | 0.400 | 8 |
| random_gate_budget_0.25_seed045::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed045::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed046::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed046::conflict | 0.500 | 0.550 | 6 |
| random_gate_budget_0.25_seed046::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed046::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.25_seed046::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed047::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed047::conflict | 0.400 | 0.400 | 8 |
| random_gate_budget_0.25_seed047::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed047::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed047::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed048::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed048::conflict | 0.450 | 0.550 | 6 |
| random_gate_budget_0.25_seed048::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed048::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed048::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed049::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed049::conflict | 0.400 | 0.450 | 8 |
| random_gate_budget_0.25_seed049::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed049::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed049::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed050::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed050::conflict | 0.550 | 0.600 | 4 |
| random_gate_budget_0.25_seed050::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed050::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed050::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed051::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.25_seed051::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.25_seed051::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed051::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed051::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed052::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed052::conflict | 0.450 | 0.250 | 9 |
| random_gate_budget_0.25_seed052::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed052::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed052::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed053::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed053::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.25_seed053::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed053::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.25_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed054::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed054::conflict | 0.550 | 0.500 | 5 |
| random_gate_budget_0.25_seed054::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed054::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed054::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed055::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed055::conflict | 0.550 | 0.550 | 5 |
| random_gate_budget_0.25_seed055::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed055::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.25_seed055::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed056::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed056::conflict | 0.500 | 0.300 | 8 |
| random_gate_budget_0.25_seed056::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed056::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed056::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed057::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.25_seed057::conflict | 0.550 | 0.550 | 5 |
| random_gate_budget_0.25_seed057::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed057::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed057::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed058::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed058::conflict | 0.500 | 0.450 | 6 |
| random_gate_budget_0.25_seed058::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed058::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed059::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.25_seed059::conflict | 0.600 | 0.500 | 5 |
| random_gate_budget_0.25_seed059::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed059::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed059::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed060::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed060::conflict | 0.600 | 0.350 | 7 |
| random_gate_budget_0.25_seed060::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed060::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed061::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed061::conflict | 0.450 | 0.500 | 6 |
| random_gate_budget_0.25_seed061::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed061::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed061::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed062::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed062::conflict | 0.600 | 0.500 | 5 |
| random_gate_budget_0.25_seed062::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed062::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed062::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed063::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed063::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.25_seed063::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed063::multi_hop | 0.650 | 0.600 | 7 |
| random_gate_budget_0.25_seed063::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed064::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed064::conflict | 0.500 | 0.350 | 7 |
| random_gate_budget_0.25_seed064::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed064::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.25_seed064::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed065::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed065::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed065::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed065::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed065::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed066::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.25_seed066::conflict | 0.550 | 0.500 | 6 |
| random_gate_budget_0.25_seed066::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed066::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed066::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed067::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed067::conflict | 0.500 | 0.550 | 5 |
| random_gate_budget_0.25_seed067::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed067::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed067::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed068::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed068::conflict | 0.650 | 0.650 | 2 |
| random_gate_budget_0.25_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed068::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed068::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed069::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed069::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed069::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed069::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed070::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed070::conflict | 0.450 | 0.500 | 7 |
| random_gate_budget_0.25_seed070::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed070::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed071::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed071::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.25_seed071::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed071::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed072::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed072::conflict | 0.450 | 0.450 | 7 |
| random_gate_budget_0.25_seed072::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed072::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed073::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.25_seed073::conflict | 0.450 | 0.450 | 7 |
| random_gate_budget_0.25_seed073::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed073::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed074::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed074::conflict | 0.400 | 0.400 | 8 |
| random_gate_budget_0.25_seed074::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed074::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed074::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed075::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed075::conflict | 0.600 | 0.500 | 5 |
| random_gate_budget_0.25_seed075::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed075::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.25_seed075::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed076::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed076::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed076::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed076::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed076::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed077::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed077::conflict | 0.500 | 0.350 | 8 |
| random_gate_budget_0.25_seed077::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed077::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed077::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed078::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed078::conflict | 0.400 | 0.550 | 6 |
| random_gate_budget_0.25_seed078::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed078::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed078::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed079::boundary_sensitive | 0.550 | 0.500 | 8 |
| random_gate_budget_0.25_seed079::conflict | 0.600 | 0.350 | 6 |
| random_gate_budget_0.25_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed079::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed079::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed080::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed080::conflict | 0.500 | 0.400 | 7 |
| random_gate_budget_0.25_seed080::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed080::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed080::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed081::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.25_seed081::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.25_seed081::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed081::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed081::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed082::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed082::conflict | 0.400 | 0.250 | 10 |
| random_gate_budget_0.25_seed082::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed082::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed082::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed083::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed083::conflict | 0.500 | 0.400 | 8 |
| random_gate_budget_0.25_seed083::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed083::multi_hop | 0.600 | 0.650 | 7 |
| random_gate_budget_0.25_seed083::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed084::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed084::conflict | 0.600 | 0.600 | 4 |
| random_gate_budget_0.25_seed084::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed084::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed084::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed085::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed085::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed085::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed085::multi_hop | 0.600 | 0.650 | 7 |
| random_gate_budget_0.25_seed085::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed086::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed086::conflict | 0.500 | 0.450 | 6 |
| random_gate_budget_0.25_seed086::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed086::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed086::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed087::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed087::conflict | 0.600 | 0.450 | 6 |
| random_gate_budget_0.25_seed087::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed087::multi_hop | 0.650 | 0.700 | 6 |
| random_gate_budget_0.25_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed088::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed088::conflict | 0.600 | 0.550 | 4 |
| random_gate_budget_0.25_seed088::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed088::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed088::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed089::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed089::conflict | 0.550 | 0.500 | 5 |
| random_gate_budget_0.25_seed089::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed089::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed089::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed090::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed090::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed090::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed090::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed090::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed091::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed091::conflict | 0.500 | 0.450 | 7 |
| random_gate_budget_0.25_seed091::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed091::multi_hop | 0.850 | 0.900 | 2 |
| random_gate_budget_0.25_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed092::boundary_sensitive | 0.550 | 0.550 | 7 |
| random_gate_budget_0.25_seed092::conflict | 0.650 | 0.500 | 4 |
| random_gate_budget_0.25_seed092::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed092::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed092::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed093::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.25_seed093::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.25_seed093::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed093::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.25_seed093::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed094::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed094::conflict | 0.600 | 0.400 | 6 |
| random_gate_budget_0.25_seed094::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed094::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed095::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.25_seed095::conflict | 0.550 | 0.400 | 7 |
| random_gate_budget_0.25_seed095::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.25_seed095::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed095::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed096::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed096::conflict | 0.450 | 0.350 | 8 |
| random_gate_budget_0.25_seed096::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed096::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.25_seed096::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed097::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.25_seed097::conflict | 0.550 | 0.450 | 5 |
| random_gate_budget_0.25_seed097::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed097::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.25_seed097::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed098::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.25_seed098::conflict | 0.550 | 0.350 | 7 |
| random_gate_budget_0.25_seed098::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed098::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.25_seed098::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed099::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.25_seed099::conflict | 0.600 | 0.550 | 4 |
| random_gate_budget_0.25_seed099::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.25_seed099::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.25_seed099::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed000::boundary_sensitive | 0.600 | 0.600 | 6 |
| random_gate_budget_0.40_seed000::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.40_seed000::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed000::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed001::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed001::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed001::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed002::conflict | 0.700 | 0.400 | 4 |
| random_gate_budget_0.40_seed002::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed002::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed003::conflict | 0.750 | 0.450 | 3 |
| random_gate_budget_0.40_seed003::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed003::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed004::conflict | 0.750 | 0.550 | 2 |
| random_gate_budget_0.40_seed004::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed004::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed005::conflict | 0.750 | 0.450 | 3 |
| random_gate_budget_0.40_seed005::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed006::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed006::conflict | 0.700 | 0.500 | 3 |
| random_gate_budget_0.40_seed006::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed006::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.40_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed007::conflict | 0.650 | 0.500 | 4 |
| random_gate_budget_0.40_seed007::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed007::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed008::conflict | 0.650 | 0.450 | 5 |
| random_gate_budget_0.40_seed008::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed008::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed009::conflict | 0.650 | 0.600 | 3 |
| random_gate_budget_0.40_seed009::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed009::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed009::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed010::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed010::conflict | 0.700 | 0.550 | 3 |
| random_gate_budget_0.40_seed010::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed010::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed010::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed011::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed011::conflict | 0.800 | 0.550 | 2 |
| random_gate_budget_0.40_seed011::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed011::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed011::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed012::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.40_seed012::conflict | 0.600 | 0.350 | 6 |
| random_gate_budget_0.40_seed012::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed012::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.40_seed012::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed013::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed013::conflict | 0.800 | 0.500 | 2 |
| random_gate_budget_0.40_seed013::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed013::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed013::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed014::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed014::conflict | 0.700 | 0.550 | 3 |
| random_gate_budget_0.40_seed014::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed014::multi_hop | 0.900 | 0.850 | 2 |
| random_gate_budget_0.40_seed014::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed015::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed015::conflict | 0.650 | 0.450 | 4 |
| random_gate_budget_0.40_seed015::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed015::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed015::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed016::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed016::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed016::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed016::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed016::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed017::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed017::conflict | 0.650 | 0.500 | 4 |
| random_gate_budget_0.40_seed017::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed017::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed017::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed018::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed018::conflict | 0.650 | 0.500 | 5 |
| random_gate_budget_0.40_seed018::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed018::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed018::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed019::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed019::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed019::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed019::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed019::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed020::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed020::conflict | 0.650 | 0.550 | 4 |
| random_gate_budget_0.40_seed020::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed020::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed020::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed021::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed021::conflict | 0.650 | 0.450 | 4 |
| random_gate_budget_0.40_seed021::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed021::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.40_seed021::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed022::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed022::conflict | 0.650 | 0.500 | 4 |
| random_gate_budget_0.40_seed022::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed022::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed022::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed023::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed023::conflict | 0.600 | 0.450 | 5 |
| random_gate_budget_0.40_seed023::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed023::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed023::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed024::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed024::conflict | 0.800 | 0.450 | 3 |
| random_gate_budget_0.40_seed024::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed024::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.40_seed024::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed025::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed025::conflict | 0.700 | 0.600 | 2 |
| random_gate_budget_0.40_seed025::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed025::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed025::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed026::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed026::conflict | 0.750 | 0.550 | 2 |
| random_gate_budget_0.40_seed026::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed026::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed026::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed027::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed027::conflict | 0.700 | 0.500 | 3 |
| random_gate_budget_0.40_seed027::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed027::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed027::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed028::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed028::conflict | 0.800 | 0.500 | 2 |
| random_gate_budget_0.40_seed028::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed028::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed028::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed029::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed029::conflict | 0.650 | 0.350 | 5 |
| random_gate_budget_0.40_seed029::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed029::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed029::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed030::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed030::conflict | 0.850 | 0.550 | 1 |
| random_gate_budget_0.40_seed030::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed030::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed030::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed031::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed031::conflict | 0.750 | 0.500 | 3 |
| random_gate_budget_0.40_seed031::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed031::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed031::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed032::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed032::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed032::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed032::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed032::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed033::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed033::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed033::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed033::multi_hop | 0.650 | 0.600 | 7 |
| random_gate_budget_0.40_seed033::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed034::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed034::conflict | 0.600 | 0.450 | 5 |
| random_gate_budget_0.40_seed034::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed034::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.40_seed034::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed035::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed035::conflict | 0.750 | 0.550 | 2 |
| random_gate_budget_0.40_seed035::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed035::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed035::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed036::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed036::conflict | 0.750 | 0.400 | 4 |
| random_gate_budget_0.40_seed036::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed036::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed036::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed037::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed037::conflict | 0.600 | 0.450 | 5 |
| random_gate_budget_0.40_seed037::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed037::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed037::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed038::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed038::conflict | 0.600 | 0.450 | 5 |
| random_gate_budget_0.40_seed038::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed038::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed038::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed039::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed039::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.40_seed039::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed039::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.40_seed039::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed040::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed040::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.40_seed040::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed040::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed040::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed041::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed041::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed041::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed041::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.40_seed041::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed042::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed042::conflict | 0.750 | 0.550 | 2 |
| random_gate_budget_0.40_seed042::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed042::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed042::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed043::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed043::conflict | 0.750 | 0.500 | 3 |
| random_gate_budget_0.40_seed043::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed043::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed043::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed044::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed044::conflict | 0.750 | 0.550 | 2 |
| random_gate_budget_0.40_seed044::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed044::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed044::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed045::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed045::conflict | 0.700 | 0.500 | 3 |
| random_gate_budget_0.40_seed045::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed045::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed045::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed046::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed046::conflict | 0.700 | 0.600 | 2 |
| random_gate_budget_0.40_seed046::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed046::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed046::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed047::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed047::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.40_seed047::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed047::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed047::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed048::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed048::conflict | 0.750 | 0.550 | 2 |
| random_gate_budget_0.40_seed048::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed048::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.40_seed048::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed049::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed049::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.40_seed049::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed049::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed049::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed050::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed050::conflict | 0.700 | 0.500 | 3 |
| random_gate_budget_0.40_seed050::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed050::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.40_seed050::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed051::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed051::conflict | 0.750 | 0.600 | 2 |
| random_gate_budget_0.40_seed051::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed051::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed051::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed052::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed052::conflict | 0.650 | 0.300 | 6 |
| random_gate_budget_0.40_seed052::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed052::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed052::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed053::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed053::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.40_seed053::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed053::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed053::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed054::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed054::conflict | 0.650 | 0.500 | 4 |
| random_gate_budget_0.40_seed054::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed054::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed054::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed055::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed055::conflict | 0.600 | 0.550 | 4 |
| random_gate_budget_0.40_seed055::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed055::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed055::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed056::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed056::conflict | 0.650 | 0.450 | 4 |
| random_gate_budget_0.40_seed056::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed056::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed056::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed057::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.40_seed057::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed057::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed057::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed057::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed058::boundary_sensitive | 0.750 | 0.750 | 3 |
| random_gate_budget_0.40_seed058::conflict | 0.600 | 0.450 | 5 |
| random_gate_budget_0.40_seed058::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed058::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.40_seed058::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed059::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed059::conflict | 0.700 | 0.550 | 3 |
| random_gate_budget_0.40_seed059::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed059::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed059::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed060::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed060::conflict | 0.850 | 0.500 | 2 |
| random_gate_budget_0.40_seed060::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed060::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed060::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed061::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed061::conflict | 0.700 | 0.550 | 3 |
| random_gate_budget_0.40_seed061::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed061::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed061::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed062::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed062::conflict | 0.800 | 0.500 | 2 |
| random_gate_budget_0.40_seed062::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed062::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed062::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed063::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed063::conflict | 0.750 | 0.400 | 4 |
| random_gate_budget_0.40_seed063::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed063::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed063::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed064::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed064::conflict | 0.650 | 0.450 | 4 |
| random_gate_budget_0.40_seed064::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed064::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed064::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed065::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed065::conflict | 0.650 | 0.500 | 4 |
| random_gate_budget_0.40_seed065::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed065::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed065::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed066::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed066::conflict | 0.750 | 0.550 | 3 |
| random_gate_budget_0.40_seed066::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed066::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed066::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed067::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed067::conflict | 0.700 | 0.500 | 3 |
| random_gate_budget_0.40_seed067::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed067::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed067::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed068::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.40_seed068::conflict | 0.800 | 0.500 | 2 |
| random_gate_budget_0.40_seed068::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed068::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed068::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed069::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed069::conflict | 0.600 | 0.450 | 5 |
| random_gate_budget_0.40_seed069::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed069::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed069::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed070::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed070::conflict | 0.550 | 0.600 | 5 |
| random_gate_budget_0.40_seed070::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed070::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed070::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed071::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed071::conflict | 0.650 | 0.450 | 5 |
| random_gate_budget_0.40_seed071::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed071::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed071::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed072::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed072::conflict | 0.600 | 0.450 | 5 |
| random_gate_budget_0.40_seed072::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed072::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed072::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed073::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed073::conflict | 0.700 | 0.550 | 3 |
| random_gate_budget_0.40_seed073::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed073::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed073::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed074::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed074::conflict | 0.550 | 0.450 | 6 |
| random_gate_budget_0.40_seed074::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed074::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.40_seed074::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed075::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed075::conflict | 0.600 | 0.500 | 5 |
| random_gate_budget_0.40_seed075::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed075::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed075::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed076::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed076::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed076::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed076::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed076::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed077::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed077::conflict | 0.750 | 0.500 | 3 |
| random_gate_budget_0.40_seed077::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed077::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.40_seed077::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed078::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed078::conflict | 0.650 | 0.550 | 3 |
| random_gate_budget_0.40_seed078::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed078::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed078::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed079::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed079::conflict | 0.650 | 0.350 | 5 |
| random_gate_budget_0.40_seed079::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed079::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed079::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed080::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed080::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.40_seed080::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed080::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed080::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed081::boundary_sensitive | 0.600 | 0.550 | 7 |
| random_gate_budget_0.40_seed081::conflict | 0.550 | 0.500 | 6 |
| random_gate_budget_0.40_seed081::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed081::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed081::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed082::boundary_sensitive | 0.650 | 0.650 | 5 |
| random_gate_budget_0.40_seed082::conflict | 0.750 | 0.500 | 3 |
| random_gate_budget_0.40_seed082::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed082::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed082::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed083::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed083::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed083::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed083::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.40_seed083::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed084::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed084::conflict | 0.700 | 0.650 | 2 |
| random_gate_budget_0.40_seed084::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed084::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed084::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed085::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed085::conflict | 0.750 | 0.500 | 3 |
| random_gate_budget_0.40_seed085::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed085::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed085::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed086::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed086::conflict | 0.700 | 0.550 | 3 |
| random_gate_budget_0.40_seed086::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed086::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed086::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed087::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed087::conflict | 0.750 | 0.450 | 4 |
| random_gate_budget_0.40_seed087::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed087::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.40_seed087::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed088::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed088::conflict | 0.700 | 0.550 | 3 |
| random_gate_budget_0.40_seed088::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed088::multi_hop | 0.750 | 0.800 | 4 |
| random_gate_budget_0.40_seed088::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed089::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed089::conflict | 0.750 | 0.450 | 3 |
| random_gate_budget_0.40_seed089::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed089::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed089::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed090::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed090::conflict | 0.650 | 0.400 | 5 |
| random_gate_budget_0.40_seed090::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed090::multi_hop | 0.850 | 0.800 | 3 |
| random_gate_budget_0.40_seed090::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed091::boundary_sensitive | 0.650 | 0.600 | 6 |
| random_gate_budget_0.40_seed091::conflict | 0.650 | 0.450 | 5 |
| random_gate_budget_0.40_seed091::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed091::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.40_seed091::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed092::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed092::conflict | 0.700 | 0.500 | 3 |
| random_gate_budget_0.40_seed092::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed092::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed092::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed093::boundary_sensitive | 0.700 | 0.700 | 4 |
| random_gate_budget_0.40_seed093::conflict | 0.650 | 0.450 | 4 |
| random_gate_budget_0.40_seed093::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed093::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed093::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed094::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed094::conflict | 0.550 | 0.400 | 6 |
| random_gate_budget_0.40_seed094::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed094::multi_hop | 0.750 | 0.700 | 5 |
| random_gate_budget_0.40_seed094::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed095::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed095::conflict | 0.800 | 0.500 | 2 |
| random_gate_budget_0.40_seed095::distractor_heavy | 0.900 | 0.900 | 2 |
| random_gate_budget_0.40_seed095::multi_hop | 0.700 | 0.750 | 5 |
| random_gate_budget_0.40_seed095::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed096::boundary_sensitive | 0.750 | 0.700 | 4 |
| random_gate_budget_0.40_seed096::conflict | 0.600 | 0.500 | 4 |
| random_gate_budget_0.40_seed096::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed096::multi_hop | 0.700 | 0.650 | 6 |
| random_gate_budget_0.40_seed096::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed097::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed097::conflict | 0.600 | 0.500 | 4 |
| random_gate_budget_0.40_seed097::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed097::multi_hop | 0.800 | 0.850 | 3 |
| random_gate_budget_0.40_seed097::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed098::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed098::conflict | 0.700 | 0.350 | 5 |
| random_gate_budget_0.40_seed098::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed098::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed098::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed099::boundary_sensitive | 0.700 | 0.650 | 5 |
| random_gate_budget_0.40_seed099::conflict | 0.700 | 0.450 | 4 |
| random_gate_budget_0.40_seed099::distractor_heavy | 0.950 | 0.950 | 1 |
| random_gate_budget_0.40_seed099::multi_hop | 0.800 | 0.750 | 4 |
| random_gate_budget_0.40_seed099::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::boundary_sensitive | 0.750 | 0.700 | 4 |
| risk_guided_doc_patch_k2::conflict | 0.800 | 0.500 | 2 |
| risk_guided_doc_patch_k2::distractor_heavy | 0.950 | 0.950 | 1 |
| risk_guided_doc_patch_k2::multi_hop | 0.800 | 0.750 | 4 |
| risk_guided_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.10::boundary_sensitive | 0.550 | 0.550 | 7 |
| safe_gate_budget_0.10::conflict | 0.250 | 0.450 | 10 |
| safe_gate_budget_0.10::distractor_heavy | 0.900 | 0.900 | 2 |
| safe_gate_budget_0.10::multi_hop | 0.700 | 0.750 | 5 |
| safe_gate_budget_0.10::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.25::boundary_sensitive | 0.550 | 0.550 | 7 |
| safe_gate_budget_0.25::conflict | 0.750 | 0.450 | 3 |
| safe_gate_budget_0.25::distractor_heavy | 0.900 | 0.900 | 2 |
| safe_gate_budget_0.25::multi_hop | 0.700 | 0.750 | 5 |
| safe_gate_budget_0.25::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.40::boundary_sensitive | 0.700 | 0.700 | 4 |
| safe_gate_budget_0.40::conflict | 0.800 | 0.500 | 2 |
| safe_gate_budget_0.40::distractor_heavy | 0.950 | 0.950 | 1 |
| safe_gate_budget_0.40::multi_hop | 0.850 | 0.800 | 3 |
| safe_gate_budget_0.40::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| conflict_0000_noisy | conflict | 4.01709 | `According to the official schedule, the Qorlan observatory opens at 8` | `8 AM` | `8 AM` |
| conflict_0018_noisy | conflict | 3.43592 | `According to the official schedule, the Mariton observatory opens at 10` | `1 PM` | `10 AM` |
| multihop_0015_noisy | multi_hop | 2.9812 | `Aster Port` | `The garden survey tracked rainfall near the western greenhouse.` | `Aster Port` |
| conflict_0003_noisy | conflict | 2.87821 | `According to the official schedule, the Kelminster observatory opens at 11` | `11 AM` | `11 AM` |
| conflict_0011_noisy | conflict | 2.74329 | `The Brevic observatory opens at 11 AM.` | `11 AM` | `11 AM` |
| multihop_0018_noisy | multi_hop | 2.70412 | `Ilya Marr` | `The designer of Project Nimbar was born in the northern records room.` | `Velora` |
| conflict_0017_noisy | conflict | 2.6876 | `The official schedule states: "The Velora observatory opens at 9 AM` | `12 AM` | `9 AM` |
| multihop_0009_noisy | multi_hop | 2.25959 | `Mariton` | `Northern records room` | `Mariton` |
| conflict_0009_noisy | conflict | 2.0267 | `According to the official schedule, the Halden observatory opens at 9` | `10 AM` | `9 AM` |
| multihop_0001_noisy | multi_hop | 1.6142 | `Qorlan` | `Tovan Reed` | `Qorlan` |

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
