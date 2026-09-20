from types import SimpleNamespace

import pytest

from scripts.run_system_scaling_benchmark import (
    fixed_length_prompt_tokens,
    prepare_results_dir,
    summarize,
)


def test_fixed_length_prompt_tokens_are_deterministic_and_exact_length():
    pack = SimpleNamespace(
        full_input_ids=[1, 2, 3, 4, 8, 9],
        query_token_range=SimpleNamespace(start=4, end=6),
    )
    context, query = fixed_length_prompt_tokens(
        pack, context_length=10, query_tokens=5
    )
    assert context == [1, 2, 3, 4, 1, 2, 3, 4, 1, 2]
    assert query == [8, 9, 8, 9, 8]


def test_scaling_summary_retains_shape_and_throughput():
    rows = [
        {
            "method": "one_shot_full_prefill",
            "context_length": 2048,
            "batch_size": 2,
            "recompute_ratio": 1.0,
            "time_to_first_logit_s": latency,
            "forward_input_tokens": 2080,
            "incremental_peak_cuda_memory_mb": 100.0,
            "max_abs_logit_diff_vs_one_shot_full": 0.0,
        }
        for latency in (1.0, 2.0)
    ]
    summary = summarize(rows)
    assert len(summary) == 1
    assert summary[0]["p50_time_to_first_logit_s"] == pytest.approx(1.5)
    assert summary[0]["mean_completed_prompts_per_s"] == pytest.approx(2 / 1.5)
    assert summary[0]["mean_prompt_tokens_per_s"] == pytest.approx(4160 / 1.5)


def test_prepare_results_dir_accepts_run_registry_files(tmp_path):
    run_dir = tmp_path / "tracked_run"
    run_dir.mkdir()
    for name in ("run_manifest.json", "stdout.log", "stderr.log"):
        (run_dir / name).write_text("", encoding="utf-8")

    prepare_results_dir(run_dir)


@pytest.mark.parametrize("name", ["system_scaling_trace.csv", "unrelated.txt"])
def test_prepare_results_dir_rejects_existing_results_or_unexpected_files(tmp_path, name):
    run_dir = tmp_path / "tracked_run"
    run_dir.mkdir()
    (run_dir / name).write_text("", encoding="utf-8")

    with pytest.raises(FileExistsError):
        prepare_results_dir(run_dir)
