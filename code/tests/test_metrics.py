import math

from safekv.metrics import logit_kl_divergence, logit_preservation_metrics, topk_overlap


class TinyTokenizer:
    def decode(self, token_ids, skip_special_tokens=False):
        del skip_special_tokens
        return f"tok{token_ids[0]}"


def test_kl_is_zero_for_identical_logits() -> None:
    assert math.isclose(logit_kl_divergence([1.0, 2.0], [1.0, 2.0]), 0.0, abs_tol=1e-7)


def test_topk_overlap() -> None:
    assert topk_overlap([4.0, 3.0, 2.0, 1.0], [4.0, 1.0, 3.0, 2.0], 2) == 0.5


def test_logit_preservation_metrics() -> None:
    metrics = logit_preservation_metrics([0.1, 4.0, 2.0], [0.2, 3.0, 5.0], TinyTokenizer())

    assert metrics["top1_match"] is False
    assert metrics["argmax_full_token"] == 1
    assert metrics["argmax_method_token"] == 2
    assert metrics["argmax_full_decoded"] == "tok1"
    assert metrics["argmax_method_decoded"] == "tok2"
