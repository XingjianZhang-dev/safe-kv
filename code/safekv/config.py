"""Configuration loading for SAFE-KV scripts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ModelConfig:
    name: str
    dtype: str = "float32"
    device: str = "cpu"
    trust_remote_code: bool = False


@dataclass(frozen=True)
class DataConfig:
    path: str
    max_examples: int | None = None
    max_examples_per_category: int | None = None


@dataclass(frozen=True)
class GenerationConfig:
    max_new_tokens: int = 16
    do_sample: bool = False
    temperature: float = 0.0
    stop_on_newline: bool = True
    stop_strings: list[str] | None = None
    prefill_mode: str = "prepare_inputs_for_generation"


@dataclass(frozen=True)
class ExperimentConfig:
    prompt_format: str = "plain_rag"
    cache_position_mode: str = "global"
    budgets: list[float] | None = None
    methods: list[str] | None = None


@dataclass(frozen=True)
class PromptConfig:
    boundary_window_tokens: int = 8
    adaptive_boundary_window: bool = True


@dataclass(frozen=True)
class RiskConfig:
    similarity_backend: str = "tfidf"
    weights: dict[str, float] | None = None


@dataclass(frozen=True)
class RecomputeConfig:
    selection_unit: str = "span"
    expand_window_tokens: int = 0
    allow_budget_overshoot: bool = True
    max_budget_overshoot_ratio: float = 0.0


@dataclass(frozen=True)
class SafeKVConfig:
    seed: int
    model: ModelConfig
    data: DataConfig
    generation: GenerationConfig
    experiment: ExperimentConfig
    prompt: PromptConfig
    risk: RiskConfig
    recompute: RecomputeConfig


def load_config(path: str | Path) -> SafeKVConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ValueError(f"config must be a mapping: {config_path}")
    return parse_config(raw)


def parse_config(raw: dict[str, Any]) -> SafeKVConfig:
    model_raw = _required_mapping(raw, "model")
    data_raw = _required_mapping(raw, "data")
    generation_raw = raw.get("generation", {})
    experiment_raw = raw.get("experiment", {})
    prompt_raw = raw.get("prompt", {})
    risk_raw = raw.get("risk", {})
    recompute_raw = raw.get("recompute", {})

    if "name" not in model_raw:
        raise ValueError("config.model.name is required")
    if "path" not in data_raw:
        raise ValueError("config.data.path is required")

    max_examples = data_raw.get("max_examples")
    if max_examples is not None:
        max_examples = int(max_examples)
    max_examples_per_category = data_raw.get("max_examples_per_category")
    if max_examples_per_category is not None:
        max_examples_per_category = int(max_examples_per_category)

    return SafeKVConfig(
        seed=int(raw.get("seed", 13)),
        model=ModelConfig(
            name=str(model_raw["name"]),
            dtype=str(model_raw.get("dtype", "float32")).lower(),
            device=str(model_raw.get("device", "cpu")).lower(),
            trust_remote_code=bool(model_raw.get("trust_remote_code", False)),
        ),
        data=DataConfig(
            path=str(data_raw["path"]),
            max_examples=max_examples,
            max_examples_per_category=max_examples_per_category,
        ),
        generation=GenerationConfig(
            max_new_tokens=int(generation_raw.get("max_new_tokens", 16)),
            do_sample=bool(generation_raw.get("do_sample", False)),
            temperature=float(generation_raw.get("temperature", 0.0)),
            stop_on_newline=bool(generation_raw.get("stop_on_newline", True)),
            stop_strings=_parse_stop_strings(generation_raw.get("stop_strings")),
            prefill_mode=str(
                generation_raw.get("prefill_mode", "prepare_inputs_for_generation")
            ),
        ),
        experiment=ExperimentConfig(
            prompt_format=str(experiment_raw.get("prompt_format", "plain_rag")),
            cache_position_mode=str(
                experiment_raw.get("cache_position_mode", "global")
            ),
            budgets=_parse_float_list(experiment_raw.get("budgets")),
            methods=_parse_string_list(experiment_raw.get("methods")),
        ),
        prompt=PromptConfig(
            boundary_window_tokens=int(prompt_raw.get("boundary_window_tokens", 8)),
            adaptive_boundary_window=bool(prompt_raw.get("adaptive_boundary_window", True)),
        ),
        risk=RiskConfig(
            similarity_backend=str(risk_raw.get("similarity_backend", "tfidf")),
            weights=_parse_float_dict(risk_raw.get("weights")),
        ),
        recompute=RecomputeConfig(
            selection_unit=str(recompute_raw.get("selection_unit", "span")),
            expand_window_tokens=int(recompute_raw.get("expand_window_tokens", 0)),
            allow_budget_overshoot=bool(
                recompute_raw.get("allow_budget_overshoot", True)
            ),
            max_budget_overshoot_ratio=float(
                recompute_raw.get("max_budget_overshoot_ratio", 0.0)
            ),
        ),
    )


def _required_mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"config.{key} must be a mapping")
    return value


def _parse_stop_strings(value: Any) -> list[str]:
    if value is None:
        return list(DEFAULT_STOP_STRINGS)
    if not isinstance(value, list):
        raise ValueError("generation.stop_strings must be a list of strings")
    return [str(item) for item in value]
DEFAULT_STOP_STRINGS = ["Human:", "[Document", "Question:", "Answer:"]


def _parse_float_list(value: Any) -> list[float] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError("expected a list of floats")
    return [float(item) for item in value]


def _parse_string_list(value: Any) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError("expected a list of strings")
    return [str(item) for item in value]


def _parse_float_dict(value: Any) -> dict[str, float] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("expected a mapping of float weights")
    return {str(key): float(weight) for key, weight in value.items()}
