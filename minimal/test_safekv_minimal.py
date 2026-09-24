"""CPU tests for minimal/safekv_minimal.py on a tiny randomly initialised Qwen2 model (no download).

Run:  python -m pytest -q minimal
The paper's own test suite is code/tests (135 passed, 1 skipped); these tests cover only the one-file implementation.
"""
import json
import sys
from pathlib import Path

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import safekv_minimal as sk  # noqa: E402
from transformers import Qwen2Config, Qwen2ForCausalLM  # noqa: E402

ATOL = 1e-4


@pytest.fixture(scope="module")
def model():
    torch.manual_seed(0)
    cfg = Qwen2Config(vocab_size=97, hidden_size=64, intermediate_size=128, num_hidden_layers=3, num_attention_heads=4,
                      num_key_value_heads=2, max_position_embeddings=512, rope_theta=10000.0)
    return Qwen2ForCausalLM(cfg).eval()


@pytest.fixture(scope="module")
def prompt():
    g = torch.Generator().manual_seed(1)
    r = lambda n: torch.randint(3, 97, (n,), generator=g).tolist()
    return sk.Prompt(prefix=r(6), docs=[r(9), r(7), r(11), r(8)], query=r(5))


def last_layer_gap(a, b, lo, hi):
    """Max |a-b| over the keys and values of the last layer on positions [lo, hi). (Layer-0 keys depend only on the
    token and its position, so context effects are checked on the last layer.)"""
    (ka, va), (kb, vb) = a[-1], b[-1]
    return max((ka[:, :, lo:hi] - kb[:, :, lo:hi]).abs().max().item(), (va[:, :, lo:hi] - vb[:, :, lo:hi]).abs().max().item())


def doc_span(p, i):
    s = p.doc_starts[i]
    return s, s + len(p.docs[i])


def test_suffix_repair_from_first_document_reproduces_full_prefill(model, prompt):
    skv = sk.SafeKV(model, max_new_tokens=6)
    full = skv.full_prefill(prompt)
    rep, n = skv.repair(prompt, skv.compose(prompt), start=0, mode="suffix")
    assert n == sum(len(d) for d in prompt.docs)
    assert sk.kv_len(rep) == sk.kv_len(full) == prompt.context_len
    assert last_layer_gap(rep, full, 0, prompt.context_len) < ATOL
    assert skv.answer(prompt, rep) == skv.answer(prompt, full)


def test_composition_changes_every_state_after_the_first_document(model, prompt):
    skv = sk.SafeKV(model)
    full, comp = skv.full_prefill(prompt), skv.compose(prompt)
    assert last_layer_gap(comp, full, 0, doc_span(prompt, 0)[1]) < ATOL          # prefix and d1: true history
    for i in range(1, len(prompt.docs)):                                           # d2..dm: mismatched history
        assert last_layer_gap(comp, full, *doc_span(prompt, i)) > 1e-3
    for i in range(len(prompt.docs)):                                               # same tokens, same positions:
        lo, hi = doc_span(prompt, i)                                                # layer-0 keys agree everywhere
        assert (comp[0][0][:, :, lo:hi] - full[0][0][:, :, lo:hi]).abs().max().item() < ATOL


def test_document_only_repair_leaves_later_slices_stale(model, prompt):
    skv = sk.SafeKV(model)
    full, comp = skv.full_prefill(prompt), skv.compose(prompt)
    rep, n = skv.repair(prompt, comp, start=1, mode="document")
    assert n == len(prompt.docs[1])
    assert last_layer_gap(rep, full, *doc_span(prompt, 1)) < ATOL      # d2 now sees p, d1 (both exact)
    for i in range(2, len(prompt.docs)):
        lo, hi = doc_span(prompt, i)
        assert last_layer_gap(rep, comp, lo, hi) == 0.0                # untouched, still composed
        assert last_layer_gap(rep, full, lo, hi) > 1e-3                # and still wrong: it never saw d2


def test_suffix_repair_is_causally_closed(model, prompt):
    skv = sk.SafeKV(model)
    full, comp = skv.full_prefill(prompt), skv.compose(prompt)
    rep, n = skv.repair(prompt, comp, start=1, mode="suffix")         # history before d2 (p, d1) is exact
    assert n == sum(len(d) for d in prompt.docs[1:])
    assert last_layer_gap(rep, full, 0, prompt.context_len) < ATOL
    rep3, _ = skv.repair(prompt, comp, start=2, mode="suffix")        # keeps stale d2, re-encodes d3.. after it
    assert last_layer_gap(rep3, comp, 0, doc_span(prompt, 1)[1]) == 0.0
    ref, _ = skv.forward([t for d in prompt.docs[2:] for t in d], sk.kv_slice(comp, 0, prompt.doc_starts[2]))
    assert last_layer_gap(rep3, ref, 0, prompt.context_len) == 0.0


