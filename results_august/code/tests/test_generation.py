from safekv.generation import (
    compute_task_metrics,
    normalize_answer,
    should_stop_generated_text,
    token_f1,
    topk_from_logits,
    trim_generated_answer,
)


class TinyTokenizer:
    def decode(self, token_ids, skip_special_tokens=False):
        del skip_special_tokens
        names = {0: "zero", 1: "one", 2: "two", 3: "three"}
        return names[token_ids[0]]


def test_normalize_answer_is_deterministic() -> None:
    assert normalize_answer(" The  Mira,   Solen! ") == "mira solen"
    assert normalize_answer("A 1994.") == "1994"


def test_token_f1_and_task_metrics() -> None:
    assert token_f1("Mira Solen", "Mira Solen") == 1.0
    assert token_f1("Mira", "Mira Solen") == 2 / 3

    metrics = compute_task_metrics("Mira Solen", "Solen")
    assert metrics["gold_exact_match"] is False
    assert metrics["gold_f1"] > 0
    assert metrics["answer_contains_gold"] is True


def test_topk_from_plain_logits() -> None:
    topk = topk_from_logits([0.1, 3.0, -1.0, 2.0], TinyTokenizer(), k=3)

    assert [row["token_id"] for row in topk] == [1, 3, 0]
    assert [row["token"] for row in topk] == ["one", "three", "zero"]
    assert topk[0]["logit"] == 3.0


def test_stop_strings_and_newline_stop_generation() -> None:
    stop_strings = ["Human:", "[Document", "Question:", "Answer:"]

    assert should_stop_generated_text("Mira Solen\nNext", True, stop_strings)
    assert should_stop_generated_text("Mira Solen [Document 1]", False, stop_strings)
    assert should_stop_generated_text("Mira Solen Question:", False, stop_strings)
    assert not should_stop_generated_text("Mira Solen", True, stop_strings)

    assert trim_generated_answer("Mira Solen\n[Document 1]", True, stop_strings) == "Mira Solen"
    assert trim_generated_answer("Mira Solen Question: repeat", False, stop_strings) == "Mira Solen"
