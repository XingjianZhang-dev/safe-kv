from types import SimpleNamespace

import pytest
import torch

from safekv.build_diagnostic import build_diagnostic_examples
from safekv.cache_ops import cache_seq_len
from safekv.data_schema import TokenRange
from scripts import run_answer_eval
from safekv_ipm.frontier_selector import FRONTIER_FEATURE_NAMES


def make_cache(length: int):
    key = torch.zeros((1, 1, length, 2), dtype=torch.float32)
    value = torch.zeros_like(key)
    return ((key, value),)


class RecordingCacheModel:
    def __init__(self):
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        past = kwargs.get("past_key_values")
        past_length = cache_seq_len(past) if past is not None else 0
        input_length = int(kwargs["input_ids"].shape[1])
        total_length = past_length + input_length
        key = torch.zeros((1, 1, total_length, 2), dtype=torch.float32)
        value = torch.zeros_like(key)
        logits = torch.zeros((1, 1, 13), dtype=torch.float32)
        return SimpleNamespace(logits=logits, past_key_values=((key, value),))


def make_suffix_pack():
    return SimpleNamespace(
        full_input_ids=list(range(7)),
        doc_ranges=[TokenRange(2, 4), TokenRange(4, 5)],
        query_token_range=TokenRange(5, 7),
    )


@pytest.mark.parametrize(
    ("ranges", "message"),
    [
        ([TokenRange(2, 3), TokenRange(4, 5)], "gap-free"),
        ([TokenRange(2, 4)], "query boundary"),
        ([TokenRange(1, 5)], "document tokens"),
    ],
)
def test_actual_recompute_rejects_non_suffix_contracts(ranges, message):
    with pytest.raises(ValueError, match=message):
        run_answer_eval.recompute_answer_suffix(
            pack=make_suffix_pack(),
            loaded=SimpleNamespace(device="cpu", model=RecordingCacheModel()),
            base_cache=make_cache(5),
            patch_ranges=ranges,
        )


def test_actual_recompute_accepts_adjacent_document_ranges_as_one_suffix():
    model = RecordingCacheModel()
    repaired = run_answer_eval.recompute_answer_suffix(
        pack=make_suffix_pack(),
        loaded=SimpleNamespace(device="cpu", model=model),
        base_cache=make_cache(5),
        patch_ranges=[TokenRange(2, 4), TokenRange(4, 5)],
    )

    assert len(model.calls) == 1
    assert model.calls[0]["input_ids"].tolist() == [[2, 3, 4]]
    assert model.calls[0]["position_ids"].tolist() == [[2, 3, 4]]
    assert cache_seq_len(model.calls[0]["past_key_values"]) == 2
    assert cache_seq_len(repaired) == 5


def test_actual_local_recompute_replaces_only_selected_range():
    base_cache = make_cache(5)
    base_cache[0][0].fill_(7.0)
    base_cache[0][1].fill_(7.0)
    model = RecordingCacheModel()

    repaired = run_answer_eval.recompute_answer_ranges_locally(
        pack=make_suffix_pack(),
        loaded=SimpleNamespace(device="cpu", model=model),
        base_cache=base_cache,
        patch_ranges=[TokenRange(2, 4)],
    )

    assert len(model.calls) == 1
    assert model.calls[0]["input_ids"].tolist() == [[2, 3]]
    assert model.calls[0]["position_ids"].tolist() == [[2, 3]]
    assert cache_seq_len(repaired) == 5
    assert torch.all(repaired[0][0][:, :, :2, :] == 7.0)
    assert torch.all(repaired[0][0][:, :, 2:4, :] == 0.0)
    assert torch.all(repaired[0][0][:, :, 4:, :] == 7.0)


def test_actual_local_recompute_rejects_overlapping_ranges():
    with pytest.raises(ValueError, match="must not overlap"):
        run_answer_eval.recompute_answer_ranges_locally(
            pack=make_suffix_pack(),
            loaded=SimpleNamespace(device="cpu", model=RecordingCacheModel()),
            base_cache=make_cache(5),
            patch_ranges=[TokenRange(2, 4), TokenRange(3, 5)],
        )


def test_full_prefill_freezes_prompt_donor_before_generation_mutates_cache(monkeypatch):
    model = RecordingCacheModel()
    loaded = SimpleNamespace(
        model=model,
        device="cpu",
        tokenizer=SimpleNamespace(decode=lambda *_args, **_kwargs: "answer"),
    )
    pack = SimpleNamespace(full_input_ids=list(range(5)))
    config = SimpleNamespace(
        generation=SimpleNamespace(
            max_new_tokens=1,
            stop_on_newline=False,
            stop_strings=[],
        )
    )

    def mutate_prompt_cache(**kwargs):
        prompt_outputs = kwargs["prompt_outputs"]
        prompt_outputs.past_key_values[0][0].fill_(9.0)
        prompt_outputs.past_key_values[0][1].fill_(9.0)
        return [1]

    monkeypatch.setattr(
        run_answer_eval,
        "greedy_generate_from_prefill",
        mutate_prompt_cache,
    )
    state = run_answer_eval.run_full_prefill_answer_state(
        example=None,
        pack=pack,
        loaded=loaded,
        config=config,
    )

    assert cache_seq_len(state["full_cache"]) == 5
    assert torch.count_nonzero(state["full_cache"][0][0]).item() == 0
    assert torch.count_nonzero(state["full_cache"][0][1]).item() == 0