def test_cached_greedy_decoding_matches_uncached(model, prompt):
    skv = sk.SafeKV(model, max_new_tokens=8)
    kv, logits = skv.forward(prompt.ids)
    cached = skv.greedy(kv, logits)
    ids, uncached = list(prompt.ids), []
    with torch.no_grad():
        for _ in range(8):
            t = int(model(input_ids=torch.tensor([ids])).logits[0, -1].argmax())
            uncached.append(t); ids.append(t)
    assert cached == uncached


def test_selectors_and_metric():
    assert sk.select_start([0.2, 0.9, 0.9, 0.1], k=1) == 1                      # tie -> lower id
    assert sk.select_start([0.2, 0.9, 0.9, 0.1], k=1, doc_ids=[5, 7, 3, 2]) == 2  # ids decide, not positions
    assert sk.select_start([0.8, 0.1, 0.9, 0.3], k=2) == 0                      # earliest of the top-2
    docs = [{"title": "Ilse Moravec", "text": "born in Graz"}, {"title": "Varn", "text": "a peninsula"}]
    assert sk.query_scores("Where was Ilse Moravec born?", docs) == [1.0, 0.0]
    assert sk.normalize_answer("The  Graz.") == sk.normalize_answer("graz")


def test_cli_end_to_end_with_local_tiny_model(tmp_path, model, capsys):
    from tokenizers import Tokenizer, models, pre_tokenizers
    from transformers import PreTrainedTokenizerFast
    words = sorted({w for d in sk.EXAMPLE["documents"] for w in (d["title"] + " " + d["text"]).split()}
                   | set(sk.EXAMPLE["question"].split()) | set("Question: Answer: Answer with the shortest exact "
                                                                 "answer phrase from documents. [Document | Title: ]".split()))
    vocab = {"<unk>": 0, "<eos>": 1, **{w: i + 2 for i, w in enumerate(words[:95])}}
    t = Tokenizer(models.WordLevel(vocab, unk_token="<unk>")); t.pre_tokenizer = pre_tokenizers.WhitespaceSplit()
    tok = PreTrainedTokenizerFast(tokenizer_object=t, unk_token="<unk>", eos_token="<eos>")
    tok.save_pretrained(tmp_path); model.save_pretrained(tmp_path)
    sk.main(["--model", str(tmp_path), "--device", "cpu", "--max-new-tokens", "3"])
    out = capsys.readouterr().out
    for name in ("full_prefill", "prefix_composition", "document_repair", "suffix_repair"):
        assert name in out
    rec = dict(sk.EXAMPLE, id="x0", documents=[dict(d, doc_id=i) for i, d in enumerate(sk.EXAMPLE["documents"])])
    (tmp_path / "d.jsonl").write_text(json.dumps(rec) + "\n" + json.dumps(dict(rec, id="x1")) + "\n")
    sk.main(["--model", str(tmp_path), "--device", "cpu", "--max-new-tokens", "3", "--jsonl", str(tmp_path / "d.jsonl"),
             "--k", "1", "--out", str(tmp_path / "o.jsonl")])
    lines = [json.loads(l) for l in (tmp_path / "o.jsonl").read_text().splitlines()]
    assert len(lines) == 2 and lines[0]["suffix_repair"]["recompute_ratio"] > 0
    assert lines[0]["full_prefill"]["equivalent"] is True


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("ds", ["hotpotqa", "2wiki"])
def test_selectors_reproduce_the_paper_runs(ds):
    """Query and risk K1/K2 starts equal the repaired-suffix lengths recorded in the paper's main runs (2,000 per set)."""
    import csv
    data, runs = ROOT / f"data/external_{ds}_500.jsonl", ROOT / f"results/acl_qwen25_7b_{ds}_suffix_main_500/answer_eval_metrics.csv"
    if not (data.exists() and runs.exists()):
        pytest.skip("repository data not present")
    recs = {r["id"]: r for r in map(json.loads, data.read_text(encoding="utf-8").splitlines())}
    methods = {"risk_guided_suffix_closure_k1": ("risk", 1), "risk_guided_suffix_closure_k2": ("risk", 2),
               "query_similarity_suffix_closure_k1": ("query", 1), "query_similarity_suffix_closure_k2": ("query", 2)}
    n = 0
    for row in csv.DictReader(open(runs, newline="")):
        if row["method"] not in methods:
            continue
        sel, k = methods[row["method"]]
        rec = recs[row["example_id"]]
        scores = sk.risk_scores(rec) if sel == "risk" else sk.query_scores(rec["question"], rec["documents"])
        start = sk.select_start(scores, k, [d["doc_id"] for d in rec["documents"]])
        assert len(rec["documents"]) - start == int(row["patched_doc_count"]), (row["example_id"], row["method"])
        n += 1
    assert n == 2000
