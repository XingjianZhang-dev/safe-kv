#!/usr/bin/env python
"""Run SAFE-KV Milestone 6A answer-level behavior evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.answer_eval import (  # noqa: E402
    append_answer_rows,
    answer_failure_analysis_markdown,
    completed_output_keys,
    internal_selector_method,
    make_answer_eval_row,
    parse_methods_arg,
    read_answer_rows,
    summarize_answer_eval_rows,
    write_answer_metrics_csv,
)
from safekv.cache_ops import (  # noqa: E402
    cache_seq_len,
    clone_legacy_cache,
    legacy_cache_to_model_cache,
    slice_legacy_cache,
    to_legacy_cache,
)
from safekv.config import load_config  # noqa: E402
from safekv.data_schema import DiagnosticExample, PromptPack, TokenRange  # noqa: E402
from safekv.doc_selector import (  # noqa: E402
    document_ranges_for_ids,
    extract_entities,
    query_similarity_doc_scores,
    random_doc_ids_same_count,
    resolve_risk_weights,
    risk_guided_doc_scores,
    safe_composition_risk,
    selected_doc_ids_for_method,
)
from safekv.full_prefill import (  # noqa: E402
    greedy_generate_from_prefill,
    load_examples_for_config,
    select_examples_per_category,
    set_deterministic_seed,
)
from safekv.generation import trim_generated_answer  # noqa: E402
from safekv.learned_selector import (  # noqa: E402
    load_selector_artifact,
    select_learned_doc_ids,
)
from safekv.metrics import logit_preservation_metrics  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import (  # noqa: E402
    build_naive_composed_context_cache,
    build_prompt_pack_for_config,
)
from safekv.patch_granularity import build_ranges_for_methods  # noqa: E402
from safekv.patch_recompute import (  # noqa: E402
    oracle_evidence_doc_patch_ranges,
    replace_cache_slices,
    stable_example_seed,
    token_count,
    validate_patch_ranges_within_documents,
)
from safekv_ipm.frontier_selector import (  # noqa: E402
    FRONTIER_FEATURE_NAMES,
    FrontierCandidate,
    choose_frontier_actions,
    frontier_feature_vector,
)
from safekv_ipm.safety_gate import predict_unsafe_probability  # noqa: E402


ANSWER_GENERATION_MODE = "manual_position_ids"
ACTUAL_RECOMPUTE_PREFIX = "actual_recompute::"
ACTUAL_LOCAL_RECOMPUTE_PREFIX = "actual_local_recompute::"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--max-examples-per-category", type=int, default=None)
    parser.add_argument("--methods", type=str, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--random-seed", type=int, default=0)
    parser.add_argument("--data-path", type=str, default=None)
    parser.add_argument("--selector-artifact", type=Path, default=None)
    parser.add_argument("--frontier-selector-artifact", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    require_fixed_python_hash_seed()
    config_path = args.config.resolve()
    startup_config_sha256 = file_sha256(config_path)
    startup_implementation_sha256 = implementation_hashes()
    config = load_config(args.config)
    if (
        file_sha256(config_path) != startup_config_sha256
        or implementation_hashes() != startup_implementation_sha256
    ):
        raise RuntimeError(
            "config or implementation changed while initializing answer evaluation; "
            "rerun from a stable source tree"
        )
    if args.data_path is not None:
        config = replace(config, data=replace(config.data, path=args.data_path))
    if config.generation.do_sample:
        raise ValueError("answer evaluation requires do_sample=false")
    if config.generation.temperature != 0.0:
        raise ValueError("answer evaluation requires temperature=0")

    config_dir = config_path.parent.parent
    data_path = Path(config.data.path)
    if not data_path.is_absolute():
        data_path = config_dir / data_path
    data_path = data_path.resolve()
    selector_path = args.selector_artifact.resolve() if args.selector_artifact else None
    frontier_selector_path = (
        args.frontier_selector_artifact.resolve()
        if args.frontier_selector_artifact
        else None
    )
    execution_snapshot = capture_answer_execution_snapshot(
        config_path=config_path,
        data_path=data_path,
        selector_path=selector_path,
        frontier_selector_path=frontier_selector_path,
    )
    if (
        execution_snapshot["config_sha256"] != startup_config_sha256
        or execution_snapshot["implementation_sha256"]
        != startup_implementation_sha256
    ):
        raise RuntimeError(
            "config or implementation changed before input snapshot capture; "
            "rerun from a stable source tree"
        )
    set_deterministic_seed(config.seed)
    examples = load_examples_for_config(config, config_dir=config_dir)
    if args.max_examples_per_category is not None:
        examples = select_examples_per_category(examples, args.max_examples_per_category)
    if args.max_examples is not None:
        examples = examples[: args.max_examples]

    methods = resolve_methods(args.methods, config.experiment.methods)
    selector_artifact = load_selector_artifact(args.selector_artifact)
    frontier_selector_artifact = load_frontier_selector_artifact(
        args.frontier_selector_artifact
    )
    args.results_dir.mkdir(parents=True, exist_ok=True)
    assert_results_dir_not_invalidated(args.results_dir)
    assert_answer_execution_snapshot_unchanged(
        execution_snapshot,
        config_path=config_path,
        data_path=data_path,
        selector_path=selector_path,
        frontier_selector_path=frontier_selector_path,
        results_dir=args.results_dir,
        stage="after_input_load",
    )

    # Load the exact model before creating/comparing the resume manifest so the
    # resolved Hub snapshot, attention backend, and runtime can be pinned.
    loaded = load_causal_lm(config.model)
    assert_answer_execution_snapshot_unchanged(
        execution_snapshot,
        config_path=config_path,
        data_path=data_path,
        selector_path=selector_path,
        frontier_selector_path=frontier_selector_path,
        results_dir=args.results_dir,
        stage="after_model_load",
    )

    outputs_path = args.results_dir / "answer_eval_outputs.jsonl"
    metrics_path = args.results_dir / "answer_eval_metrics.csv"
    summary_path = args.results_dir / "answer_eval_summary.json"
    failure_path = args.results_dir / "answer_failure_analysis.md"
    manifest_path = args.results_dir / "answer_eval_manifest.json"

    manifest = answer_eval_manifest(
        args=args,
        config=config,
        methods=methods,
        loaded=loaded,
        execution_snapshot=execution_snapshot,
    )
    if args.resume:
        if not manifest_path.exists():
            raise ValueError(
                f"cannot resume without a run manifest: {manifest_path}; "
                "use a new results directory"
            )
        previous_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous_manifest != manifest:
            raise ValueError(
                "resume manifest mismatch; use the original inputs/options or a new "
                "results directory"
            )
    else:
        outputs_path.unlink(missing_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    completed = completed_output_keys(outputs_path) if args.resume else set()
    failed_rows: list[dict[str, Any]] = []
    for example in examples:
        pack = build_prompt_pack_for_config(example, loaded, config)
        full_state = run_full_prefill_answer_state(
            example=example,
            pack=pack,
            loaded=loaded,
            config=config,
        )
        base_state: dict[str, Any] | None = None
        full_cache = full_state["full_cache"]

        for method in methods:
            key = (example.id, method)
            if key in completed:
                continue
            try:
                if method == "full_prefill":
                    row = full_prefill_answer_row(example, pack, full_state)
                else:
                    if method != "exact_prefix_reuse" and base_state is None:
                        base_state = run_base_answer_state(
                            example=example,
                            pack=pack,
                            loaded=loaded,
                            config=config,
                            full_logits=full_state["first_logits"],
                        )
                    row = run_method_answer_row(
                        method=method,
                        example=example,
                        pack=pack,
                        loaded=loaded,
                        config=config,
                        full_state=full_state,
                        base_state=base_state,
                        full_cache=full_cache,
                        random_seed=args.random_seed,
                        selector_artifact=selector_artifact,
                        frontier_selector_artifact=frontier_selector_artifact,
                    )
                append_answer_rows(outputs_path, [row])
                completed.add(key)
            except Exception as exc:  # pragma: no cover - real model diagnostics only
                failed_rows.append(
                    {
                        "example_id": example.id,
                        "category": example.category,
                        "method": method,
                        "error": repr(exc),
                    }
                )

    assert_answer_execution_snapshot_unchanged(
        execution_snapshot,
        config_path=config_path,
        data_path=data_path,
        selector_path=selector_path,
        frontier_selector_path=frontier_selector_path,
        results_dir=args.results_dir,
        stage="after_evaluation",
    )
    rows = read_answer_rows(outputs_path)
    write_answer_metrics_csv(metrics_path, rows)
    summary = summarize_answer_eval_rows(rows)
    summary["failed_rows"] = failed_rows
    summary["num_failed_rows"] = len(failed_rows)
    summary["config_path"] = str(args.config)
    summary["dataset_path"] = config.data.path
    summary["model_name"] = config.model.name
    summary["actual_device"] = loaded.device
    summary["torch_dtype"] = loaded.torch_dtype_name
    summary["prompt_format"] = config.experiment.prompt_format
    summary["generation_mode"] = ANSWER_GENERATION_MODE
    summary["max_new_tokens"] = config.generation.max_new_tokens
    summary["stop_on_newline"] = config.generation.stop_on_newline
    summary["stop_strings"] = list(config.generation.stop_strings or [])
    summary["selected_methods"] = methods
    summary["selector_artifact"] = str(args.selector_artifact) if args.selector_artifact else None
    summary["frontier_selector_artifact"] = (
        str(args.frontier_selector_artifact) if args.frontier_selector_artifact else None
    )
    summary["resume"] = bool(args.resume)
    summary["outputs"] = {
        "answer_eval_outputs": str(outputs_path),
        "answer_eval_metrics_csv": str(metrics_path),
        "answer_eval_summary": str(summary_path),
        "answer_failure_analysis": str(failure_path),
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    failure_path.write_text(
        answer_failure_analysis_markdown(rows, summary),
        encoding="utf-8",
    )
    print(json.dumps(compact_console_summary(summary), indent=2, ensure_ascii=False))


def answer_eval_manifest(
    *,
    args: argparse.Namespace,
    config: Any,
    methods: list[str],
    loaded: Any,
    execution_snapshot: dict[str, Any],
) -> dict[str, Any]:
    risk_weights = resolve_risk_weights(config.risk.weights)
    return {
        "schema_version": 6,
        "config_path": execution_snapshot["config_path"],
        "config_sha256": execution_snapshot["config_sha256"],
        "data_path": execution_snapshot["data_path"],
        "data_sha256": execution_snapshot["data_sha256"],
        "model_name": config.model.name,
        "model_commit_hash": getattr(loaded.model.config, "_commit_hash", None),
        "tokenizer_commit_hash": getattr(
            loaded.tokenizer, "init_kwargs", {}
        ).get("_commit_hash"),
        "tokenizer_sha256": tokenizer_sha256(loaded.tokenizer),
        "model_dtype": config.model.dtype,
        "resolved_torch_dtype": loaded.torch_dtype_name,
        "actual_device": loaded.device,
        "attention_implementation": getattr(
            loaded.model.config, "_attn_implementation", None
        ),
        "runtime": runtime_provenance(loaded),
        "implementation_sha256": execution_snapshot["implementation_sha256"],
        "answer_generation_mode": ANSWER_GENERATION_MODE,
        "seed": config.seed,
        "random_seed": args.random_seed,
        "max_examples": args.max_examples,
        "max_examples_per_category": args.max_examples_per_category,
        "methods": methods,
        "risk_selector": {
            "weights": risk_weights,
            "formula": "sum(weights[feature] * feature_value)",
            "features": {
                "retrieval_score": "per-example min-max-normalized document retrieval score",
                "query_similarity": "recall of unique normalized non-stopword alphanumeric question terms in document title and text",
                "entity_overlap": "recall of regex-extracted question entities in document title and text",
                "conflict_indicator": "1 when the document participates in a date/number disagreement under comparison cues or sufficient question overlap; otherwise 0",
                "cross_doc_shared_entity": "per-example min-max-normalized count of extracted entities shared with other documents",
            },
            "tie_break": "descending score, then ascending document id/input order",
        },
        "selector_artifact": execution_snapshot["selector_artifact"],
        "selector_artifact_sha256": execution_snapshot[
            "selector_artifact_sha256"
        ],
        "frontier_selector_artifact": execution_snapshot[
            "frontier_selector_artifact"
        ],
        "frontier_selector_artifact_sha256": execution_snapshot[
            "frontier_selector_artifact_sha256"
        ],
    }


def resolve_methods(value: str | None, configured: list[str]) -> list[str]:
    methods = parse_methods_arg(value) if value is not None else list(configured)
    if not methods:
        raise ValueError("answer evaluation requires at least one configured method")
    if len(methods) != len(set(methods)):
        raise ValueError("answer evaluation methods must not contain duplicates")
    return methods


def load_frontier_selector_artifact(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    resolved = Path(path).resolve()
    artifact = json.loads(resolved.read_text(encoding="utf-8"))
    if artifact.get("type") != "linear_logistic_executable_suffix_frontier_selector":
        raise ValueError("unexpected frozen frontier selector artifact type")
    if artifact.get("feature_contract", {}).get("names") != list(
        FRONTIER_FEATURE_NAMES
    ):
        raise ValueError("frozen frontier selector feature contract mismatch")
    if artifact.get("integrity", {}).get("test_set_used") is not False:
        raise ValueError("frontier selector does not certify calibration-only fitting")
    model = artifact.get("model", {})
    expected = len(FRONTIER_FEATURE_NAMES)
    for name in ("means", "scales", "coefficients"):
        if len(model.get(name, [])) != expected:
            raise ValueError(f"frontier selector {name} length mismatch")
    return artifact


def implementation_hashes(*, code_root: Path | None = None) -> dict[str, str]:
    production_root = Path(__file__).resolve().parents[1]
    code_root = production_root if code_root is None else code_root.resolve()
    runner_path = (
        Path(__file__).resolve()
        if code_root == production_root
        else code_root / "scripts" / "run_answer_eval.py"
    )
    paths = [
        runner_path,
        *sorted((code_root / "safekv").rglob("*.py")),
        *sorted((code_root / "safekv_ipm").rglob("*.py")),
    ]
    return {
        str(path.relative_to(code_root)): file_sha256(path)
        for path in paths
    }


def capture_answer_execution_snapshot(
    *,
    config_path: Path,
    data_path: Path,
    selector_path: Path | None,
    frontier_selector_path: Path | None = None,
    code_root: Path | None = None,
) -> dict[str, Any]:
    """Capture every mutable local input that can affect an answer run."""

    return {
        "config_path": str(config_path.resolve()),
        "config_sha256": file_sha256(config_path.resolve()),
        "data_path": str(data_path.resolve()),
        "data_sha256": file_sha256(data_path.resolve()),
        "selector_artifact": str(selector_path.resolve()) if selector_path else None,
        "selector_artifact_sha256": (
            file_sha256(selector_path.resolve()) if selector_path else None
        ),
        "frontier_selector_artifact": (
            str(frontier_selector_path.resolve()) if frontier_selector_path else None
        ),
        "frontier_selector_artifact_sha256": (
            file_sha256(frontier_selector_path.resolve())
            if frontier_selector_path
            else None
        ),
        "implementation_sha256": implementation_hashes(code_root=code_root),
    }


def assert_results_dir_not_invalidated(results_dir: Path) -> None:
    invalid_provenance_path = results_dir / "INVALID_PROVENANCE_DRIFT.json"
    if invalid_provenance_path.exists():
        raise ValueError(
            f"results directory was permanently invalidated by provenance drift: "
            f"{invalid_provenance_path}; use a new results directory"
        )


def require_fixed_python_hash_seed() -> None:
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise ValueError(
            "answer evaluation requires PYTHONHASHSEED=0 to pin process-level "
            "hash iteration; set it before launching Python"
        )


def assert_answer_execution_snapshot_unchanged(
    expected: dict[str, Any],
    *,
    config_path: Path,
    data_path: Path,
    selector_path: Path | None,
    frontier_selector_path: Path | None = None,
    results_dir: Path | None = None,
    stage: str,
    code_root: Path | None = None,
) -> None:
    """Fail closed if code or inputs drift after they were parsed or loaded."""

    try:
        observed = capture_answer_execution_snapshot(
            config_path=config_path,
            data_path=data_path,
            selector_path=selector_path,
            frontier_selector_path=frontier_selector_path,
            code_root=code_root,
        )
    except OSError as exc:
        observed = {"snapshot_error": repr(exc)}
    if observed == expected:
        return
    report = {
        "status": "INVALID_PROVENANCE_DRIFT",
        "stage": stage,
        "expected": expected,
        "observed": observed,
    }
    if results_dir is not None:
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "INVALID_PROVENANCE_DRIFT.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    raise RuntimeError(
        f"answer-evaluation code or inputs changed at {stage}; "
        "discard this directory and rerun fresh"
    )


def tokenizer_sha256(tokenizer: Any) -> str:
    backend = getattr(tokenizer, "backend_tokenizer", None)
    if backend is None or not hasattr(backend, "to_str"):
        raise ValueError("a serializable fast tokenizer is required for provenance")
    digest = hashlib.sha256()
    digest.update(backend.to_str().encode("utf-8"))
    metadata = {
        "class": f"{tokenizer.__class__.__module__}.{tokenizer.__class__.__qualname__}",
        "special_tokens_map": getattr(tokenizer, "special_tokens_map", {}),
        "chat_template": getattr(tokenizer, "chat_template", None),
        "model_max_length": getattr(tokenizer, "model_max_length", None),
        "padding_side": getattr(tokenizer, "padding_side", None),
        "truncation_side": getattr(tokenizer, "truncation_side", None),
    }
    digest.update(
        json.dumps(
            metadata,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
    )
    return digest.hexdigest()


def runtime_provenance(loaded: Any) -> dict[str, Any]:
    import numpy
    import yaml
    import torch
    import tokenizers
    import transformers

    try:
        import scipy
    except ImportError:
        scipy = None

    runtime: dict[str, Any] = {
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "pyyaml": yaml.__version__,
        "scipy_present": scipy is not None,
        "scipy": scipy.__version__ if scipy is not None else None,
        "torch": torch.__version__,
        "tokenizers": tokenizers.__version__,
        "transformers": transformers.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "nvidia_driver": nvidia_driver_version(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "deterministic_algorithms_warn_only": (
            torch.is_deterministic_algorithms_warn_only_enabled()
        ),
        "deterministic_debug_mode": torch.get_deterministic_debug_mode(),
        "cudnn_enabled": torch.backends.cudnn.enabled,
        "cudnn_deterministic": torch.backends.cudnn.deterministic,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
        "float32_matmul_precision": torch.get_float32_matmul_precision(),
        "cuda_matmul_allow_tf32": torch.backends.cuda.matmul.allow_tf32,
        "cuda_matmul_allow_fp16_reduced_precision_reduction": (
            torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction
        ),
        "cuda_matmul_allow_bf16_reduced_precision_reduction": (
            torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction
        ),
        "cuda_matmul_allow_fp16_accumulation": (
            torch.backends.cuda.matmul.allow_fp16_accumulation
        ),
        "cudnn_allow_tf32": torch.backends.cudnn.allow_tf32,
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
    }
    if loaded.device == "cuda":
        runtime.update(
            {
                "gpu": torch.cuda.get_device_name(0),
                "cuda_device_capability": list(torch.cuda.get_device_capability(0)),
                "sdpa_flash_enabled": torch.backends.cuda.flash_sdp_enabled(),
                "sdpa_mem_efficient_enabled": (
                    torch.backends.cuda.mem_efficient_sdp_enabled()
                ),
                "sdpa_math_enabled": torch.backends.cuda.math_sdp_enabled(),
                "sdpa_cudnn_enabled": torch.backends.cuda.cudnn_sdp_enabled(),
                "sdpa_fp16_bf16_reduction_math_allowed": (
                    torch.backends.cuda.fp16_bf16_reduction_math_sdp_allowed()
                ),
            }
        )
    return runtime


def nvidia_driver_version() -> str | None:
    try:
        return subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=driver_version",
                "--format=csv,noheader",
            ],
            text=True,
            timeout=5,
        ).splitlines()[0].strip()
    except (OSError, subprocess.SubprocessError, IndexError):
        return None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_full_prefill_answer_state(
    *,
    example: DiagnosticExample,
    pack: PromptPack,
    loaded: Any,
    config: Any,
) -> dict[str, Any]:
    import torch

    input_ids = torch.tensor([pack.full_input_ids], dtype=torch.long, device=loaded.device)
    attention_mask = torch.ones_like(input_ids)
    position_ids = torch.arange(input_ids.shape[1], dtype=torch.long, device=loaded.device).unsqueeze(0)
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            use_cache=True,
        )
        # Greedy generation mutates a DynamicCache by appending answer tokens.
        # Freeze the prompt donor before generation so replacement ranges can
        # never observe or retain a generated-token tail.
        prompt_cache = clone_legacy_cache(outputs.past_key_values)
        if cache_seq_len(prompt_cache) != input_ids.shape[1]:
            raise ValueError("full-prefill prompt cache length mismatch")
        first_logits = outputs.logits[:, -1, :].detach().float().cpu()[0]
        token_ids = greedy_generate_from_prefill(
            model=loaded.model,
            tokenizer=loaded.tokenizer,
            prompt_outputs=outputs,
            first_logits=outputs.logits,
            prompt_length=input_ids.shape[1],
            max_new_tokens=config.generation.max_new_tokens,
            stop_on_newline=config.generation.stop_on_newline,
            stop_strings=config.generation.stop_strings,
            device=loaded.device,
            mode=ANSWER_GENERATION_MODE,
        )
    return {
        "first_logits": first_logits,
        "generated_token_ids": token_ids,
        "generated_answer": decode_and_trim_answer(loaded.tokenizer, token_ids, config),
        "full_cache": prompt_cache,
    }


def run_base_answer_state(
    *,
    example: DiagnosticExample,
    pack: PromptPack,
    loaded: Any,
    config: Any,
    full_logits: Any,
) -> dict[str, Any]:
    _ = example
    base_cache, cache_metadata = build_naive_composed_context_cache(
        loaded.model,
        pack,
        loaded.device,
        position_mode="global",
        includes_prefix_cache=True,
        doc_conditioning="prefix",
    )
    query_state = run_query_and_generate_from_context_cache(
        loaded=loaded,
        config=config,
        pack=pack,
        context_cache=base_cache,
    )
    logit_metrics = logit_preservation_metrics(
        full_logits,
        query_state["first_logits"],
        loaded.tokenizer,
    )
    return {
        "context_cache": base_cache,
        "cache_metadata": cache_metadata,
        **query_state,
        "logit_metrics": logit_metrics,
    }


def run_method_answer_row(
    *,
    method: str,
    example: DiagnosticExample,
    pack: PromptPack,
    loaded: Any,
    config: Any,
    full_state: dict[str, Any],
    base_state: dict[str, Any] | None,
    full_cache: Any,
    random_seed: int,
    selector_artifact: dict[str, Any] | None,
    frontier_selector_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    method_metadata: dict[str, Any] = {}
    if method == "exact_prefix_reuse":
        context_length = pack.query_token_range.start
        exact_context_cache = slice_legacy_cache(full_cache, 0, context_length)
        query_state = run_query_and_generate_from_context_cache(
            loaded=loaded,
            config=config,
            pack=pack,
            context_cache=exact_context_cache,
        )
        logit_metrics = logit_preservation_metrics(
            full_state["first_logits"],
            query_state["first_logits"],
            loaded.tokenizer,
        )
        patch_ranges = []
        selected_doc_ids = []
        method_metadata = {
            "cache_control": "exact_prefix",
            "exact_prefix_length": context_length,
        }
    elif method == "prefix_conditioned_naive_global":
        if base_state is None:
            raise ValueError("prefix-conditioned composition state is missing")
        patch_ranges: list[TokenRange] = []
        selected_doc_ids: list[int] = []
        query_state = base_state
        logit_metrics = base_state["logit_metrics"]
    else:
        if base_state is None:
            raise ValueError("prefix-conditioned composition state is missing")
        actual_suffix_recompute = method.startswith(ACTUAL_RECOMPUTE_PREFIX)
        actual_local_recompute = method.startswith(ACTUAL_LOCAL_RECOMPUTE_PREFIX)
        if actual_suffix_recompute and actual_local_recompute:
            raise ValueError("method cannot request both local and suffix recomputation")
        if actual_suffix_recompute:
            policy_method = method.removeprefix(ACTUAL_RECOMPUTE_PREFIX)
        elif actual_local_recompute:
            policy_method = method.removeprefix(ACTUAL_LOCAL_RECOMPUTE_PREFIX)
        else:
            policy_method = method
        if policy_method == "frozen_frontier_selector":
            if not actual_suffix_recompute:
                raise ValueError(
                    "frozen_frontier_selector must use actual_recompute:: execution"
                )
            patch_ranges, selected_doc_ids, method_metadata = (
                frozen_frontier_patch_ranges(
                    example=example,
                    pack=pack,
                    artifact=frontier_selector_artifact,
                )
            )
        else:
            patch_ranges, selected_doc_ids = patch_ranges_for_answer_method(
                method=policy_method,
                example=example,
                pack=pack,
                seed=random_seed,
                selector_artifact=selector_artifact,
                risk_weights=config.risk.weights,
            )
        validate_patch_ranges_within_documents(patch_ranges, pack)
        full_prefill_fallback = bool(
            method_metadata.get("frontier_full_prefill_fallback", False)
        )
        if full_prefill_fallback:
            query_state = full_state
            logit_metrics = {
                "first_token_kl_full_to_method": 0.0,
                "first_token_js_divergence": 0.0,
                "max_abs_logit_diff": 0.0,
                "mean_abs_logit_diff": 0.0,
                "top1_match": True,
                "top5_overlap": 1.0,
                "top10_overlap": 1.0,
            }
        else:
            if not patch_ranges:
                context_cache = base_state["context_cache"]
            elif actual_suffix_recompute:
                context_cache = recompute_answer_suffix(
                    pack=pack,
                    loaded=loaded,
                    base_cache=base_state["context_cache"],
                    patch_ranges=patch_ranges,
                )
            elif actual_local_recompute:
                context_cache = recompute_answer_ranges_locally(
                    pack=pack,
                    loaded=loaded,
                    base_cache=base_state["context_cache"],
                    patch_ranges=patch_ranges,
                )
            else:
                context_cache = replace_cache_slices(
                    base_state["context_cache"],
                    full_cache,
                    patch_ranges,
                )
            if cache_seq_len(context_cache) != cache_seq_len(
                base_state["context_cache"]
            ):
                raise ValueError("patched cache length mismatch")
            query_state = run_query_and_generate_from_context_cache(
                loaded=loaded,
                config=config,
                pack=pack,
                context_cache=context_cache,
            )
            logit_metrics = logit_preservation_metrics(
                full_state["first_logits"],
                query_state["first_logits"],
                loaded.tokenizer,
            )

    composed_len = (
        pack.query_token_range.start
        if method == "exact_prefix_reuse"
        else int(base_state["cache_metadata"]["composed_context_length"])
    )
    patched_count = (
        composed_len
        if method_metadata.get("frontier_full_prefill_fallback", False)
        else token_count(patch_ranges)
    )
    online_context_prefill_fraction = (
        patched_count / composed_len if composed_len else 0.0
    )
    return make_answer_eval_row(
        example_id=example.id,
        category=example.category,
        method=method,
        generated_answer=query_state["generated_answer"],
        full_prefill_answer=full_state["generated_answer"],
        gold_answer=example.gold_answer,
        patched_doc_count=len(selected_doc_ids),
        patched_token_count=patched_count,
        patched_token_ratio=patched_count / composed_len if composed_len else 0.0,
        prompt_length=len(pack.full_input_ids),
        query_length=pack.query_token_range.length,
        first_token_kl_full_to_method=logit_metrics["first_token_kl_full_to_method"],
        top1_match=logit_metrics["top1_match"],
        extra={
            # This is the steady-state online context-compute cost used by the
            # journal analysis.  Keep it distinct from patched_token_ratio:
            # the latter describes cache surgery, whereas an explicit
            # full-prefill fallback has no "patch" but costs the whole context.
            "online_context_prefill_fraction": online_context_prefill_fraction,
            "online_context_prefill_token_count": patched_count,
            "context_token_count": composed_len,
            "selected_doc_ids": selected_doc_ids,
            "generated_token_ids": query_state["generated_token_ids"],
            "full_prefill_token_ids": full_state["generated_token_ids"],
            "generated_token_sequence_exact_to_full_prefill": (
                query_state["generated_token_ids"] == full_state["generated_token_ids"]
            ),
            "first_token_js_divergence": logit_metrics[
                "first_token_js_divergence"
            ],
            "max_abs_logit_diff": logit_metrics["max_abs_logit_diff"],
            "mean_abs_logit_diff": logit_metrics["mean_abs_logit_diff"],
            "top5_overlap": logit_metrics["top5_overlap"],
            "top10_overlap": logit_metrics["top10_overlap"],
            **method_metadata,
        },
    )


def frozen_frontier_patch_ranges(
    *,
    example: DiagnosticExample,
    pack: PromptPack,
    artifact: dict[str, Any] | None,
) -> tuple[list[TokenRange], list[int], dict[str, Any]]:
    """Execute the calibration-frozen start selector using pre-generation inputs."""

    import numpy as np

    if artifact is None:
        raise ValueError(
            "actual_recompute::frozen_frontier_selector requires "
            "--frontier-selector-artifact"
        )
    count = len(example.documents)
    example_dict = example.to_dict()
    context_tokens = max(1, pack.query_token_range.start)
    candidates = []
    for start in range(count + 1):
        patched_tokens = sum(item.length for item in pack.doc_ranges[start:])
        candidates.append(
            FrontierCandidate(
                example_id=example.id,
                group_id=example.id,
                dataset="runtime",
                condition="runtime",
                start=start,
                num_documents=count,
                unsafe=False,
                patch_ratio=patched_tokens / context_tokens,
                features=frontier_feature_vector(
                    example_dict,
                    start=start,
                    prompt_length=len(pack.full_input_ids),
                ),
            )
        )
    model = artifact["model"]
    matrix = np.asarray([candidate.features for candidate in candidates], dtype=np.float64)
    probabilities = predict_unsafe_probability(
        matrix,
        means=model["means"],
        scales=model["scales"],
        coefficients=model["coefficients"],
        intercept=model["intercept"],
    )
    threshold = float(artifact["threshold"])
    action = choose_frontier_actions(
        candidates,
        probabilities,
        threshold=threshold,
    )[example.id]
    fallback = action is None
    selected_start = 0 if fallback else int(action.start)
    selected_doc_ids = [doc.doc_id for doc in example.documents[selected_start:]]
    ranges = document_ranges_for_ids(example, pack, selected_doc_ids)
    return ranges, selected_doc_ids, {
        "frontier_selected_start": None if fallback else selected_start,
        "frontier_full_prefill_fallback": fallback,
        "frontier_frozen_threshold": threshold,
        "frontier_selected_unsafe_probability": (
            None if fallback else float(probabilities[selected_start])
        ),
    }


def recompute_answer_suffix(
    *,
    pack: PromptPack,
    loaded: Any,
    base_cache: Any,
    patch_ranges: list[TokenRange],
) -> Any:
    """Execute a selected suffix against the composed prefix cache.

    The paper-facing answer evaluator historically copied the corresponding KV
    slices from a separately computed full-prefill cache.  This helper instead
    measures the deployable path used by the latency evaluator: retain the
    composed cache before the selected frontier and run the complete contiguous
    suffix through the model under that retained prefix state.
    """

    import torch

    ordered_ranges = sorted(patch_ranges, key=lambda item: (item.start, item.end))
    if not ordered_ranges:
        return base_cache
    if any(
        previous.end != current.start
        for previous, current in zip(ordered_ranges, ordered_ranges[1:])
    ):
        raise ValueError("actual suffix recompute requires one gap-free token range")
    token_range = TokenRange(ordered_ranges[0].start, ordered_ranges[-1].end)
    if token_count(patch_ranges) != token_range.length:
        raise ValueError("actual suffix recompute ranges contain gaps or overlap")
    if token_range.end != pack.query_token_range.start:
        raise ValueError("actual suffix recompute must end at the query boundary")
    if not pack.doc_ranges or token_range.start < pack.doc_ranges[0].start:
        raise ValueError("actual suffix recompute must start inside document tokens")

    prefix_cache = slice_legacy_cache(base_cache, 0, token_range.start)
    input_ids = torch.tensor(
        [pack.full_input_ids[token_range.start : token_range.end]],
        dtype=torch.long,
        device=loaded.device,
    )
    position_ids = torch.arange(
        token_range.start,
        token_range.end,
        dtype=torch.long,
        device=loaded.device,
    ).unsqueeze(0)
    attention_mask = torch.ones(
        (1, token_range.end),
        dtype=torch.long,
        device=loaded.device,
    )
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=legacy_cache_to_model_cache(prefix_cache),
            use_cache=True,
        )
    donor_cache = to_legacy_cache(outputs.past_key_values)
    return replace_cache_slices(base_cache, donor_cache, [token_range])


def recompute_answer_ranges_locally(
    *,
    pack: PromptPack,
    loaded: Any,
    base_cache: Any,
    patch_ranges: list[TokenRange],
) -> Any:
    """Actually forward selected ranges while deliberately retaining later stale K/V.

    Each range is recomputed under the cache state that precedes it after any
    earlier selected ranges have been repaired. Unselected gaps and all states
    after the final range remain from the composed cache. This is the executable
    counterpart of document/window-only repair, not a donor-copy oracle.
    """

    import torch

    ordered_ranges = sorted(patch_ranges, key=lambda item: (item.start, item.end))
    if any(
        previous.end > current.start
        for previous, current in zip(ordered_ranges, ordered_ranges[1:])
    ):
        raise ValueError("actual local recompute ranges must not overlap")
    context_length = cache_seq_len(base_cache)
    current_cache = base_cache
    for token_range in ordered_ranges:
        if token_range.start < 0 or token_range.end > context_length:
            raise ValueError("actual local recompute range falls outside context cache")
        prefix_cache = slice_legacy_cache(current_cache, 0, token_range.start)
        input_ids = torch.tensor(
            [pack.full_input_ids[token_range.start : token_range.end]],
            dtype=torch.long,
            device=loaded.device,
        )
        position_ids = torch.arange(
            token_range.start,
            token_range.end,
            dtype=torch.long,
            device=loaded.device,
        ).unsqueeze(0)
        attention_mask = torch.ones(
            (1, token_range.end),
            dtype=torch.long,
            device=loaded.device,
        )
        with torch.no_grad():
            outputs = loaded.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                position_ids=position_ids,
                past_key_values=legacy_cache_to_model_cache(prefix_cache),
                use_cache=True,
            )
        donor_cache = to_legacy_cache(outputs.past_key_values)
        current_cache = replace_cache_slices(
            current_cache,
            donor_cache,
            [token_range],
        )
    if cache_seq_len(current_cache) != context_length:
        raise ValueError("actual local recompute changed context cache length")
    return current_cache


def full_prefill_answer_row(
    example: DiagnosticExample,
    pack: PromptPack,
    full_state: dict[str, Any],
) -> dict[str, Any]:
    return make_answer_eval_row(
        example_id=example.id,
        category=example.category,
        method="full_prefill",
        generated_answer=full_state["generated_answer"],
        full_prefill_answer=full_state["generated_answer"],
        gold_answer=example.gold_answer,
        patched_doc_count=0,
        patched_token_count=0,
        patched_token_ratio=0.0,
        prompt_length=len(pack.full_input_ids),
        query_length=pack.query_token_range.length,
        first_token_kl_full_to_method=0.0,
        top1_match=True,
        extra={
            "online_context_prefill_fraction": 1.0,
            "online_context_prefill_token_count": pack.query_token_range.start,
            "context_token_count": pack.query_token_range.start,
            "selected_doc_ids": [],
            "generated_token_ids": full_state["generated_token_ids"],
            "full_prefill_token_ids": full_state["generated_token_ids"],
            "generated_token_sequence_exact_to_full_prefill": True,
            "first_token_js_divergence": 0.0,
            "max_abs_logit_diff": 0.0,
            "mean_abs_logit_diff": 0.0,
            "top5_overlap": 1.0,
            "top10_overlap": 1.0,
        },
    )


def run_query_and_generate_from_context_cache(
    *,
    loaded: Any,
    config: Any,
    pack: PromptPack,
    context_cache: Any,
) -> dict[str, Any]:
    import torch

    query_range = pack.query_token_range
    query_ids = torch.tensor(
        [pack.full_input_ids[query_range.start : query_range.end]],
        dtype=torch.long,
        device=loaded.device,
    )
    query_position_ids = torch.arange(
        query_range.start,
        query_range.end,
        dtype=torch.long,
        device=loaded.device,
    ).unsqueeze(0)
    composed_len = cache_seq_len(context_cache)
    attention_mask = torch.ones(
        (1, composed_len + query_ids.shape[1]),
        dtype=torch.long,
        device=loaded.device,
    )
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=query_ids,
            attention_mask=attention_mask,
            position_ids=query_position_ids,
            past_key_values=legacy_cache_to_model_cache(context_cache),
            use_cache=True,
        )
        first_logits = outputs.logits[:, -1, :].detach().float().cpu()[0]
        prompt_length = cache_seq_len(to_legacy_cache(outputs.past_key_values))
        token_ids = greedy_generate_from_prefill(
            model=loaded.model,
            tokenizer=loaded.tokenizer,
            prompt_outputs=outputs,
            first_logits=outputs.logits,
            prompt_length=prompt_length,
            max_new_tokens=config.generation.max_new_tokens,
            stop_on_newline=config.generation.stop_on_newline,
            stop_strings=config.generation.stop_strings,
            device=loaded.device,
            mode=ANSWER_GENERATION_MODE,
        )
    return {
        "first_logits": first_logits,
        "generated_token_ids": token_ids,
        "generated_answer": decode_and_trim_answer(loaded.tokenizer, token_ids, config),
    }


def patch_ranges_for_answer_method(
    *,
    method: str,
    example: DiagnosticExample,
    pack: PromptPack,
    seed: int,
    selector_artifact: dict[str, Any] | None = None,
    risk_weights: dict[str, float] | None = None,
) -> tuple[list[TokenRange], list[int]]:
    if method == "all_document_patch":
        selected_doc_ids = [doc.doc_id for doc in example.documents]
        return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids
    if method == "oracle_evidence_doc_patch":
        selected_doc_ids = sorted(
            {
                doc_id
                for token_range in oracle_evidence_doc_patch_ranges(example, pack)
                for doc_id in _doc_ids_for_ranges(example, pack, [token_range])
            }
        )
        return oracle_evidence_doc_patch_ranges(example, pack), selected_doc_ids
    if method == "oracle_evidence_doc_adjacent_patch":
        selected_doc_ids = _oracle_doc_ids_with_neighbors(example, neighbor_window=1)
        return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids
    if method == "oracle_evidence_doc_suffix_closure_patch":
        selected_doc_ids = _oracle_doc_suffix_closure_ids(example)
        return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids
    if method == "oracle_evidence_doc_linked_closure_patch":
        selected_doc_ids = _linked_closure_ids_from_selected(
            example,
            list(_oracle_doc_ids_for_example(example)),
        )
        return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids
    if method == "oracle_evidence_doc_linked_interval_patch":
        selected_doc_ids = _linked_interval_ids_from_selected(
            example,
            list(_oracle_doc_ids_for_example(example)),
        )
        return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids
    linked_closure_doc_ids = _selector_linked_closure_doc_ids(
        method,
        example,
        seed=seed,
        selector_artifact=selector_artifact,
        risk_weights=risk_weights,
    )
    if linked_closure_doc_ids is not None:
        return document_ranges_for_ids(example, pack, linked_closure_doc_ids), linked_closure_doc_ids
    linked_interval_doc_ids = _selector_linked_interval_doc_ids(
        method,
        example,
        seed=seed,
        selector_artifact=selector_artifact,
        risk_weights=risk_weights,
    )
    if linked_interval_doc_ids is not None:
        return document_ranges_for_ids(example, pack, linked_interval_doc_ids), linked_interval_doc_ids
    adaptive_doc_ids = _adaptive_suffix_doc_ids(
        method,
        example,
        seed=seed,
        selector_artifact=selector_artifact,
        risk_weights=risk_weights,
    )
    if adaptive_doc_ids is not None:
        return document_ranges_for_ids(example, pack, adaptive_doc_ids), adaptive_doc_ids
    downstream_doc_ids = _selector_downstream_doc_ids(
        method,
        example,
        seed=seed,
        selector_artifact=selector_artifact,
        risk_weights=risk_weights,
    )
    if downstream_doc_ids is not None:
        return document_ranges_for_ids(example, pack, downstream_doc_ids), downstream_doc_ids
    suffix_closure_doc_ids = _selector_suffix_closure_doc_ids(
        method,
        example,
        seed=seed,
        selector_artifact=selector_artifact,
        risk_weights=risk_weights,
    )
    if suffix_closure_doc_ids is not None:
        return document_ranges_for_ids(example, pack, suffix_closure_doc_ids), suffix_closure_doc_ids
    cost_aware_suffix_doc_ids = _cost_aware_suffix_doc_ids(
        method, example, risk_weights=risk_weights
    )
    if cost_aware_suffix_doc_ids is not None:
        return document_ranges_for_ids(example, pack, cost_aware_suffix_doc_ids), cost_aware_suffix_doc_ids
    margin_adaptive_suffix_doc_ids = _margin_adaptive_suffix_doc_ids(
        method, example, risk_weights=risk_weights
    )
    if margin_adaptive_suffix_doc_ids is not None:
        return (
            document_ranges_for_ids(example, pack, margin_adaptive_suffix_doc_ids),
            margin_adaptive_suffix_doc_ids,
        )
    hybrid_union_doc_ids = _hybrid_query_risk_union_suffix_doc_ids(
        method, example, risk_weights=risk_weights
    )
    if hybrid_union_doc_ids is not None:
        return document_ranges_for_ids(example, pack, hybrid_union_doc_ids), hybrid_union_doc_ids
    random_spec = _seeded_random_doc_patch_k(method)
    if random_spec is not None:
        random_k, explicit_seed = random_spec
        selected_doc_ids = random_doc_ids_same_count(
            example,
            count=random_k,
            seed=stable_example_seed(
                seed if explicit_seed is None else explicit_seed,
                example.id,
                method,
            ),
        )
        return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids
    if method.startswith("learned_doc_patch_"):
        selected_doc_ids = select_learned_doc_ids(method, example, selector_artifact)
        return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids

    granularity_ranges = _answer_granularity_ranges(method, example, pack, seed)
    if granularity_ranges is not None:
        return granularity_ranges, _doc_ids_for_ranges(example, pack, granularity_ranges)

    internal_method = internal_selector_method(method)
    selected_doc_ids, _reason = selected_doc_ids_for_method(
        internal_method,
        example,
        seed=seed,
        risk_weights=risk_weights,
    )
    return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids


def decode_and_trim_answer(tokenizer: Any, token_ids: list[int], config: Any) -> str:
    answer = tokenizer.decode(token_ids, skip_special_tokens=True).strip()
    return trim_generated_answer(
        answer,
        stop_on_newline=config.generation.stop_on_newline,
        stop_strings=config.generation.stop_strings,
    )


def compact_console_summary(summary: dict[str, Any]) -> dict[str, Any]:
    methods = {}
    for method, data in summary.get("method_level", {}).items():
        methods[method] = {
            "answer_equivalence_to_full_prefill": data[
                "answer_equivalence_to_full_prefill"
            ],
            "gold_exact_match": data["gold_exact_match"],
            "gold_token_f1": data["gold_token_f1"],
            "avg_patched_token_ratio": data["avg_patched_token_ratio"],
            "avg_online_context_prefill_fraction": data[
                "avg_online_context_prefill_fraction"
            ],
            "avg_first_token_kl": data["avg_first_token_kl"],
        }
    return {
        "num_rows": summary.get("num_rows"),
        "num_failed_rows": summary.get("num_failed_rows"),
        "category_counts": summary.get("category_counts"),
        "method_level": methods,
        "outputs": summary.get("outputs"),
    }


def _doc_ids_for_ranges(
    example: DiagnosticExample,
    pack: PromptPack,
    ranges: list[TokenRange],
) -> list[int]:
    doc_ids = []
    for doc, doc_range in zip(example.documents, pack.doc_ranges, strict=True):
        for token_range in ranges:
            if doc_range.start <= token_range.start and token_range.end <= doc_range.end:
                doc_ids.append(doc.doc_id)
                break
    return doc_ids


def _seeded_random_doc_patch_k(method: str) -> tuple[int, int | None] | None:
    return _seeded_random_method_spec(method, prefix="random_doc_patch_k")


def _seeded_random_suffix_closure_k(
    method: str,
) -> tuple[int, int | None] | None:
    return _seeded_random_method_spec(method, prefix="random_suffix_closure_k")


def _seeded_random_method_spec(
    method: str,
    *,
    prefix: str,
) -> tuple[int, int | None] | None:
    match = re.fullmatch(rf"{re.escape(prefix)}(\d+)_(?:seeded|seed(\d+))", method)
    if match is None:
        return None
    return int(match.group(1)), (int(match.group(2)) if match.group(2) else None)


def _answer_granularity_ranges(
    method: str,
    example: DiagnosticExample,
    pack: PromptPack,
    seed: int,
) -> list[TokenRange] | None:
    granularity_prefixes = (
        "oracle_evidence_span_window_",
        "oracle_evidence_suffix_patch",
        "oracle_evidence_sentence_to_doc_end_patch",
        "oracle_support_and_conflict_span_patch",
        "oracle_support_and_conflict_suffix_patch",
        "random_patch_same_budget::",
    )
    if not method.startswith(granularity_prefixes):
        return None
    return build_ranges_for_methods(example, pack, [method], seed=seed)[method]


def _oracle_doc_ids_with_neighbors(
    example: DiagnosticExample,
    *,
    neighbor_window: int,
) -> list[int]:
    oracle_ids = _oracle_doc_ids_for_example(example)
    if not oracle_ids:
        return []
    ordered_ids = [doc.doc_id for doc in example.documents]
    selected: set[int] = set()
    for index, doc_id in enumerate(ordered_ids):
        if doc_id not in oracle_ids:
            continue
        start = max(0, index - neighbor_window)
        end = min(len(ordered_ids), index + neighbor_window + 1)
        selected.update(ordered_ids[start:end])
    return [doc_id for doc_id in ordered_ids if doc_id in selected]


def _oracle_doc_suffix_closure_ids(example: DiagnosticExample) -> list[int]:
    oracle_ids = _oracle_doc_ids_for_example(example)
    if not oracle_ids:
        return []
    ordered_ids = [doc.doc_id for doc in example.documents]
    earliest_index = min(index for index, doc_id in enumerate(ordered_ids) if doc_id in oracle_ids)
    return ordered_ids[earliest_index:]


def _selector_suffix_closure_doc_ids(
    method: str,
    example: DiagnosticExample,
    *,
    seed: int,
    selector_artifact: dict[str, Any] | None,
    risk_weights: dict[str, float] | None = None,
) -> list[int] | None:
    if method.startswith("learned_suffix_closure_k"):
        learned_method = method.replace("learned_suffix_closure", "learned_doc_patch", 1)
        selected_doc_ids = select_learned_doc_ids(learned_method, example, selector_artifact)
    elif method.startswith("query_similarity_suffix_closure_k"):
        selector_method = method.replace(
            "query_similarity_suffix_closure",
            "query_similarity_doc_patch",
            1,
        )
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            selector_method, example, seed=seed, risk_weights=risk_weights
        )
    elif method.startswith("risk_guided_suffix_closure_k"):
        selector_method = method.replace(
            "risk_guided_suffix_closure",
            "risk_guided_doc_patch",
            1,
        )
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            selector_method, example, seed=seed, risk_weights=risk_weights
        )
    else:
        random_spec = _seeded_random_suffix_closure_k(method)
        if random_spec is None:
            return None
        random_k, explicit_seed = random_spec
        selected_doc_ids = random_doc_ids_same_count(
            example,
            count=random_k,
            seed=stable_example_seed(
                seed if explicit_seed is None else explicit_seed,
                example.id,
                method,
            ),
        )
    return _suffix_closure_ids_from_selected(example, selected_doc_ids)


def _cost_aware_suffix_doc_ids(
    method: str,
    example: DiagnosticExample,
    *,
    risk_weights: dict[str, float] | None = None,
) -> list[int] | None:
    query_match = re.fullmatch(r"query_similarity_cost_aware_suffix_a([0-9_]+)", method)
    risk_match = re.fullmatch(r"risk_guided_cost_aware_suffix_a([0-9_]+)", method)
    match = query_match or risk_match
    if match is None:
        return None
    alpha = float(match.group(1).replace("_", "."))
    scores = (
        query_similarity_doc_scores(example)
        if query_match is not None
        else risk_guided_doc_scores(example, risk_weights)
    )
    score_by_doc = {score.doc_id: score.score for score in scores}
    ordered_ids = [doc.doc_id for doc in example.documents]
    n_docs = max(1, len(ordered_ids))
    best_doc_id = ordered_ids[0]
    best_key: tuple[float, float, float, int] | None = None
    for index, doc_id in enumerate(ordered_ids):
        suffix_ratio = (n_docs - index) / n_docs
        raw_score = score_by_doc.get(doc_id, 0.0)
        adjusted_score = raw_score - alpha * suffix_ratio
        key = (adjusted_score, raw_score, -suffix_ratio, -doc_id)
        if best_key is None or key > best_key:
            best_key = key
            best_doc_id = doc_id
    return _suffix_closure_ids_from_selected(example, [best_doc_id])


def _margin_adaptive_suffix_doc_ids(
    method: str,
    example: DiagnosticExample,
    *,
    risk_weights: dict[str, float] | None = None,
) -> list[int] | None:
    query_match = re.fullmatch(r"query_similarity_margin_adaptive_suffix_m([0-9_]+)", method)
    risk_match = re.fullmatch(r"risk_guided_margin_adaptive_suffix_m([0-9_]+)", method)
    match = query_match or risk_match
    if match is None:
        return None
    margin = float(match.group(1).replace("_", "."))
    scores = (
        query_similarity_doc_scores(example)
        if query_match is not None
        else risk_guided_doc_scores(example, risk_weights)
    )
    ordered_scores = sorted(scores, key=lambda item: (-item.score, item.doc_id))
    if not ordered_scores:
        return []
    selected = [ordered_scores[0].doc_id]
    if len(ordered_scores) > 1:
        gap = ordered_scores[0].score - ordered_scores[1].score
        if gap <= margin:
            selected.append(ordered_scores[1].doc_id)
    return _suffix_closure_ids_from_selected(example, selected)


def _hybrid_query_risk_union_suffix_doc_ids(
    method: str,
    example: DiagnosticExample,
    *,
    risk_weights: dict[str, float] | None = None,
) -> list[int] | None:
    match = re.fullmatch(r"hybrid_query_risk_union_suffix_k(\d+)", method)
    if match is None:
        return None
    k = int(match.group(1))
    query_selected = _top_k_doc_ids_from_scores(query_similarity_doc_scores(example), k)
    risk_selected = _top_k_doc_ids_from_scores(
        risk_guided_doc_scores(example, risk_weights), k
    )
    selected = sorted(set(query_selected) | set(risk_selected))
    return _suffix_closure_ids_from_selected(example, selected)


def _top_k_doc_ids_from_scores(scores: list[Any], k: int) -> list[int]:
    if k <= 0:
        return []
    ordered = sorted(scores, key=lambda item: (-item.score, item.doc_id))
    return [item.doc_id for item in ordered[:k]]


def _selector_linked_closure_doc_ids(
    method: str,
    example: DiagnosticExample,
    *,
    seed: int,
    selector_artifact: dict[str, Any] | None,
    risk_weights: dict[str, float] | None = None,
) -> list[int] | None:
    query_match = re.fullmatch(r"query_similarity_linked_closure_k(\d+)", method)
    risk_match = re.fullmatch(r"risk_guided_linked_closure_k(\d+)", method)
    learned_match = re.fullmatch(r"learned_linked_closure_k(\d+)", method)
    random_match = re.fullmatch(r"random_linked_closure_k(\d+)_seeded", method)
    if query_match is not None:
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            f"query_similarity_doc_patch_k{query_match.group(1)}",
            example,
            seed=seed,
        )
    elif risk_match is not None:
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            f"risk_guided_doc_patch_k{risk_match.group(1)}",
            example,
            seed=seed,
            risk_weights=risk_weights,
        )
    elif learned_match is not None:
        selected_doc_ids = select_learned_doc_ids(
            f"learned_doc_patch_k{learned_match.group(1)}",
            example,
            selector_artifact,
        )
    elif random_match is not None:
        selected_doc_ids = random_doc_ids_same_count(
            example,
            count=int(random_match.group(1)),
            seed=stable_example_seed(seed, example.id, method),
        )
    else:
        return None
    return _linked_closure_ids_from_selected(example, selected_doc_ids)


def _selector_linked_interval_doc_ids(
    method: str,
    example: DiagnosticExample,
    *,
    seed: int,
    selector_artifact: dict[str, Any] | None,
    risk_weights: dict[str, float] | None = None,
) -> list[int] | None:
    query_match = re.fullmatch(r"query_similarity_linked_interval_k(\d+)", method)
    risk_match = re.fullmatch(r"risk_guided_linked_interval_k(\d+)", method)
    learned_match = re.fullmatch(r"learned_linked_interval_k(\d+)", method)
    random_match = re.fullmatch(r"random_linked_interval_k(\d+)_seeded", method)
    if query_match is not None:
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            f"query_similarity_doc_patch_k{query_match.group(1)}",
            example,
            seed=seed,
        )
    elif risk_match is not None:
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            f"risk_guided_doc_patch_k{risk_match.group(1)}",
            example,
            seed=seed,
            risk_weights=risk_weights,
        )
    elif learned_match is not None:
        selected_doc_ids = select_learned_doc_ids(
            f"learned_doc_patch_k{learned_match.group(1)}",
            example,
            selector_artifact,
        )
    elif random_match is not None:
        selected_doc_ids = random_doc_ids_same_count(
            example,
            count=int(random_match.group(1)),
            seed=stable_example_seed(seed, example.id, method),
        )
    else:
        return None
    return _linked_interval_ids_from_selected(example, selected_doc_ids)


def _adaptive_suffix_doc_ids(
    method: str,
    example: DiagnosticExample,
    *,
    seed: int,
    selector_artifact: dict[str, Any] | None,
    risk_weights: dict[str, float] | None = None,
) -> list[int] | None:
    query_match = re.fullmatch(r"query_similarity_adaptive_suffix_t([0-9_]+)_k(\d+)", method)
    risk_match = re.fullmatch(r"risk_guided_adaptive_suffix_t([0-9_]+)_k(\d+)", method)
    learned_match = re.fullmatch(r"learned_adaptive_suffix_t([0-9_]+)_k(\d+)", method)
    random_match = re.fullmatch(r"random_adaptive_suffix_t([0-9_]+)_k(\d+)_seeded", method)
    match = query_match or risk_match or learned_match or random_match
    if match is None:
        return None

    threshold = float(match.group(1).replace("_", "."))
    k = int(match.group(2))
    if query_match is not None:
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            f"query_similarity_doc_patch_k{k}",
            example,
            seed=seed,
        )
    elif risk_match is not None:
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            f"risk_guided_doc_patch_k{k}",
            example,
            seed=seed,
            risk_weights=risk_weights,
        )
    elif learned_match is not None:
        selected_doc_ids = select_learned_doc_ids(
            f"learned_doc_patch_k{k}",
            example,
            selector_artifact,
        )
    else:
        selected_doc_ids = random_doc_ids_same_count(
            example,
            count=k,
            seed=stable_example_seed(seed, example.id, method),
        )
    risk_score, _reason = safe_composition_risk(example)
    if risk_score < threshold:
        return selected_doc_ids
    return _suffix_closure_ids_from_selected(example, selected_doc_ids)


def _selector_downstream_doc_ids(
    method: str,
    example: DiagnosticExample,
    *,
    seed: int,
    selector_artifact: dict[str, Any] | None,
    risk_weights: dict[str, float] | None = None,
) -> list[int] | None:
    oracle_match = re.fullmatch(r"oracle_evidence_doc_downstream_w(\d+)_patch", method)
    if oracle_match is not None:
        selected_doc_ids = list(_oracle_doc_ids_for_example(example))
        return _downstream_window_ids_from_selected(
            example,
            selected_doc_ids,
            window_docs=int(oracle_match.group(1)),
        )

    learned_match = re.fullmatch(r"learned_downstream_w(\d+)_k(\d+)", method)
    if learned_match is not None:
        selected_doc_ids = select_learned_doc_ids(
            f"learned_doc_patch_k{learned_match.group(2)}",
            example,
            selector_artifact,
        )
        return _downstream_window_ids_from_selected(
            example,
            selected_doc_ids,
            window_docs=int(learned_match.group(1)),
        )

    query_match = re.fullmatch(r"query_similarity_downstream_w(\d+)_k(\d+)", method)
    if query_match is not None:
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            f"query_similarity_doc_patch_k{query_match.group(2)}",
            example,
            seed=seed,
        )
        return _downstream_window_ids_from_selected(
            example,
            selected_doc_ids,
            window_docs=int(query_match.group(1)),
        )

    risk_match = re.fullmatch(r"risk_guided_downstream_w(\d+)_k(\d+)", method)
    if risk_match is not None:
        selected_doc_ids, _reason = selected_doc_ids_for_method(
            f"risk_guided_doc_patch_k{risk_match.group(2)}",
            example,
            seed=seed,
            risk_weights=risk_weights,
        )
        return _downstream_window_ids_from_selected(
            example,
            selected_doc_ids,
            window_docs=int(risk_match.group(1)),
        )

    random_match = re.fullmatch(r"random_downstream_w(\d+)_k(\d+)_seeded", method)
    if random_match is None:
        return None
    selected_doc_ids = random_doc_ids_same_count(
        example,
        count=int(random_match.group(2)),
        seed=stable_example_seed(seed, example.id, method),
    )
    return _downstream_window_ids_from_selected(
        example,
        selected_doc_ids,
        window_docs=int(random_match.group(1)),
    )


def _downstream_window_ids_from_selected(
    example: DiagnosticExample,
    selected_doc_ids: list[int],
    *,
    window_docs: int,
) -> list[int]:
    if window_docs <= 0:
        return []
    selected = set(selected_doc_ids)
    if not selected:
        return []
    ordered_ids = [doc.doc_id for doc in example.documents]
    earliest_index = min(index for index, doc_id in enumerate(ordered_ids) if doc_id in selected)
    end = min(len(ordered_ids), earliest_index + window_docs)
    return ordered_ids[earliest_index:end]


def _suffix_closure_ids_from_selected(
    example: DiagnosticExample,
    selected_doc_ids: list[int],
) -> list[int]:
    selected = set(selected_doc_ids)
    if not selected:
        return []
    ordered_ids = [doc.doc_id for doc in example.documents]
    earliest_index = min(index for index, doc_id in enumerate(ordered_ids) if doc_id in selected)
    return ordered_ids[earliest_index:]


def _linked_closure_ids_from_selected(
    example: DiagnosticExample,
    selected_doc_ids: list[int],
) -> list[int]:
    if not selected_doc_ids:
        return []
    selected = set(selected_doc_ids)
    ordered_docs = list(example.documents)
    entities_by_doc = {
        doc.doc_id: extract_entities(f"{doc.title} {doc.text}")
        for doc in ordered_docs
    }
    closure = set(selected)
    active_entities: set[str] = set()
    for doc in ordered_docs:
        if doc.doc_id in selected:
            active_entities.update(entities_by_doc[doc.doc_id])
            continue
        if active_entities and active_entities & entities_by_doc[doc.doc_id]:
            closure.add(doc.doc_id)
            active_entities.update(entities_by_doc[doc.doc_id])
    return [doc.doc_id for doc in ordered_docs if doc.doc_id in closure]


def _linked_interval_ids_from_selected(
    example: DiagnosticExample,
    selected_doc_ids: list[int],
) -> list[int]:
    linked_doc_ids = _linked_closure_ids_from_selected(example, selected_doc_ids)
    if not linked_doc_ids:
        return []
    ordered_ids = [doc.doc_id for doc in example.documents]
    linked = set(linked_doc_ids)
    selected = set(selected_doc_ids)
    start = min(index for index, doc_id in enumerate(ordered_ids) if doc_id in selected)
    end = max(index for index, doc_id in enumerate(ordered_ids) if doc_id in linked) + 1
    return ordered_ids[start:end]


def _oracle_doc_ids_for_example(example: DiagnosticExample) -> set[int]:
    doc_ids = {evidence.doc_id for evidence in example.evidence}
    if example.category == "conflict":
        doc_ids.update(example.conflicting_docs)
    return doc_ids


if __name__ == "__main__":
    main()
