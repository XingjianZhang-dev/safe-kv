#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 OUTPUT_PROTOCOL_JSON" >&2
  exit 2
fi

BASE=/root/autodl-tmp/safekv_ipm_journal
OUT=$1

evidence=(
  --baseline-evidence "$BASE/baseline_provenance.json"
  --baseline-evidence "$BASE/run_registry/baseline_final_repository_recheck_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/baseline_final_repository_recheck_20260822_v1/stdout.log"
  --baseline-evidence "$BASE/baseline_patches/flashinfer_py311_annotations.patch"
  --baseline-evidence "$BASE/run_registry/lmcache_v054_isolated_environment_install_20260821_v2/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/lmcache_v054_official_blend_unmodified_local_mistral_20260821_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/lmcache_v054_official_blend_unmodified_local_mistral_20260821_v1/stderr.log"
  --baseline-evidence "$BASE/run_registry/lmcache_v054_vllm027_registration_compat_qwen_smoke_20260821_v3/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/lmcache_v054_vllm027_registration_compat_qwen_smoke_20260821_v3/stderr.log"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_env_create_20260821_v2/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_unmodified_install_20260821_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_unmodified_install_20260821_v1/stderr.log"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_unmodified_install_cuda_path_20260821_v2/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_unmodified_install_cuda_path_20260821_v2/stderr.log"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_unmodified_install_prefetched_cutlass_20260821_v3/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_unmodified_install_prefetched_cutlass_20260821_v3/stderr.log"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_blackwell_compat_sm90_ptx_20260821_v4/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_blackwell_compat_sm90_ptx_20260821_v4/stderr.log"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_blackwell_full_source_build_20260821_v7/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_blackwell_full_source_build_20260821_v7/stderr.log"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_blackwell_noneditable_install_j8_20260822_v9/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_blackwell_noneditable_install_j8_20260822_v9/stderr.log"
  --baseline-evidence "$BASE/run_registry/epic_official_vllm070_blackwell_noneditable_install_j8_20260822_v9/stdout.log"
  --baseline-evidence "$BASE/baselines/dependencies/cutlass-v3.6.0-20260821.tar.gz"
  --baseline-evidence "$BASE/baselines/dependencies/vllm-flash-attention-d4e09037abf588af1ec47d0e966b237ee376876c-20260821.tar.gz"
  --baseline-evidence "$BASE/baselines/dependencies/vllm-flash-attention-d4e09037-with-cutlass-c506e167-20260821.tar.gz"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_paper_artifact_clone_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_requirements_install_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_import_blackwell_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_qwen3_hotpotqa_n1_smoke_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_qwen3_hotpotqa_n1_smoke_20260822_v1/stderr.log"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_qwen3_hotpotqa_n1_smoke_20260822_v2/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_qwen3_hotpotqa_n100_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_fullrecompute_qwen3_hotpotqa_n100_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_qwen3_musique_n100_20260822_v2/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_fullrecompute_qwen3_musique_n100_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_postrun_audit_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_postrun_audit_20260822_v1/stdout.log"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_dataset_snapshots_20260822_v2/run_manifest.json"
  --baseline-evidence "$BASE/baseline_data_snapshots/kvpacket_native_validation_20260822.json"
  --baseline-evidence "$BASE/run_registry/kvpacket_official_reproduction_summary_20260822_v1/run_manifest.json"
  --baseline-evidence "$BASE/baseline_results/kvpacket_official_native_reproduction_20260822.json"
  --baseline-evidence "$BASE/baseline_configs/eval_results/kvpacket_qwen3_hotpotqa_n100_result.json"
  --baseline-evidence "$BASE/baseline_configs/eval_results/full_recompute_qwen3_hotpotqa_n100_result.json"
  --baseline-evidence "$BASE/baseline_configs/eval_results/kvpacket_qwen3_musique_n100_result.json"
  --baseline-evidence "$BASE/baseline_configs/eval_results/full_recompute_qwen3_musique_n100_result.json"
)

/root/miniconda3/envs/safekv/bin/python "$BASE/code/scripts/freeze_ipm_test_protocol.py" \
  --data-root "$BASE/datasets/ipm_v1" \
  --data-build-manifest "$BASE/datasets/ipm_v1/hotpotqa_build_manifest.json" \
  --data-build-manifest "$BASE/datasets/ipm_v1/2wiki_build_manifest.json" \
  --data-build-manifest "$BASE/datasets/ipm_v1/musique_build_manifest.json" \
  --retriever-model-manifest "$BASE/model_manifests/bge_base_en_v15_a5beb1e.json" \
  --retriever-verification-report "$BASE/run_registry/bge_model_snapshot_verify_prefreeze_20260821_v1/model_snapshot_verification.json" \
  --config "$BASE/code/configs/ipm_qwen25_7b_main.yaml" \
  --model-manifest "$BASE/model_manifests/qwen25_7b_instruct_a09a354.json" \
  --model-verification-report "$BASE/run_registry/qwen25_model_snapshot_verify_prefreeze_20260821_v1/model_snapshot_verification.json" \
  --model-verification-report "$BASE/run_registry/mistral_model_snapshot_verify_prefreeze_20260821_v1/model_snapshot_verification.json" \
  --model-verification-report "$BASE/run_registry/yi15_model_snapshot_verify_prefreeze_20260821_v1/model_snapshot_verification.json" \
  --model-verification-report "$BASE/model_verification/qwen3_4b_instruct_2507_prefreeze.json" \
  --frontier-artifact "$BASE/run_registry/qwen25_frontier_selector_calibration_c10_20260821_v1/frontier_selector.json" \
  --frontier-selection-report "$BASE/run_registry/qwen25_frontier_selector_selection_20260821_v1/frontier_selector_selection.json" \
  --safety-gate-artifact "$BASE/run_registry/qwen25_safety_gate_calibration_20260821_v1/frozen_safety_gate.json" \
  --baseline-audit "$BASE/BASELINE_AVAILABILITY_AUDIT.md" \
  "${evidence[@]}" \
  --code-root "$BASE/code" \
  --registry-dir "$BASE/run_registry" \
  --transfer-model mistral "$BASE/code/configs/ipm_mistral_7b_main.yaml" "$BASE/model_manifests/mistral_7b_instruct_v03_c170c70.json" \
  --transfer-model yi15 "$BASE/code/configs/ipm_yi15_9b_16k_main.yaml" "$BASE/model_manifests/yi15_9b_chat_16k_2f8753b.json" \
  --transfer-model qwen3 "$BASE/code/configs/ipm_qwen3_4b_main.yaml" "$BASE/model_manifests/qwen3_4b_instruct_2507_cdbee75.json" \
  --out "$OUT"
