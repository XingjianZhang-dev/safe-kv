# SAFE-KV CPU Selector Audit

This is a selector-only audit. It does not establish language-model answer quality or end-to-end recomputation correctness.

## Quality under retrieval-score removal and order shuffling

| Dataset | Scenario | Method | Recall | Any hit | Exact set | Suffix ratio |
|---|---|---|---:|---:|---:|---:|
| 2wiki | order_shuffled | query_similarity_doc_patch_k2 | 0.537 | 0.910 | 0.215 | 0.878 |
| 2wiki | order_shuffled | risk_guided_doc_patch_k2 | 0.818 | 0.998 | 0.638 | 0.801 |
| 2wiki | original | query_similarity_doc_patch_k2 | 0.656 | 0.972 | 0.376 | 0.934 |
| 2wiki | original | risk_guided_doc_patch_k2 | 0.818 | 0.998 | 0.638 | 0.969 |
| 2wiki | retrieval_neutral | query_similarity_doc_patch_k2 | 0.656 | 0.972 | 0.376 | 0.934 |
| 2wiki | retrieval_neutral | risk_guided_doc_patch_k2 | 0.623 | 0.960 | 0.326 | 0.917 |
| 2wiki | retrieval_neutral_order_shuffled | query_similarity_doc_patch_k2 | 0.537 | 0.910 | 0.215 | 0.878 |
| 2wiki | retrieval_neutral_order_shuffled | risk_guided_doc_patch_k2 | 0.620 | 0.960 | 0.321 | 0.800 |
| hotpotqa | order_shuffled | query_similarity_doc_patch_k2 | 0.434 | 0.737 | 0.131 | 0.883 |
| hotpotqa | order_shuffled | risk_guided_doc_patch_k2 | 0.856 | 1.000 | 0.713 | 0.799 |
| hotpotqa | original | query_similarity_doc_patch_k2 | 0.544 | 0.848 | 0.240 | 0.886 |
| hotpotqa | original | risk_guided_doc_patch_k2 | 0.858 | 1.000 | 0.716 | 0.973 |
| hotpotqa | retrieval_neutral | query_similarity_doc_patch_k2 | 0.544 | 0.848 | 0.240 | 0.886 |
| hotpotqa | retrieval_neutral | risk_guided_doc_patch_k2 | 0.471 | 0.774 | 0.168 | 0.840 |
| hotpotqa | retrieval_neutral_order_shuffled | query_similarity_doc_patch_k2 | 0.434 | 0.737 | 0.131 | 0.883 |
| hotpotqa | retrieval_neutral_order_shuffled | risk_guided_doc_patch_k2 | 0.467 | 0.770 | 0.163 | 0.799 |

## Local CPU latency

CPU: Apple M4 Pro

| Workload | Method | Calls | Median ms | P95 ms | P99 ms |
|---|---|---:|---:|---:|---:|
| external_hotpotqa | query_similarity_doc_patch_k1 | 5000 | 0.266 | 0.746 | 2.580 |
| external_hotpotqa | query_similarity_doc_patch_k2 | 5000 | 0.206 | 0.357 | 0.497 |
| external_hotpotqa | risk_guided_doc_patch_k1 | 5000 | 1.594 | 2.629 | 3.359 |
| external_hotpotqa | risk_guided_doc_patch_k2 | 5000 | 1.510 | 2.256 | 2.757 |
| external_2wiki | query_similarity_doc_patch_k1 | 5000 | 0.157 | 0.296 | 0.348 |
| external_2wiki | query_similarity_doc_patch_k2 | 5000 | 0.156 | 0.300 | 0.349 |
| external_2wiki | risk_guided_doc_patch_k1 | 5000 | 1.306 | 2.456 | 2.890 |
| external_2wiki | risk_guided_doc_patch_k2 | 5000 | 1.295 | 2.446 | 2.873 |
| synthetic_docs3 | query_similarity_doc_patch_k1 | 2000 | 0.052 | 0.063 | 0.079 |
| synthetic_docs3 | query_similarity_doc_patch_k2 | 2000 | 0.053 | 0.065 | 0.091 |
| synthetic_docs3 | risk_guided_doc_patch_k1 | 2000 | 0.390 | 0.445 | 0.517 |
| synthetic_docs3 | risk_guided_doc_patch_k2 | 2000 | 0.391 | 0.463 | 0.576 |
| synthetic_docs7 | query_similarity_doc_patch_k1 | 2000 | 0.086 | 0.098 | 0.116 |
| synthetic_docs7 | query_similarity_doc_patch_k2 | 2000 | 0.086 | 0.094 | 0.115 |
| synthetic_docs7 | risk_guided_doc_patch_k1 | 2000 | 0.656 | 0.748 | 0.822 |
| synthetic_docs7 | risk_guided_doc_patch_k2 | 2000 | 0.666 | 0.799 | 0.899 |
| synthetic_docs19 | query_similarity_doc_patch_k1 | 2000 | 0.192 | 0.220 | 0.285 |
| synthetic_docs19 | query_similarity_doc_patch_k2 | 2000 | 0.191 | 0.216 | 0.267 |
| synthetic_docs19 | risk_guided_doc_patch_k1 | 2000 | 1.454 | 1.640 | 1.759 |
| synthetic_docs19 | risk_guided_doc_patch_k2 | 2000 | 1.454 | 1.626 | 1.773 |
| synthetic_docs67 | query_similarity_doc_patch_k1 | 400 | 0.605 | 0.706 | 0.812 |
| synthetic_docs67 | query_similarity_doc_patch_k2 | 400 | 0.609 | 0.758 | 1.048 |
| synthetic_docs67 | risk_guided_doc_patch_k1 | 400 | 4.623 | 5.044 | 5.262 |
| synthetic_docs67 | risk_guided_doc_patch_k2 | 400 | 4.573 | 4.763 | 4.905 |

## Interpretation guardrail

These results can support a narrow claim about selector cost and label-free document identification. They cannot support the paper's answer-equivalence or production-latency claims without the GPU recomputation experiment.
