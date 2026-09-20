"""HuggingFace model and tokenizer loading utilities."""

from __future__ import annotations

from dataclasses import dataclass

from safekv.config import ModelConfig


@dataclass(frozen=True)
class LoadedModel:
    tokenizer: object
    model: object
    device: str
    torch_dtype_name: str
    warnings: list[str]


def load_tokenizer(model_name: str, trust_remote_code: bool = False) -> object:
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        use_fast=True,
        trust_remote_code=trust_remote_code,
    )
    if not getattr(tokenizer, "is_fast", False):
        raise ValueError(f"tokenizer for {model_name!r} must be a fast tokenizer")
    return tokenizer


def load_causal_lm(model_config: ModelConfig) -> LoadedModel:
    import torch
    from transformers import AutoModelForCausalLM

    _ensure_torch_default_device_compat(torch)

    warnings: list[str] = []
    device = _resolve_device(model_config.device, warnings)
    dtype = _resolve_dtype(model_config.dtype)
    load_dtype = dtype
    if device == "cpu" and dtype is torch.float16:
        warnings.append("Requested float16 on CPU; using float32 for CPU inference.")
        load_dtype = torch.float32

    tokenizer = load_tokenizer(
        model_config.name,
        trust_remote_code=model_config.trust_remote_code,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_config.name,
        torch_dtype=load_dtype,
        trust_remote_code=model_config.trust_remote_code,
    )
    model.to(device)
    model.eval()
    return LoadedModel(
        tokenizer=tokenizer,
        model=model,
        device=device,
        torch_dtype_name=str(load_dtype).replace("torch.", ""),
        warnings=warnings,
    )


def _ensure_torch_default_device_compat(torch_module: object) -> None:
    if hasattr(torch_module, "get_default_device"):
        return

    def get_default_device():
        return torch_module.device("cpu")

    setattr(torch_module, "get_default_device", get_default_device)


def _resolve_device(requested_device: str, warnings: list[str]) -> str:
    import torch

    requested = requested_device.lower()
    if requested == "cuda":
        if torch.cuda.is_available():
            return "cuda"
        warnings.append("Requested CUDA but torch.cuda.is_available() is false; using CPU.")
        return "cpu"
    if requested == "cpu":
        return "cpu"
    raise ValueError(f"unsupported device {requested_device!r}; expected 'cuda' or 'cpu'")


def _resolve_dtype(dtype_name: str):
    import torch

    normalized = dtype_name.lower()
    if normalized in {"float16", "fp16", "half"}:
        return torch.float16
    if normalized in {"bfloat16", "bf16"}:
        return torch.bfloat16
    if normalized in {"float32", "fp32", "single"}:
        return torch.float32
    raise ValueError(f"unsupported dtype {dtype_name!r}")
