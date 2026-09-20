from types import SimpleNamespace

import pytest
import torch

from safekv.cache_ops import cache_seq_len
from safekv.data_schema import TokenRange
from scripts import run_answer_eval


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
