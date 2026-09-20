#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-quick}"

clean_python_caches() {
  find . -type d -name __pycache__ -prune -exec rm -rf {} +
  find . -type d -name .pytest_cache -prune -exec rm -rf {} +
  find . -type f -name '*.pyc' -delete
}

case "$MODE" in
  quick)
    cd code
    python -m pytest -q
    cd ..
    clean_python_caches
    python scripts/verify_packaged_results.py
    ;;
  tables)
    mkdir -p reproduction_runs/results_paper
    python scripts/rebuild_headline_tables.py
    clean_python_caches
    python scripts/verify_packaged_results.py
    ;;
  commands)
    python scripts/emit_reproduction_commands.py
    ;;
  gpu-core)
    mkdir -p reproduction_runs/recomputed
    PYTHONPATH=code python code/scripts/run_answer_eval.py \
      --config configs/acl_qwen25_7b_hotpotqa_500.yaml \
      --data-path data/external_hotpotqa_500.jsonl \
      --max-examples 500 \
      --methods full_prefill,prefix_conditioned_naive_global,query_similarity_suffix_closure_k1,query_similarity_suffix_closure_k2,risk_guided_suffix_closure_k1,risk_guided_suffix_closure_k2,hybrid_query_risk_union_suffix_k1,random_suffix_closure_k2_seeded \
      --results-dir reproduction_runs/recomputed/acl_qwen25_7b_hotpotqa_suffix_main_500 \
      --resume
    PYTHONPATH=code python code/scripts/run_answer_eval.py \
      --config configs/acl_qwen25_7b_2wiki_500.yaml \
      --data-path data/external_2wiki_500.jsonl \
      --max-examples 500 \
      --methods full_prefill,prefix_conditioned_naive_global,query_similarity_suffix_closure_k1,query_similarity_suffix_closure_k2,risk_guided_suffix_closure_k1,risk_guided_suffix_closure_k2,hybrid_query_risk_union_suffix_k1,random_suffix_closure_k2_seeded \
      --results-dir reproduction_runs/recomputed/acl_qwen25_7b_2wiki_suffix_main_500 \
      --resume
    ;;
  gpu-all-answer)
    python scripts/emit_reproduction_commands.py --kind answer --execute
    ;;
  gpu-latency)
    python scripts/emit_reproduction_commands.py --kind latency --execute
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    echo "Available modes: quick, tables, commands, gpu-core, gpu-all-answer, gpu-latency" >&2
    exit 2
    ;;
esac
