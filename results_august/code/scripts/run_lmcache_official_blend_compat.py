#!/usr/bin/env python
"""Run LMCache's official CacheBlend example with one documented API shim.

The LMCache v0.5.4 example expands ``dataclasses.asdict(EngineArgs)`` into
``vllm.LLM``.  Newer vLLM releases reject one of the resulting ``None``
compilation fields before the engine is created.  This wrapper imports the
unmodified official example and replaces only its engine-construction helper
with the equivalent explicit public ``LLM`` arguments.  Prompt construction,
LMCache settings, request order, generation, and cleanup remain official.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.util
import json
import platform
import sys
from pathlib import Path
from typing import Any, Iterator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-blend", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--use-disk", action="store_true")
    parser.add_argument("--enable-sparse", action="store_true")
    parser.add_argument(
        "--register-model-shim",
        action="store_true",
        help=(
            "wrap vLLM GPUModelRunner.load_model to perform the model registration "
            "required by LMCache CacheBlend"
        ),
    )
    parser.add_argument("--blend-special-str", default="# #")
    return parser.parse_args()


def load_official_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("lmcache_official_blend", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import official LMCache example: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_model_registration_shim() -> list[str]:
    """Install the public workaround for LMCache issue #4131/#1405."""

    patched = []
    for module_name in (
        "vllm.v1.worker.gpu_model_runner",
        "vllm.v1.worker.gpu.model_runner",
    ):
        try:
            runner_class = importlib.import_module(module_name).GPUModelRunner
        except (ImportError, AttributeError):
            continue
        original = runner_class.load_model
        if getattr(original, "_safekv_lmcache_registration_shim", False):
            patched.append(module_name)
            continue

        def load_model_and_register(
            self: Any,
            *positional: Any,
            _original: Any = original,
            **keyword: Any,
        ) -> Any:
            result = _original(self, *positional, **keyword)
            from lmcache.integration.vllm.utils import ENGINE_NAME
            from lmcache.v1.compute.models.utils import VLLMModelTracker

            model = self.model
            # Enforce-eager should make this unnecessary, but unwrapping keeps
            # the workaround valid if vLLM still supplies a runnable wrapper.
            model = getattr(model, "runnable", model)
            VLLMModelTracker.register_model(ENGINE_NAME, model)
            return result

        load_model_and_register._safekv_lmcache_registration_shim = True
        runner_class.load_model = load_model_and_register
        patched.append(module_name)
    if not patched:
        raise RuntimeError("no supported vLLM GPUModelRunner class was found")
    return patched


def main() -> None:
    args = parse_args()
    official_path = args.official_blend.resolve()
    model_path = args.model.resolve()
    report_path = args.report.resolve()
    if report_path.exists():
        raise FileExistsError(f"refusing to overwrite compatibility report: {report_path}")
    if not official_path.is_file() or not model_path.is_dir():
        raise FileNotFoundError("official example or local model snapshot is missing")

    official = load_official_module(official_path)
    from lmcache.integration.vllm.utils import ENGINE_NAME
    from lmcache.v1.cache_engine import LMCacheEngineBuilder
    from vllm import LLM
    from vllm.config import KVTransferConfig
    import lmcache
    import torch
    import transformers
    import vllm

    patched_model_runners = (
        install_model_registration_shim() if args.register_model_shim else []
    )

    @contextlib.contextmanager
    def compatible_builder(lmcache_connector: str, model: str) -> Iterator[Any]:
        transfer = KVTransferConfig(
            kv_connector=lmcache_connector,
            kv_role="kv_both",
        )
        # Semantically identical to the non-default fields in the official
        # EngineArgs construction, without expanding unrelated None defaults.
        llm = LLM(
            model=model,
            kv_transfer_config=transfer,
            max_model_len=32648,
            gpu_memory_utilization=0.7,
            enable_prefix_caching=False,
            enforce_eager=True,
        )
        try:
            yield llm
        finally:
            LMCacheEngineBuilder.destroy(ENGINE_NAME)

    official.build_llm_with_lmcache = compatible_builder
    forwarded = [str(official_path), "--model", str(model_path)]
    if args.use_disk:
        forwarded.append("--use-disk")
    if args.enable_sparse:
        forwarded.append("--enable-sparse")
    forwarded.extend(["--blend-special-str", args.blend_special_str])
    previous_argv = sys.argv
    try:
        sys.argv = forwarded
        official.main()
    finally:
        sys.argv = previous_argv

    report = {
        "schema_version": 1,
        "status": "completed",
        "scope": "compatibility smoke only; not a SAFE-KV comparative benchmark",
        "official_example": str(official_path),
        "model": str(model_path),
        "compatibility_delta": (
            "replace EngineArgs-to-asdict expansion with the same explicit non-default "
            "LLM constructor arguments required by vLLM 0.27.1"
        ),
        "model_registration_shim": {
            "enabled": args.register_model_shim,
            "patched_modules": patched_model_runners,
            "operation": (
                "wrap GPUModelRunner.load_model and register the loaded model with "
                "VLLMModelTracker under LMCache ENGINE_NAME"
                if args.register_model_shim
                else None
            ),
        },
        "unchanged_official_components": [
            "LMCache environment configuration",
            "prompt and separator construction",
            "request order",
            "sampling parameters",
            "generation calls",
            "LMCache cleanup",
        ],
        "runtime": {
            "python": platform.python_version(),
            "lmcache": lmcache.__version__,
            "vllm": vllm.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
