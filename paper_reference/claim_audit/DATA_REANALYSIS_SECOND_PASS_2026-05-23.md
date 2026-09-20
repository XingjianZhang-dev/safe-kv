# SAFE-KV Data Reanalysis, Second Pass (2026-05-23)

This pass re-read the raw experiment outputs under `results/` rather than relying only on the paper tables. The repository currently contains 219 result files across 7B external runs, synthetic noise sweeps, position sweeps, selector diagnostics, latency runs, and method-development ablations.

## Core Evidence Reconfirmed

- **External 7B drift is large.** Prefix-conditioned composition preserves only 47.2% of Qwen2.5-7B HotpotQA-500 full-prefill answers and 37.8% of 2Wiki-500 answers.
- **SAFE-KV recovers behavior.** Risk suffix K2 reaches 99.8% answer equivalence on HotpotQA-500 and 98.4% on 2Wiki-500, leaving 1 and 6 changed-and-gold-wrong answers.
- **The answer-bearing document is not enough.** In Noise16-250, oracle evidence-document patching reaches only 54.4% equivalence, while oracle suffix closure reaches 93.6%.
- **Fixed local windows are not enough.** On 2Wiki-100, risk downstream w4 reaches 79.0% equivalence at 72.9% patch ratio; risk suffix K1 reaches 97.0% at 79.3%.
- **Position explains the mechanism.** In the high-noise position sweep, evidence-first examples stay at 42.0% under document patching, matching unsafe prefix composition, while oracle/query suffix repair reaches 98.0% overall.
- **Random suffix is a hard baseline, not a strawman.** Random K2 reaches 91.8% on HotpotQA and 83.4% on 2Wiki, but selected risk K2 still improves to 99.8% and 98.4%.

## Additional Ablations That Shaped the Paper

- **Linked intervals:** Noise16 oracle linked intervals reach 80.0%, below oracle suffix closure at 93.6%. This supports the claim that human-plausible local reasoning chains do not necessarily form causally closed cache repair units.
- **Adaptive suffix:** Noise16 risk adaptive suffix reaches 86.8% at 57.9% patch ratio, compared with risk suffix K2 at 88.8% and 69.9%. This is a useful quality--budget point but not the high-fidelity setting.
- **Cost-aware suffix:** On 2Wiki-100, risk cost-aware suffix reaches 96.0% at about 79% patch ratio, close to risk K1 at 97.0%. This supports the quality--budget framing.
- **Learned selector:** Synthetic-trained learned selection improves some synthetic suffix results but fails to transfer to external selector evidence labels. The final paper should keep the selector story modest.
- **All-document sanity:** All-document patching reaches 100.0% equivalence on noisy sanity examples at 89.9% patch ratio, validating the patch operator but not serving as a practical algorithm.
- **Latency:** Short 2Wiki prompts remain overhead-sensitive, while longer noise64 prompts show risk K1 at 0.140s versus full prefill at 0.215s. The claim should remain prototype TTFT feasibility, not production throughput.

## Writing Decision

The second pass strengthens the current story: SAFE-KV should be presented as a semantic causal-state contract for non-prefix RAG KV reuse. The final method is not a clever document selector; it is suffix repair from an estimated causal frontier. Selectors determine budget and risk, while causal suffix closure is the stable mechanism across external datasets, synthetic stress tests, position sweeps, and cross-model checks.
