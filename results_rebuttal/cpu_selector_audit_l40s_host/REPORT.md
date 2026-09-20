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

CPU: x86_64

| Workload | Method | Calls | Median ms | P95 ms | P99 ms |
|---|---|---:|---:|---:|---:|
| external_hotpotqa | query_similarity_doc_patch_k1 | 10000 | 0.121 | 0.181 | 0.220 |
| external_hotpotqa | query_similarity_doc_patch_k2 | 10000 | 0.120 | 0.182 | 0.220 |
| external_hotpotqa | risk_guided_doc_patch_k1 | 10000 | 1.170 | 1.782 | 2.214 |
| external_hotpotqa | risk_guided_doc_patch_k2 | 10000 | 1.184 | 1.800 | 2.262 |
| external_2wiki | query_similarity_doc_patch_k1 | 10000 | 0.105 | 0.197 | 0.232 |
| external_2wiki | query_similarity_doc_patch_k2 | 10000 | 0.105 | 0.199 | 0.235 |
| external_2wiki | risk_guided_doc_patch_k1 | 10000 | 1.041 | 2.079 | 2.498 |
| external_2wiki | risk_guided_doc_patch_k2 | 10000 | 1.053 | 2.125 | 2.500 |
| synthetic_docs3 | query_similarity_doc_patch_k1 | 4000 | 0.037 | 0.045 | 0.052 |
| synthetic_docs3 | query_similarity_doc_patch_k2 | 4000 | 0.037 | 0.044 | 0.053 |
| synthetic_docs3 | risk_guided_doc_patch_k1 | 4000 | 0.297 | 0.327 | 0.406 |
| synthetic_docs3 | risk_guided_doc_patch_k2 | 4000 | 0.299 | 0.329 | 0.403 |
| synthetic_docs7 | query_similarity_doc_patch_k1 | 4000 | 0.063 | 0.071 | 0.087 |
| synthetic_docs7 | query_similarity_doc_patch_k2 | 4000 | 0.062 | 0.069 | 0.089 |
| synthetic_docs7 | risk_guided_doc_patch_k1 | 4000 | 0.499 | 0.540 | 0.675 |
| synthetic_docs7 | risk_guided_doc_patch_k2 | 4000 | 0.501 | 0.546 | 0.687 |
| synthetic_docs19 | query_similarity_doc_patch_k1 | 4000 | 0.138 | 0.153 | 0.198 |
| synthetic_docs19 | query_similarity_doc_patch_k2 | 4000 | 0.136 | 0.146 | 0.186 |
| synthetic_docs19 | risk_guided_doc_patch_k1 | 4000 | 1.112 | 1.455 | 1.626 |
| synthetic_docs19 | risk_guided_doc_patch_k2 | 4000 | 1.131 | 1.458 | 1.572 |
| synthetic_docs67 | query_similarity_doc_patch_k1 | 800 | 0.424 | 0.633 | 0.706 |
| synthetic_docs67 | query_similarity_doc_patch_k2 | 800 | 0.425 | 0.614 | 0.686 |
| synthetic_docs67 | risk_guided_doc_patch_k1 | 800 | 3.394 | 3.798 | 4.684 |
| synthetic_docs67 | risk_guided_doc_patch_k2 | 800 | 3.420 | 3.631 | 4.705 |

## Interpretation guardrail

These results can support a narrow claim about selector cost and label-free document identification. They cannot support the paper's answer-equivalence or production-latency claims without the GPU recomputation experiment.
