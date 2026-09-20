# SAFE-KV Cost Accounting

These are recomputation-budget proxies, not measured serving latency.
`estimated_recompute_ratio = patched_token_ratio`; `estimated_prefill_saving = 1 - patched_token_ratio`.

| model | dataset | method | ans_eq | changed_wrong | patch_ratio | est_saving |
|---|---|---|---:|---:|---:|---:|
| qwen05 | diagnostic_clean | entity_overlap_doc_patch_k2 | 0.970 | 0.010 | 0.543 | 0.457 |
| qwen05 | diagnostic_clean | full_prefill | 1.000 | 0.000 | 0.000 | 1.000 |
| qwen05 | diagnostic_clean | oracle_evidence_doc_patch | 0.970 | 0.010 | 0.457 | 0.543 |
| qwen05 | diagnostic_clean | prefix_conditioned_naive_global | 0.850 | 0.140 | 0.000 | 1.000 |
| qwen05 | diagnostic_clean | query_similarity_doc_patch_k2 | 0.970 | 0.010 | 0.544 | 0.456 |
| qwen05 | diagnostic_clean | random_doc_patch_k2_seeded | 0.960 | 0.030 | 0.528 | 0.472 |
| qwen05 | diagnostic_clean | safe_gate_t0.60 | 0.920 | 0.070 | 0.110 | 0.890 |
| qwen05 | diagnostic_noisy | entity_overlap_doc_patch_k2 | 0.900 | 0.070 | 0.548 | 0.452 |
| qwen05 | diagnostic_noisy | full_prefill | 1.000 | 0.000 | 0.000 | 1.000 |
| qwen05 | diagnostic_noisy | oracle_evidence_doc_patch | 0.900 | 0.060 | 0.423 | 0.577 |
| qwen05 | diagnostic_noisy | prefix_conditioned_naive_global | 0.690 | 0.230 | 0.000 | 1.000 |
| qwen05 | diagnostic_noisy | query_similarity_doc_patch_k2 | 0.890 | 0.070 | 0.550 | 0.450 |
| qwen05 | diagnostic_noisy | random_doc_patch_k2_seeded | 0.830 | 0.110 | 0.536 | 0.464 |
| qwen05 | diagnostic_noisy | safe_gate_t0.60 | 0.810 | 0.140 | 0.282 | 0.718 |
| qwen15 | diagnostic_clean | entity_overlap_doc_patch_k2 | 0.960 | 0.030 | 0.543 | 0.457 |
| qwen15 | diagnostic_clean | full_prefill | 1.000 | 0.000 | 0.000 | 1.000 |
| qwen15 | diagnostic_clean | oracle_evidence_doc_patch | 0.960 | 0.030 | 0.457 | 0.543 |
| qwen15 | diagnostic_clean | prefix_conditioned_naive_global | 0.880 | 0.110 | 0.000 | 1.000 |
| qwen15 | diagnostic_clean | query_similarity_doc_patch_k2 | 0.960 | 0.030 | 0.544 | 0.456 |
| qwen15 | diagnostic_clean | random_doc_patch_k2_seeded | 0.930 | 0.060 | 0.528 | 0.472 |
| qwen15 | diagnostic_clean | safe_gate_t0.60 | 0.920 | 0.060 | 0.110 | 0.890 |
| qwen15 | diagnostic_noisy | entity_overlap_doc_patch_k2 | 0.920 | 0.060 | 0.548 | 0.452 |
| qwen15 | diagnostic_noisy | full_prefill | 1.000 | 0.000 | 0.000 | 1.000 |
| qwen15 | diagnostic_noisy | oracle_evidence_doc_patch | 0.890 | 0.100 | 0.423 | 0.577 |
| qwen15 | diagnostic_noisy | prefix_conditioned_naive_global | 0.740 | 0.200 | 0.000 | 1.000 |
| qwen15 | diagnostic_noisy | query_similarity_doc_patch_k2 | 0.920 | 0.060 | 0.550 | 0.450 |
| qwen15 | diagnostic_noisy | random_doc_patch_k2_seeded | 0.860 | 0.080 | 0.536 | 0.464 |
| qwen15 | diagnostic_noisy | safe_gate_t0.60 | 0.840 | 0.130 | 0.282 | 0.718 |
| qwen05 | external_multihop | entity_overlap_doc_patch_k2 | 0.500 | 0.430 | 0.415 | 0.585 |
| qwen05 | external_multihop | full_prefill | 1.000 | 0.000 | 0.000 | 1.000 |
| qwen05 | external_multihop | oracle_evidence_doc_patch | 0.470 | 0.470 | 0.416 | 0.584 |
| qwen05 | external_multihop | prefix_conditioned_naive_global | 0.410 | 0.490 | 0.000 | 1.000 |
| qwen05 | external_multihop | query_similarity_doc_patch_k2 | 0.500 | 0.430 | 0.447 | 0.553 |
| qwen05 | external_multihop | random_doc_patch_k2_seeded | 0.550 | 0.390 | 0.387 | 0.613 |
| qwen05 | external_multihop | safe_gate_t0.60 | 0.480 | 0.450 | 0.425 | 0.575 |
| qwen15 | external_multihop | entity_overlap_doc_patch_k2 | 0.620 | 0.330 | 0.415 | 0.585 |
| qwen15 | external_multihop | full_prefill | 1.000 | 0.000 | 0.000 | 1.000 |
| qwen15 | external_multihop | oracle_evidence_doc_patch | 0.640 | 0.310 | 0.416 | 0.584 |
| qwen15 | external_multihop | prefix_conditioned_naive_global | 0.440 | 0.480 | 0.000 | 1.000 |
| qwen15 | external_multihop | query_similarity_doc_patch_k2 | 0.620 | 0.320 | 0.447 | 0.553 |
| qwen15 | external_multihop | random_doc_patch_k2_seeded | 0.640 | 0.310 | 0.387 | 0.613 |
| qwen15 | external_multihop | safe_gate_t0.60 | 0.630 | 0.320 | 0.425 | 0.575 |
| smollm17 | diagnostic_noisy | entity_overlap_doc_patch_k2 | 0.940 | 0.050 | 0.549 | 0.451 |
| smollm17 | diagnostic_noisy | full_prefill | 1.000 | 0.000 | 0.000 | 1.000 |
| smollm17 | diagnostic_noisy | oracle_evidence_doc_patch | 0.890 | 0.070 | 0.425 | 0.575 |
| smollm17 | diagnostic_noisy | prefix_conditioned_naive_global | 0.680 | 0.240 | 0.000 | 1.000 |
| smollm17 | diagnostic_noisy | query_similarity_doc_patch_k2 | 0.920 | 0.070 | 0.551 | 0.449 |
| smollm17 | diagnostic_noisy | random_doc_patch_k2_seeded | 0.840 | 0.120 | 0.540 | 0.460 |
| smollm17 | diagnostic_noisy | safe_gate_t0.60 | 0.810 | 0.150 | 0.283 | 0.717 |
| smollm17 | external_multihop | entity_overlap_doc_patch_k2 | 0.550 | 0.420 | 0.416 | 0.584 |
| smollm17 | external_multihop | full_prefill | 1.000 | 0.000 | 0.000 | 1.000 |
| smollm17 | external_multihop | oracle_evidence_doc_patch | 0.570 | 0.400 | 0.416 | 0.584 |
| smollm17 | external_multihop | prefix_conditioned_naive_global | 0.520 | 0.440 | 0.000 | 1.000 |
| smollm17 | external_multihop | query_similarity_doc_patch_k2 | 0.580 | 0.390 | 0.447 | 0.553 |
| smollm17 | external_multihop | random_doc_patch_k2_seeded | 0.600 | 0.340 | 0.387 | 0.613 |
| smollm17 | external_multihop | safe_gate_t0.60 | 0.560 | 0.420 | 0.424 | 0.576 |
