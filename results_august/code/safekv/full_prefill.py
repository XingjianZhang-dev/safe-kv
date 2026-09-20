"""Full-prefill reference inference for SAFE-KV Milestone 2."""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from safekv.build_diagnostic import CATEGORIES
from safekv.build_diagnostic import read_jsonl
from safekv.config import SafeKVConfig
from safekv.data_schema import DiagnosticExample, PromptPack, TokenRange
from safekv.generation import (
    compute_task_metrics,
    should_stop_generated_text,
    topk_from_logits,
    trim_generated_answer,
)
from safekv.modeling import LoadedModel
from safekv.prompting import build_rag_prompt

GENERATION_MODES = (
    "manual_position_ids",
    "cache_position_only",
    "prepare_inputs_for_generation",
)


@dataclass(frozen=True)
class GreedyGenerationResult:
    token_ids: list[int]
    step_logits: list[Any]
    mode: str


def set_deterministic_seed(seed: int) -> None:
    random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        return


def load_examples_for_config(config: SafeKVConfig, config_dir: Path) -> list[DiagnosticExample]:
    data_path = Path(config.data.path)
    if not data_path.is_absolute():
        data_path = config_dir / data_path
    examples = read_jsonl(data_path)
    if config.data.max_examples_per_category is not None:
        examples = select_examples_per_category(
            examples,
            max_examples_per_category=config.data.max_examples_per_category,
        )
    if config.data.max_examples is not None:
        examples = examples[: config.data.max_examples]
    return examples


def select_examples_per_category(
    examples: list[DiagnosticExample], max_examples_per_category: int
) -> list[DiagnosticExample]:
    if max_examples_per_category <= 0:
        raise ValueError("max_examples_per_category must be positive")

    counts: defaultdict[str, int] = defaultdict(int)
    selected: list[DiagnosticExample] = []
    for example in examples:
        if counts[example.category] >= max_examples_per_category:
            continue
        selected.append(example)
        counts[example.category] += 1
    return selected


def select_generation_sanity_examples(
    examples: list[DiagnosticExample],
    examples_per_category: int = 1,
) -> list[DiagnosticExample]:
    selected = select_examples_per_category(
        examples,
        max_examples_per_category=examples_per_category,
    )
    seen = {example.category for example in selected}
    missing = [category for category in CATEGORIES if category not in seen]
    if missing:
        raise ValueError(f"generation sanity selection missing categories: {missing}")
    return selected


