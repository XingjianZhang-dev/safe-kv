# Paper Result Summary

This directory consolidates SAFE-KV paper-facing tables from diagnostic, answer-level,
external, subset, and budget-gate analyses.

Use the claim audit as the boundary for ARR drafting: the strongest claims are semantic
safety analysis, structured answer drift, document-level repair, and calibrated
quality-budget trade-offs. External natural data should be framed as a sanity check.

## 7B Additions

- SmolLM2-1.7B cross-family sanity supports that answer drift and document repair are not Qwen-family-only.
- Held-out gate calibration shows moderate/high budget gates can help on controlled noisy diagnostic data, but external results remain mixed against matched random gates.
- Table 7 reports recomputation-budget proxies only: patched-token ratio, estimated recompute ratio, and estimated prefill-token saving. These are not production latency or throughput measurements.

## Drafting Boundary

The ARR paper should emphasize semantic safety analysis, prefix-conditioned composition,
document-level repair, and calibrated quality-budget trade-offs. It should avoid universal
selector/gate dominance claims and avoid system-level serving speedup claims.
