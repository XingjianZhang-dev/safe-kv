#!/usr/bin/env python
"""Compare manual greedy generation from prefill cache against model.generate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.config import load_config
from safekv.full_prefill import (
    GENERATION_MODES,
    greedy_generate_from_prefill_result,
    load_examples_for_config,
    select_generation_sanity_examples,
    set_deterministic_seed,
)
from safekv.generation_sanity import (
    category_counts,
    first_failed_check,
    first_token_mismatch,
    format_first_mismatch,
)
from safekv.modeling import load_causal_lm
from safekv.prompting import build_rag_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--examples-per-category", type=int, default=1)
    parser.add_argument("--out", type=Path, default=Path("results/generation_sanity.json"))
    parser.add_argument(
        "--debug-dir",
        type=Path,
        default=Path("results/generation_sanity_debug"),
    )
    parser.add_argument("--allow-mismatch", action="store_true")
    return parser.parse_args()


def main() -> None:
    import torch

    args = parse_args()
    config = load_config(args.config)
    set_deterministic_seed(config.seed)

    config_dir = args.config.resolve().parent.parent
    examples = load_examples_for_config(config, config_dir=config_dir)
    loaded = load_causal_lm(config.model)
    examples = select_generation_sanity_examples(
        examples,
        examples_per_category=args.examples_per_category,
    )

    checks = []
    first_debug_written = False
    for example in examples:
        pack = build_rag_prompt(
            example,
            loaded.tokenizer,
            prompt_format=config.experiment.prompt_format,
            boundary_window_tokens=config.prompt.boundary_window_tokens,
            adaptive_boundary_window=config.prompt.adaptive_boundary_window,
        )
        input_ids = torch.tensor([pack.full_input_ids], dtype=torch.long, device=loaded.device)
        attention_mask = torch.ones_like(input_ids, device=loaded.device)
        position_ids = torch.arange(
            input_ids.shape[1], dtype=torch.long, device=loaded.device
        ).unsqueeze(0)

        with torch.no_grad():
            outputs = loaded.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                position_ids=position_ids,
                use_cache=True,
            )
            generated = loaded.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=config.generation.max_new_tokens,
                do_sample=False,
                repetition_penalty=1.0,
                pad_token_id=getattr(loaded.tokenizer, "eos_token_id", None),
                return_dict_in_generate=True,
                output_scores=True,
            )
            model_tokens = [
                int(token_id)
                for token_id in generated.sequences[0, input_ids.shape[1] :].tolist()
            ]
            mode_results = {}
            for mode in GENERATION_MODES:
                result = greedy_generate_from_prefill_result(
                    model=loaded.model,
                    tokenizer=loaded.tokenizer,
                    prompt_outputs=outputs,
                    first_logits=outputs.logits,
                    prompt_length=input_ids.shape[1],
                    max_new_tokens=config.generation.max_new_tokens,
                    stop_on_newline=False,
                    stop_strings=[],
                    device=loaded.device,
                    mode=mode,
                )
                mode_results[mode] = {
                    "tokens": result.token_ids,
                    "text": loaded.tokenizer.decode(
                        result.token_ids, skip_special_tokens=True
                    ),
                    "match": result.token_ids == model_tokens,
                    "first_mismatch": first_token_mismatch(result.token_ids, model_tokens),
                    "score_debug": compare_step_scores(
                        result.step_logits,
                        list(generated.scores or []),
                        loaded.tokenizer,
                    ),
                }
        matched_modes = [
            mode for mode, mode_result in mode_results.items() if mode_result["match"]
        ]
        preferred_mode = (
            config.generation.prefill_mode
            if config.generation.prefill_mode in matched_modes
            else matched_modes[0]
            if matched_modes
            else config.generation.prefill_mode
            if config.generation.prefill_mode in mode_results
            else GENERATION_MODES[0]
        )
        preferred_result = mode_results[preferred_mode]
        match = bool(matched_modes)
        check = {
            "example_id": example.id,
            "category": example.category,
            "match": match,
            "configured_mode": config.generation.prefill_mode,
            "matched_modes": matched_modes,
            "preferred_mode": preferred_mode,
            "manual_tokens": preferred_result["tokens"],
            "model_generate_tokens": model_tokens,
            "manual_text": preferred_result["text"],
            "model_generate_text": loaded.tokenizer.decode(
                model_tokens, skip_special_tokens=True
            ),
            "first_mismatch": preferred_result["first_mismatch"],
            "mode_results": {
                mode: {
                    "match": mode_result["match"],
                    "first_mismatch": mode_result["first_mismatch"],
                    "tokens": mode_result["tokens"],
                    "text": mode_result["text"],
                }
                for mode, mode_result in mode_results.items()
            },
        }
        checks.append(check)
        if not match and not first_debug_written:
            write_debug_json(
                args.debug_dir,
                example_id=example.id,
                check=check,
                mode_results=mode_results,
                model_generation_config=loaded.model.generation_config.to_dict(),
                generate_kwargs=neutral_generate_kwargs(config.generation.max_new_tokens),
            )
            first_debug_written = True

    matching_modes_all_examples = [
        mode
        for mode in GENERATION_MODES
        if all(mode in check.get("matched_modes", []) for check in checks)
    ]
    summary = {
        "config_path": str(args.config),
        "num_examples": len(checks),
        "category_counts": category_counts(checks),
        "all_match": bool(matching_modes_all_examples),
        "matching_modes": matching_modes_all_examples,
        "per_example_any_mode_match": all(check["match"] for check in checks),
        "configured_mode": config.generation.prefill_mode,
        "generate_kwargs": neutral_generate_kwargs(config.generation.max_new_tokens),
        "checks": checks,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if not summary["all_match"] and not args.allow_mismatch:
        failed = first_failed_check(checks)
        if failed is not None:
            print(format_first_mismatch(failed), file=sys.stderr)
        raise SystemExit(1)


def neutral_generate_kwargs(max_new_tokens: int) -> dict[str, object]:
    return {
        "max_new_tokens": max_new_tokens,
        "do_sample": False,
        "repetition_penalty": 1.0,
        "return_dict_in_generate": True,
        "output_scores": True,
    }


def compare_step_scores(
    manual_scores: list[object],
    model_scores: list[object],
    tokenizer: object,
    max_steps: int = 8,
) -> list[dict[str, object]]:
    import torch

    rows: list[dict[str, object]] = []
    for step, (manual_score, model_score) in enumerate(zip(manual_scores, model_scores)):
        if step >= max_steps:
            break
        manual_tensor = manual_score.float().cpu()
        model_tensor = model_score[0].detach().float().cpu()
        diff = torch.max(torch.abs(manual_tensor - model_tensor)).item()
        manual_top = int(torch.argmax(manual_tensor).item())
        model_top = int(torch.argmax(model_tensor).item())
        rows.append(
            {
                "step": step,
                "max_abs_diff": float(diff),
                "manual_top_token": manual_top,
                "model_generate_top_token": model_top,
                "manual_top_text": tokenizer.decode([manual_top], skip_special_tokens=True),
                "model_generate_top_text": tokenizer.decode([model_top], skip_special_tokens=True),
            }
        )
    return rows


def write_debug_json(
    debug_dir: Path,
    example_id: str,
    check: dict[str, object],
    mode_results: dict[str, dict[str, object]],
    model_generation_config: dict[str, object],
    generate_kwargs: dict[str, object],
) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    debug = {
        "example_id": example_id,
        "check": check,
        "model_generation_config": model_generation_config,
        "generate_kwargs": generate_kwargs,
        "mode_score_debug": {
            mode: mode_result["score_debug"] for mode, mode_result in mode_results.items()
        },
    }
    (debug_dir / f"{example_id}.json").write_text(
        json.dumps(debug, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