def test_exact_prefix_reuse_runs_query_from_full_context_cache(monkeypatch):
    model = RecordingCacheModel()
    tokenizer = SimpleNamespace(
        decode=lambda *_args, **_kwargs: "answer",
    )
    loaded = SimpleNamespace(model=model, device="cpu", tokenizer=tokenizer)
    pack = make_suffix_pack()
    config = SimpleNamespace(
        generation=SimpleNamespace(
            max_new_tokens=1,
            stop_on_newline=False,
            stop_strings=[],
        )
    )
    monkeypatch.setattr(
        run_answer_eval,
        "greedy_generate_from_prefill",
        lambda **_kwargs: [1],
    )
    full_state = {
        "first_logits": torch.zeros(13),
        "generated_token_ids": [1],
        "generated_answer": "answer",
        "full_cache": make_cache(7),
    }
    example = SimpleNamespace(
        id="exact-prefix",
        category="control",
        gold_answer="answer",
    )

    row = run_answer_eval.run_method_answer_row(
        method="exact_prefix_reuse",
        example=example,
        pack=pack,
        loaded=loaded,
        config=config,
        full_state=full_state,
        base_state=None,
        full_cache=full_state["full_cache"],
        random_seed=0,
        selector_artifact=None,
    )

    assert cache_seq_len(model.calls[0]["past_key_values"]) == 5
    assert model.calls[0]["input_ids"].tolist() == [[5, 6]]
    assert row["method"] == "exact_prefix_reuse"
    assert row["cache_control"] == "exact_prefix"
    assert row["answer_equivalence_to_full_prefill"] is True
    assert row["patched_token_ratio"] == 0.0
    assert row["online_context_prefill_fraction"] == 0.0
    assert row["online_context_prefill_token_count"] == 0
    assert row["context_token_count"] == 5


def test_full_prefill_row_records_full_online_context_compute():
    row = run_answer_eval.full_prefill_answer_row(
        SimpleNamespace(id="full", category="control", gold_answer="answer"),
        make_suffix_pack(),
        {
            "generated_token_ids": [1],
            "generated_answer": "answer",
        },
    )

    assert row["patched_token_ratio"] == 0.0
    assert row["online_context_prefill_fraction"] == 1.0
    assert row["online_context_prefill_token_count"] == row["context_token_count"]


def test_random_controls_accept_explicit_and_inherited_seeds():
    assert run_answer_eval._seeded_random_doc_patch_k(
        "random_doc_patch_k2_seeded"
    ) == (2, None)
    assert run_answer_eval._seeded_random_doc_patch_k(
        "random_doc_patch_k2_seed29"
    ) == (2, 29)
    assert run_answer_eval._seeded_random_suffix_closure_k(
        "random_suffix_closure_k1_seed47"
    ) == (1, 47)
    assert run_answer_eval._seeded_random_suffix_closure_k(
        "random_suffix_closure_k1_seedx"
    ) is None


def make_snapshot_tree(tmp_path):
    code_root = tmp_path / "code"
    (code_root / "scripts").mkdir(parents=True)
    (code_root / "safekv").mkdir()
    runner = code_root / "scripts" / "run_answer_eval.py"
    implementation = code_root / "safekv" / "module.py"
    config = tmp_path / "config.yaml"
    data = tmp_path / "data.jsonl"
    selector = tmp_path / "selector.json"
    runner.write_text("# runner\n", encoding="utf-8")
    implementation.write_text("VALUE = 1\n", encoding="utf-8")
    config.write_text("seed: 13\n", encoding="utf-8")
    data.write_text('{"id":"example"}\n', encoding="utf-8")
    selector.write_text('{"selector":"fixed"}\n', encoding="utf-8")
    snapshot = run_answer_eval.capture_answer_execution_snapshot(
        config_path=config,
        data_path=data,
        selector_path=selector,
        code_root=code_root,
    )
    return code_root, config, data, selector, snapshot


def assert_snapshot_rejected(code_root, config, data, selector, snapshot):
    with pytest.raises(RuntimeError, match="changed at test"):
        run_answer_eval.assert_answer_execution_snapshot_unchanged(
            snapshot,
            config_path=config,
            data_path=data,
            selector_path=selector,
            stage="test",
            code_root=code_root,
        )


@pytest.mark.parametrize("target", ["config", "data", "selector", "implementation"])
def test_answer_execution_snapshot_rejects_modified_inputs(tmp_path, target):
    code_root, config, data, selector, snapshot = make_snapshot_tree(tmp_path)
    paths = {
        "config": config,
        "data": data,
        "selector": selector,
        "implementation": code_root / "safekv" / "module.py",
    }
    paths[target].write_text("changed\n", encoding="utf-8")
    assert_snapshot_rejected(code_root, config, data, selector, snapshot)


