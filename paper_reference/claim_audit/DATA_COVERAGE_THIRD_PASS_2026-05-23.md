# Data Coverage Third Pass

This audit supports the third-pass paper rewrite requested on 2026-05-23.

## Result Inventory

- Paper-facing result files under `results/`: 219.
- Answer-level metric files: 35.
- Main external 7B evidence: HotpotQA-500 and 2Wiki-500 suffix-main runs, with bootstrap intervals, held-out calibration, and full-prefill-correct subset analyses.
- Mechanism evidence: 2Wiki downstream windows, Noise0/8/16 sweeps, Noise16 closure, Noise16 K sweeps, high-noise linked intervals, adaptive suffixes, and position sweeps.
- Cross-model evidence: Mistral-7B noisy suffix diagnostics and smoke checks.
- Efficiency evidence: 2Wiki latency suffix runs and noise64 latency suffix runs.
- Development/sanity evidence: small-model diagnostics, all-document patch sanity, learned-selector artifacts, and smoke runs.

## Paper Integration

- Main paper uses the 7B external runs, causal-closure/window diagnostics, position sweep, selector/budget operating points, and robustness/calibration checks.
- Appendix `Result Inventory and Restored Diagnostics` now maps every result family to its role: headline evidence, mechanism analysis, negative ablation, calibration, latency, or sanity/development support.
- Three compact tables that had been moved out of the main body are restored in the appendix: composition ablation, repair granularity, and small-model answer-level summary.

## Interpretation

The complete data suite supports a single coherent story. Unsafe prefix-conditioned non-prefix composition creates answer-level drift. Coherent suffix recomputation is already strong, which is why matched random suffix is a hard baseline. Selected SAFE-KV suffixes improve over that baseline by estimating the causal frontier. Document-only, fixed-window, linked-interval, adaptive, and learned-selector variants are retained because their failures define the boundary of the final method.
