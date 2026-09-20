# Reproduction Instructions

These commands reproduce the SAFE-KV artifact from the packaged supplement. Commands assume the current directory is `supplement_reproducibility/` unless stated otherwise.

The original GPU experiments were run on an NVIDIA L40S-class GPU with PyTorch `2.4.1+cu124` and Transformers `4.57.6`. Re-running answer-level experiments requires GPU memory sufficient for the listed models.

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r code/requirements.txt
```

The source package is under `code/`, so use `PYTHONPATH=code` when running scripts from this supplement root.

## Unit Tests

```bash
cd code
python -m pytest -q
cd ..
```

## Data Generation

The processed JSONL files used in the paper are already included under `data/`. To regenerate them:

```bash
PYTHONPATH=code python code/scripts/build_diagnostic_data.py \
  --n-per-category 20 \
  --seed 13 \
  --out data/diagnostic_100.jsonl

PYTHONPATH=code python code/scripts/build_diagnostic_data.py \
  --n-per-category 20 \
  --seed 13 \
  --variant noisy_retrieval \
  --out data/diagnostic_100_noisy.jsonl

PYTHONPATH=code python code/scripts/build_external_data.py \
  --dataset hotpotqa \
  --n 50 \
  --seed 13 \
  --out data/external_hotpotqa_50.jsonl

PYTHONPATH=code python code/scripts/build_external_data.py \
  --dataset 2wiki \
  --n 50 \
  --seed 13 \
  --out data/external_2wiki_50.jsonl

cat data/external_hotpotqa_50.jsonl data/external_2wiki_50.jsonl > data/external_multihop_100.jsonl
```

The external builders use public Hugging Face datasets where available. The processed files in this supplement are the exact examples used for the reported paper runs.

## Core Answer-Level Runs

```bash
PYTHONPATH=code python code/scripts/run_answer_eval.py \
  --config configs/v0_qwen05_100.yaml \
  --results-dir results_qwen05_100_answer \
  --resume

PYTHONPATH=code python code/scripts/run_answer_eval.py \
  --config configs/v0_qwen05_100_noisy.yaml \
  --results-dir results_qwen05_100_noisy_answer \
  --resume

PYTHONPATH=code python code/scripts/run_answer_eval.py \
  --config configs/v0_qwen15_100.yaml \
  --results-dir results_qwen15_100_answer \
  --resume

PYTHONPATH=code python code/scripts/run_answer_eval.py \
  --config configs/v0_qwen15_100_noisy.yaml \
  --results-dir results_qwen15_100_noisy_answer \
  --resume
```

## External Sanity Runs

```bash
PYTHONPATH=code python code/scripts/run_answer_eval.py \
  --config configs/v0_qwen05_external.yaml \
  --results-dir results_qwen05_external_answer \
  --resume

PYTHONPATH=code python code/scripts/run_answer_eval.py \
  --config configs/v0_qwen15_external.yaml \
  --results-dir results_qwen15_external_answer \
  --resume
```

## Cross-Family SmolLM2 Runs

```bash
PYTHONPATH=code python code/scripts/run_answer_eval.py \
  --config configs/v0_smollm17_noisy.yaml \
  --results-dir results_smollm17_noisy_answer \
  --resume

PYTHONPATH=code python code/scripts/run_answer_eval.py \
  --config configs/v0_smollm17_external.yaml \
  --results-dir results_smollm17_external_answer \
  --resume
```

## Budgeted Gate and Held-Out Calibration

```bash
PYTHONPATH=code python code/scripts/run_budget_gate_eval.py \
  --config configs/v0_qwen05_100_noisy.yaml \
  --results-dir results_budget_gate/qwen05_noisy \
  --target-budgets 0.10,0.25,0.40 \
  --num-random-seeds 100

PYTHONPATH=code python code/scripts/run_budget_gate_eval.py \
  --config configs/v0_qwen05_external.yaml \
  --results-dir results_budget_gate/qwen05_external \
  --target-budgets 0.10,0.25,0.40 \
  --num-random-seeds 100

PYTHONPATH=code python code/scripts/run_heldout_gate_calibration.py \
  --out-dir results_paper
```

See the included `configs/` directory for the complete set of model/data configs used in the paper.

## Paper Table Generation

The summarized paper tables are included under `results/paper_tables/results_paper/`. To regenerate them from local result directories:

```bash
PYTHONPATH=code python code/scripts/make_paper_tables.py --out-dir results_paper
PYTHONPATH=code python code/scripts/make_cost_accounting_tables.py --out-dir results_paper
```

If regenerated into the supplement root, copy the resulting `results_paper/` files into `results/paper_tables/results_paper/` for the same layout used here.

## Notes on Runtime

Unit tests are CPU-only and should not download models. Full answer-level reproduction downloads public model weights and can take substantial GPU time. The supplement includes summary metrics so reviewers can inspect reported results without rerunning every GPU experiment.
