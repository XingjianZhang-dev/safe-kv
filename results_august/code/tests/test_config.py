from pathlib import Path

from safekv.config import load_config, parse_config


def test_parse_config_required_fields() -> None:
    config = parse_config(
        {
            "seed": 21,
            "model": {
                "name": "example/model",
                "dtype": "bfloat16",
                "device": "cpu",
                "trust_remote_code": True,
            },
            "data": {
                "path": "data/example.jsonl",
                "max_examples": 9,
                "max_examples_per_category": 3,
            },
            "generation": {
                "max_new_tokens": 7,
                "do_sample": False,
                "temperature": 0.0,
                "stop_on_newline": True,
                "stop_strings": ["Human:", "Question:"],
                "prefill_mode": "cache_position_only",
            },
            "experiment": {
                "prompt_format": "plain_rag",
                "cache_position_mode": "global",
                "budgets": [0.0, 0.1],
                "methods": ["full_prefill", "naive_global"],
            },
            "prompt": {"boundary_window_tokens": 6, "adaptive_boundary_window": True},
            "risk": {
                "similarity_backend": "tfidf",
                "weights": {"query_similarity": 0.4},
            },
            "recompute": {
                "selection_unit": "span",
                "expand_window_tokens": 4,
                "allow_budget_overshoot": False,
                "max_budget_overshoot_ratio": 0.02,
            },
        }
    )

    assert config.seed == 21
    assert config.model.name == "example/model"
    assert config.model.dtype == "bfloat16"
    assert config.model.device == "cpu"
    assert config.model.trust_remote_code is True
    assert config.data.max_examples == 9
    assert config.data.max_examples_per_category == 3
    assert config.generation.max_new_tokens == 7
    assert config.generation.stop_strings == ["Human:", "Question:"]
    assert config.generation.prefill_mode == "cache_position_only"
    assert config.experiment.prompt_format == "plain_rag"
    assert config.experiment.cache_position_mode == "global"
    assert config.experiment.budgets == [0.0, 0.1]
    assert config.experiment.methods == ["full_prefill", "naive_global"]
    assert config.prompt.boundary_window_tokens == 6
    assert config.prompt.adaptive_boundary_window is True
    assert config.risk.weights == {"query_similarity": 0.4}
    assert config.recompute.expand_window_tokens == 4
    assert config.recompute.allow_budget_overshoot is False


def test_smollm17_configs_parse() -> None:
    root = Path(__file__).resolve().parents[1]
    noisy = load_config(root / "configs" / "v0_smollm17_noisy.yaml")
    external = load_config(root / "configs" / "v0_smollm17_external.yaml")

    assert noisy.model.name == "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    assert external.model.name == "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    assert noisy.experiment.prompt_format == "chat_rag"
    assert external.experiment.prompt_format == "chat_rag"
    assert noisy.data.path == "data/diagnostic_100_noisy.jsonl"
    assert external.data.path == "data/external_multihop_100.jsonl"
    assert noisy.generation.prefill_mode == "manual_position_ids"
