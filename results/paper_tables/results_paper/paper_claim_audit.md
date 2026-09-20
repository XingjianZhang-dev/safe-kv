# SAFE-KV Claim Audit

## Strongly Supported

- Non-prefix KV composition can cause answer-level drift.
- Prefix-conditioned composition is much stronger than doc-only composition.
- Residual drift is structured and harder under conflict/multi-hop/noisy retrieval.
- Span-level patching is unreliable.
- Document-level repair is a more coherent repair unit.
- First-token KL is correlated with answer-level mismatch.
- Cross-family SmolLM2 sanity shows answer drift is not Qwen-family-only.
- External HotpotQA/2Wiki sanity confirms answer drift is not synthetic-only.

## Supported With Caveat

- Semantic document selectors help under controlled noisy diagnostic.
- External natural data shows drift and partial repair, but selectors do not consistently beat random.
- Safe gating gives quality-budget trade-offs, but fixed thresholds are not portable.
- Budget-targeted gating is more defensible than fixed thresholds, but must be compared to matched random gates.
- Held-out gate calibration helps avoid post-hoc threshold selection, but only beats matched random reliably on controlled noisy/clean diagnostic settings at moderate budgets.
- External natural data shows partial document-level repair, but random K2 remains a very competitive baseline.

## Not Supported / Do Not Claim

- Universal semantic selector dominance.
- System-level latency or throughput improvements.
- vLLM/LMCache replacement.
- Span-level recompute as the final method.
- SOTA QA performance.
- Universal gate superiority over matched random budgets.

## Future Work

- Better external retrieval calibration.
- More robust gate calibration.
- Real serving integration.
- Larger model and real latency evaluation.
- Better held-out calibration protocols for natural external retrieval settings.