def run_full_prefill_dataset(
    config: SafeKVConfig,
    loaded: LoadedModel,
    examples: list[DiagnosticExample],
    out_dir: str | Path,
    config_path: str | Path,
) -> dict[str, Any]:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    outputs_path = out_path / "full_prefill_outputs.jsonl"
    summary_path = out_path / "full_prefill_summary.json"
    logits_dir = out_path / "logits" / "full_prefill"
    prompt_packs_dir = out_path / "prompt_packs"
    logits_dir.mkdir(parents=True, exist_ok=True)
    prompt_packs_dir.mkdir(parents=True, exist_ok=True)
    logits_dtype = logits_storage_dtype(config.model.dtype)

    prompt_lengths: list[int] = []
    category_counts: Counter[str] = Counter()
    rows_written = 0
    with outputs_path.open("w", encoding="utf-8") as handle:
        for example in examples:
            pack = build_rag_prompt(
                example,
                loaded.tokenizer,
                prompt_format=config.experiment.prompt_format,
                boundary_window_tokens=config.prompt.boundary_window_tokens,
                adaptive_boundary_window=config.prompt.adaptive_boundary_window,
            )
            logits_path = logits_dir / f"{example.id}.pt"
            prompt_pack_path = prompt_packs_dir / f"{example.id}.json"
            row = run_full_prefill_example(
                example=example,
                pack=pack,
                loaded=loaded,
                max_new_tokens=config.generation.max_new_tokens,
                stop_on_newline=config.generation.stop_on_newline,
                stop_strings=config.generation.stop_strings,
                generation_mode=config.generation.prefill_mode,
                logits_path=logits_path,
                logits_dtype=logits_dtype,
                prompt_pack_path=prompt_pack_path,
            )
            validate_full_prefill_output_row(row)
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            prompt_lengths.append(len(pack.full_input_ids))
            category_counts[example.category] += 1
            rows_written += 1

    avg_prompt_length = (
        sum(prompt_lengths) / len(prompt_lengths) if prompt_lengths else 0.0
    )
    summary = {
        "config_path": str(config_path),
        "model_name": config.model.name,
        "requested_device": config.model.device,
        "actual_device": loaded.device,
        "torch_dtype": loaded.torch_dtype_name,
        "warnings": loaded.warnings,
        "num_examples": rows_written,
        "category_counts": dict(sorted(category_counts.items())),
        "average_prompt_length": avg_prompt_length,
        "max_prompt_length": max(prompt_lengths) if prompt_lengths else 0,
        "min_prompt_length": min(prompt_lengths) if prompt_lengths else 0,
        "logits_dir": str(logits_dir),
        "logits_dtype": logits_dtype,
        "prompt_format": config.experiment.prompt_format,
        "boundary_window_tokens": config.prompt.boundary_window_tokens,
        "adaptive_boundary_window": config.prompt.adaptive_boundary_window,
        "stop_on_newline": config.generation.stop_on_newline,
        "stop_strings": list(config.generation.stop_strings or []),
        "prefill_generation_mode": config.generation.prefill_mode,
        "prompt_packs_dir": str(prompt_packs_dir),
        "outputs_path": str(outputs_path),
        "summary_path": str(summary_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def run_full_prefill_example(
    example: DiagnosticExample,
    pack: PromptPack,
    loaded: LoadedModel,
    max_new_tokens: int,
    stop_on_newline: bool,
    stop_strings: list[str] | None,
    generation_mode: str,
    logits_path: Path,
    logits_dtype: str,
    prompt_pack_path: Path,
) -> dict[str, Any]:
    import torch

    if max_new_tokens <= 0:
        raise ValueError("max_new_tokens must be positive")

    input_ids = torch.tensor([pack.full_input_ids], dtype=torch.long, device=loaded.device)
    attention_mask = torch.ones_like(input_ids, device=loaded.device)
    position_ids = torch.arange(input_ids.shape[1], dtype=torch.long, device=loaded.device).unsqueeze(0)

    with torch.no_grad():
        outputs = loaded.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            use_cache=True,
        )
        first_answer_logits = outputs.logits[:, -1, :].detach().float().cpu()[0]
        save_logits(first_answer_logits, logits_path, logits_dtype)
        write_prompt_pack_metadata(pack, prompt_pack_path)
        top10 = topk_from_logits(first_answer_logits, loaded.tokenizer, k=10)
        generated_token_ids = greedy_generate_from_prefill(
            model=loaded.model,
            tokenizer=loaded.tokenizer,
            prompt_outputs=outputs,
            first_logits=outputs.logits,
            prompt_length=input_ids.shape[1],
            max_new_tokens=max_new_tokens,
            stop_on_newline=stop_on_newline,
            stop_strings=stop_strings,
            device=loaded.device,
            mode=generation_mode,
        )

    generated_answer = loaded.tokenizer.decode(
        generated_token_ids,
        skip_special_tokens=True,
    ).strip()
    generated_answer = trim_generated_answer(
        generated_answer,
        stop_on_newline=stop_on_newline,
        stop_strings=stop_strings,
    )

    row = {
        "example_id": example.id,
        "id": example.id,
        "category": example.category,
        "gold_answer": example.gold_answer,
        "full_text": pack.full_text,
        "prompt_token_counts": {
            "full": len(pack.full_input_ids),
            "context": len(pack.context_input_ids),
            "query": len(pack.query_input_ids),
        },
        "context_token_range": _range_to_dict(pack.context_token_range),
        "query_token_range": _range_to_dict(pack.query_token_range),
        "logits_path": str(logits_path),
        "logits_dtype": logits_dtype,
        "logits_shape": list(first_answer_logits.shape),
        "prompt_pack_path": str(prompt_pack_path),
        "top10_next_tokens": top10,
        "generated_token_ids": [int(token_id) for token_id in generated_token_ids],
        "generated_answer": generated_answer,
        "stop_on_newline": stop_on_newline,
        "stop_strings": list(stop_strings or []),
        "prefill_generation_mode": generation_mode,
        "task_metrics": compute_task_metrics(generated_answer, example.gold_answer),
    }
    return row


def logits_storage_dtype(requested_dtype: str) -> str:
    return "float32" if requested_dtype.lower() in {"float32", "fp32", "single"} else "float16"


def save_logits(logits: Any, path: Path, dtype_name: str) -> None:
    import torch

    if dtype_name == "float32":
        dtype = torch.float32
    elif dtype_name == "float16":
        dtype = torch.float16
    else:
        raise ValueError(f"unsupported logits storage dtype {dtype_name!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(logits.to(dtype), path)


def write_prompt_pack_metadata(pack: PromptPack, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(prompt_pack_metadata(pack), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def prompt_pack_metadata(pack: PromptPack) -> dict[str, Any]:
    return {
        "example_id": pack.example_id,
        "prompt_format": pack.prompt_format,
        "full_text": pack.full_text,
        "context_text": pack.context_text,
        "query_text": pack.query_text,
        "full_input_ids": pack.full_input_ids,
        "context_input_ids": pack.context_input_ids,
        "query_input_ids": pack.query_input_ids,
        "offset_mapping": [list(offset) for offset in pack.offset_mapping],
        "prompt_token_counts": {
            "full": len(pack.full_input_ids),
            "context": len(pack.context_input_ids),
            "query": len(pack.query_input_ids),
        },
        "context_token_range": _range_to_dict(pack.context_token_range),
        "query_token_range": _range_to_dict(pack.query_token_range),
        "doc_ranges": [_range_to_dict(token_range) for token_range in pack.doc_ranges],
        "doc_text_ranges": [_range_to_dict(token_range) for token_range in pack.doc_text_ranges],
        "doc_char_ranges": [
            {
                "doc_id": doc.doc_id,
                "prompt_doc_index": doc.prompt_doc_index,
                "title": doc.title,
                "block_char_range": _char_range_to_dict(doc.block_char_range),
                "text_char_range": _char_range_to_dict(doc.text_char_range),
            }
            for doc in pack.doc_char_ranges
        ],
        "span_ranges": [
            {
                "span_id": span.span_id,
                "doc_id": span.doc_id,
                "text": span.text,
                "token_range": _range_to_dict(span.token_range),
                "prompt_char_range": _char_range_to_dict(span.prompt_char_range),
                "char_range_in_doc": list(span.char_range_in_doc)
                if span.char_range_in_doc is not None
                else None,
                "role": span.role,
                "retrieval_score": span.retrieval_score,
                "token_distance_to_doc_start": span.token_distance_to_doc_start,
                "token_distance_to_doc_end": span.token_distance_to_doc_end,
                "boundary_token_overlap_ratio": span.boundary_token_overlap_ratio,
                "effective_boundary_window_tokens": span.effective_boundary_window_tokens,
                "contains_gold_evidence": span.contains_gold_evidence,
            }
            for span in pack.span_ranges
        ],
        "evidence_span_ids": list(pack.evidence_span_ids),
        "conflict_doc_ids": list(pack.conflict_doc_ids),
        "offset_mapping_source": pack.offset_mapping_source,
        "boundary_window_tokens": pack.boundary_window_tokens,
    }


def greedy_generate_from_prefill(
    model: Any,
    tokenizer: Any,
    prompt_outputs: Any,
    first_logits: Any,
    prompt_length: int,
    max_new_tokens: int,
    stop_on_newline: bool,
    stop_strings: list[str] | None,
    device: str,
    mode: str = "prepare_inputs_for_generation",
) -> list[int]:
    return greedy_generate_from_prefill_result(
        model=model,
        tokenizer=tokenizer,
        prompt_outputs=prompt_outputs,
        first_logits=first_logits,
        prompt_length=prompt_length,
        max_new_tokens=max_new_tokens,
        stop_on_newline=stop_on_newline,
        stop_strings=stop_strings,
        device=device,
        mode=mode,
    ).token_ids


def greedy_generate_from_prefill_result(
    model: Any,
    tokenizer: Any,
    prompt_outputs: Any,
    first_logits: Any,
    prompt_length: int,
    max_new_tokens: int,
    stop_on_newline: bool,
    stop_strings: list[str] | None,
    device: str,
    mode: str = "prepare_inputs_for_generation",
) -> GreedyGenerationResult:
    import torch

    if mode not in GENERATION_MODES:
        raise ValueError(f"unsupported generation mode {mode!r}")

    eos_ids = _eos_token_ids(tokenizer, model)
    past_key_values = prompt_outputs.past_key_values
    logits = first_logits
    generated: list[int] = []
    step_logits: list[Any] = []
    running_input_ids: Any | None = None
    attention_mask = torch.ones((1, prompt_length), dtype=torch.long, device=device)

    for step in range(max_new_tokens):
        step_logits.append(logits[:, -1, :].detach().float().cpu()[0])
        next_id = int(torch.argmax(logits[:, -1, :], dim=-1).item())
        generated.append(next_id)
        decoded = tokenizer.decode(generated, skip_special_tokens=True)
        if next_id in eos_ids:
            break
        if should_stop_generated_text(
            decoded,
            stop_on_newline=stop_on_newline,
            stop_strings=stop_strings,
        ):
            break

        next_input_ids = torch.tensor([[next_id]], dtype=torch.long, device=device)
        attention_mask = torch.cat(
            [attention_mask, torch.ones((1, 1), dtype=torch.long, device=device)],
            dim=1,
        )
        total_length = attention_mask.shape[1]
        running_input_ids = (
            next_input_ids
            if running_input_ids is None
            else torch.cat([running_input_ids, next_input_ids], dim=1)
        )
        model_kwargs = build_generation_step_kwargs(
            model=model,
            mode=mode,
            next_input_ids=next_input_ids,
            generated_input_ids=running_input_ids,
            attention_mask=attention_mask,
            past_key_values=past_key_values,
            position_index=total_length - 1,
            device=device,
        )
        outputs = model(**model_kwargs)
        past_key_values = outputs.past_key_values
        logits = outputs.logits

    return GreedyGenerationResult(token_ids=generated, step_logits=step_logits, mode=mode)


def build_generation_step_kwargs(
    model: Any,
    mode: str,
    next_input_ids: Any,
    generated_input_ids: Any,
    attention_mask: Any,
    past_key_values: Any,
    position_index: int,
    device: str,
) -> dict[str, Any]:
    import torch

    if mode == "manual_position_ids":
        return {
            "input_ids": next_input_ids,
            "attention_mask": attention_mask,
            "position_ids": torch.tensor([[position_index]], dtype=torch.long, device=device),
            "past_key_values": past_key_values,
            "use_cache": True,
        }
    if mode == "cache_position_only":
        return {
            "input_ids": next_input_ids,
            "attention_mask": attention_mask,
            "past_key_values": past_key_values,
            "use_cache": True,
            "cache_position": torch.tensor([position_index], dtype=torch.long, device=device),
        }
    if mode == "prepare_inputs_for_generation":
        prepare = getattr(model, "prepare_inputs_for_generation", None)
        if prepare is None:
            return build_generation_step_kwargs(
                model=model,
                mode="manual_position_ids",
                next_input_ids=next_input_ids,
                generated_input_ids=generated_input_ids,
                attention_mask=attention_mask,
                past_key_values=past_key_values,
                position_index=position_index,
                device=device,
            )
        return prepare(
            generated_input_ids,
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            cache_position=torch.tensor([position_index], dtype=torch.long, device=device),
            use_cache=True,
        )
    raise ValueError(f"unsupported generation mode {mode!r}")


def validate_full_prefill_output_row(row: dict[str, Any]) -> None:
    required_keys = {
        "example_id",
        "category",
        "gold_answer",
        "full_text",
        "prompt_token_counts",
        "context_token_range",
        "query_token_range",
        "logits_path",
        "logits_dtype",
        "logits_shape",
        "prompt_pack_path",
        "top10_next_tokens",
        "generated_answer",
        "task_metrics",
    }
    missing = required_keys - set(row)
    if missing:
        raise ValueError(f"full-prefill output row missing keys: {sorted(missing)}")
    if row["logits_dtype"] not in {"float16", "float32"}:
        raise ValueError("logits_dtype must be float16 or float32")
    if not isinstance(row["logits_shape"], list) or len(row["logits_shape"]) != 1:
        raise ValueError("logits_shape must be a one-dimensional shape list")
    if len(row["top10_next_tokens"]) > 10:
        raise ValueError("top10_next_tokens cannot contain more than 10 entries")
    for token in row["top10_next_tokens"]:
        for key in ("token_id", "token", "logit"):
            if key not in token:
                raise ValueError(f"top10 token row missing {key!r}")
    for range_key in ("context_token_range", "query_token_range"):
        token_range = row[range_key]
        if set(token_range) != {"start", "end"}:
            raise ValueError(f"{range_key} must contain start and end")
        if token_range["end"] < token_range["start"]:
            raise ValueError(f"{range_key} end must be >= start")


def _range_to_dict(token_range: TokenRange) -> dict[str, int]:
    return {"start": token_range.start, "end": token_range.end}


def _char_range_to_dict(char_range: Any) -> dict[str, int]:
    return {"start": int(char_range.start), "end": int(char_range.end)}


def _eos_token_ids(tokenizer: Any, model: Any | None = None) -> set[int]:
    eos_values: list[Any] = []
    if model is not None:
        generation_config = getattr(model, "generation_config", None)
        if generation_config is not None:
            eos_values.append(getattr(generation_config, "eos_token_id", None))
    eos_values.append(getattr(tokenizer, "eos_token_id", None))
    ids: set[int] = set()
    for eos in eos_values:
        if eos is None:
            continue
        if isinstance(eos, list):
            ids.update(int(token_id) for token_id in eos)
        else:
            ids.add(int(eos))
    return ids