def test_answer_execution_snapshot_rejects_added_or_removed_python(tmp_path):
    code_root, config, data, selector, snapshot = make_snapshot_tree(tmp_path)
    added = code_root / "safekv" / "added.py"
    added.write_text("VALUE = 2\n", encoding="utf-8")
    assert_snapshot_rejected(code_root, config, data, selector, snapshot)

    added.unlink()
    (code_root / "safekv" / "module.py").unlink()
    assert_snapshot_rejected(code_root, config, data, selector, snapshot)


def test_invalidated_answer_directory_cannot_be_reused(tmp_path):
    (tmp_path / "INVALID_PROVENANCE_DRIFT.json").write_text(
        '{}\n', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="permanently invalidated"):
        run_answer_eval.assert_results_dir_not_invalidated(tmp_path)


def test_answer_runner_requires_fixed_python_hash_seed(monkeypatch):
    monkeypatch.delenv("PYTHONHASHSEED", raising=False)
    with pytest.raises(ValueError, match="PYTHONHASHSEED=0"):
        run_answer_eval.require_fixed_python_hash_seed()
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    run_answer_eval.require_fixed_python_hash_seed()


def test_answer_runner_uses_configured_methods_unless_cli_overrides():
    assert run_answer_eval.resolve_methods(None, ["configured"]) == ["configured"]
    assert run_answer_eval.resolve_methods("cli_a,cli_b", ["configured"]) == [
        "cli_a",
        "cli_b",
    ]
    with pytest.raises(ValueError, match="duplicates"):
        run_answer_eval.resolve_methods(None, ["same", "same"])


def test_suffix_selector_executes_supplied_risk_weights():
    example = next(
        item
        for item in build_diagnostic_examples(n_per_category=1, seed=13)
        if item.category == "distractor_heavy"
    )
    cross_document_only = {
        "retrieval_score": 0.0,
        "query_similarity": 0.0,
        "entity_overlap": 0.0,
        "conflict_indicator": 0.0,
        "cross_doc_shared_entity": 1.0,
    }

    default_ids = run_answer_eval._selector_suffix_closure_doc_ids(
        "risk_guided_suffix_closure_k1",
        example,
        seed=13,
        selector_artifact=None,
    )
    weighted_ids = run_answer_eval._selector_suffix_closure_doc_ids(
        "risk_guided_suffix_closure_k1",
        example,
        seed=13,
        selector_artifact=None,
        risk_weights=cross_document_only,
    )

    assert default_ids == [1, 2, 3, 4, 5]
    assert weighted_ids == [4, 5]


def frontier_artifact(*, intercept: float, threshold: float) -> dict:
    size = len(FRONTIER_FEATURE_NAMES)
    return {
        "type": "linear_logistic_executable_suffix_frontier_selector",
        "feature_contract": {"names": list(FRONTIER_FEATURE_NAMES)},
        "model": {
            "means": [0.0] * size,
            "scales": [1.0] * size,
            "coefficients": [0.0] * size,
            "intercept": intercept,
        },
        "threshold": threshold,
        "integrity": {"test_set_used": False},
    }


def test_frozen_frontier_selector_executes_latest_safe_or_full_fallback():
    example = next(iter(build_diagnostic_examples(n_per_category=1, seed=13)))
    ranges = []
    cursor = 2
    for _doc in example.documents:
        ranges.append(TokenRange(cursor, cursor + 2))
        cursor += 2
    pack = SimpleNamespace(
        full_input_ids=list(range(cursor + 2)),
        doc_ranges=ranges,
        query_token_range=TokenRange(cursor, cursor + 2),
    )

    no_repair = frontier_artifact(intercept=-20.0, threshold=0.5)
    selected_ranges, selected_ids, metadata = run_answer_eval.frozen_frontier_patch_ranges(
        example=example,
        pack=pack,
        artifact=no_repair,
    )
    assert selected_ranges == []
    assert selected_ids == []
    assert metadata["frontier_selected_start"] == len(example.documents)
    assert metadata["frontier_full_prefill_fallback"] is False

    fallback = frontier_artifact(intercept=20.0, threshold=0.5)
    selected_ranges, selected_ids, metadata = run_answer_eval.frozen_frontier_patch_ranges(
        example=example,
        pack=pack,
        artifact=fallback,
    )
    assert selected_ranges == ranges
    assert selected_ids == [doc.doc_id for doc in example.documents]
    assert metadata["frontier_selected_start"] is None
    assert metadata["frontier_full_prefill_fallback"] is True


def test_frontier_artifact_loader_rejects_test_fitted_artifact(tmp_path):
    path = tmp_path / "frontier.json"
    value = frontier_artifact(intercept=0.0, threshold=0.5)
    path.write_text(__import__("json").dumps(value), encoding="utf-8")
    assert run_answer_eval.load_frontier_selector_artifact(path) == value
    value["integrity"]["test_set_used"] = True
    path.write_text(__import__("json").dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="calibration-only"):
        run_answer_eval.load_frontier_selector_artifact(path)
