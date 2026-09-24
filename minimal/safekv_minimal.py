#!/usr/bin/env python3
"""SAFE-KV in one file: causal suffix repair for non-prefix KV-cache reuse in RAG.

A compact, dependency-light reference implementation of the protocol in

    Xingjian Zhang. SAFE-KV: Causal Suffix Repair for Behavior-Preserving Non-Prefix KV Cache Reuse in RAG.
    Findings of AACL-IJCNLP 2026.

It works with any Hugging Face decoder-only model that uses the standard `DynamicCache` (tested with the Qwen2
family) and needs only `torch` and `transformers`.

The idea in four steps, for a prompt x = (p, d_1, ..., d_m, q):

  1. Full prefill (the reference).  One causal pass over x; every KV entry is computed under its true history.
  2. Prefix-conditioned composition (what non-prefix reuse does).  Each document d_i is encoded after the static
     prefix p alone, at its target position, and the slices are concatenated.  Same tokens, same positions, but for
     i > 1 the slice of d_i never saw d_1..d_{i-1}: its history is mismatched and the answer can change.
  3. Causal suffix repair (SAFE-KV).  Choose a start document s, keep the composed cache before d_s, and re-encode
     d_s, ..., d_m in order.  Every state from s onward is then computed under a consistent history.  Re-encoding
     d_s alone ("document-only repair") is not enough: every later slice still misses it (causal closure).
  4. The contract.  A repaired cache is correct when greedy decoding of the query reproduces the full-prefill answer
     (normalized short-answer equivalence); the cost is the fraction of document tokens re-encoded.

The start s is chosen by a training-free selector: the query selector (question-term recall, as in the paper) is
built in; `--selector risk` uses the paper's risk selector from `code/safekv/doc_selector.py` when run inside the
repository.  Selected top-K documents define s as the earliest of them; score ties go to the lower document id.

This file is a readable companion to the artifact, not the code that produced the paper's numbers
(`code/scripts/run_answer_eval.py`).  It tokenizes the prefix, each document and the query separately, so segment
boundaries are exact, and its numbers are close to but not identical with the paper's.

Usage:
  python minimal/safekv_minimal.py                                   # built-in example, Qwen2.5-0.5B-Instruct
  python minimal/safekv_minimal.py --model Qwen/Qwen2.5-7B-Instruct --device cuda --dtype float16
  python minimal/safekv_minimal.py --jsonl data/external_2wiki_500.jsonl --limit 50 --k 2 --selector risk
"""
from __future__ import annotations

import argparse
import json
import re
import string
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

KV = list  # list over layers of (key, value) tensors, each [batch=1, kv_heads, seq, head_dim]

ANSWER_INSTRUCTION = "Answer with the shortest exact answer phrase from the documents."
STOP_STRINGS = ("Human:", "[Document", "Question:", "Answer:")
_STOPWORDS = {"a", "an", "and", "at", "by", "does", "for", "from", "in", "is", "of", "on", "or", "the", "to", "was",
              "what", "when", "where", "who", "with"}


# ----------------------------------------------------------------------------------------------- KV-cache helpers
def to_kv(cache) -> KV:
    """Model cache -> list of (key, value) per layer."""
    if hasattr(cache, "layers"):
        return [(layer.keys, layer.values) for layer in cache.layers]
    if hasattr(cache, "to_legacy_cache"):
        return [tuple(kv) for kv in cache.to_legacy_cache()]
    return [tuple(kv) for kv in cache]


def to_cache(kv: KV) -> DynamicCache:
    """List of (key, value) per layer -> a fresh DynamicCache the model can extend."""
    cache = DynamicCache()
    for i, (k, v) in enumerate(kv):
        cache.update(k, v, i)
    return cache


def kv_slice(kv: KV, start: int, end: int) -> KV:
    return [(k[:, :, start:end], v[:, :, start:end]) for k, v in kv]


def kv_cat(*parts: KV) -> KV:
    parts = [p for p in parts if p]
    return [(torch.cat([p[i][0] for p in parts], dim=2), torch.cat([p[i][1] for p in parts], dim=2))
            for i in range(len(parts[0]))]


def kv_len(kv: KV) -> int:
    return kv[0][0].shape[2] if kv else 0


# ----------------------------------------------------------------------------------------------- prompt
@dataclass
class Prompt:
    """Token ids of the static prefix, each retrieved document (in prompt order) and the query."""
    prefix: list[int]
    docs: list[list[int]]
    query: list[int]

    @property
    def doc_starts(self) -> list[int]:
        starts, pos = [], len(self.prefix)
        for d in self.docs:
            starts.append(pos)
            pos += len(d)
        return starts

    @property
    def context_len(self) -> int:
        return len(self.prefix) + sum(len(d) for d in self.docs)

    @property
    def ids(self) -> list[int]:
        return self.prefix + [t for d in self.docs for t in d] + self.query


def render_prompt(tokenizer, documents: list[dict], question: str) -> Prompt:
    """The paper's chat-RAG layout: one user message holding the documents and the question.

    documents: [{"title": ..., "text": ...}, ...] in prompt order.
    """
    doc_texts = [f"[Document {i} | Title: {d.get('title', '')}]\n{d['text']}\n\n" for i, d in enumerate(documents, 1)]
    query_text = f"Question: {question}\n{ANSWER_INSTRUCTION}\nAnswer:"
    content = "".join(doc_texts) + query_text
    head, tail = "", ""
    if getattr(tokenizer, "chat_template", None):
        rendered = tokenizer.apply_chat_template([{"role": "user", "content": content}], tokenize=False,
                                                 add_generation_prompt=True)
        at = rendered.find(content)
        if at < 0:
            raise ValueError("the chat template does not keep the user content verbatim")
        head, tail = rendered[:at], rendered[at + len(content):]
    enc = lambda s: tokenizer(s, add_special_tokens=False)["input_ids"] if s else []
    head_ids = enc(head)
    if not head_ids and tokenizer.bos_token_id is not None:
        head_ids = [tokenizer.bos_token_id]
    return Prompt(prefix=head_ids, docs=[enc(t) for t in doc_texts], query=enc(query_text + tail))


# ----------------------------------------------------------------------------------------------- core protocol
class SafeKV:
    def __init__(self, model, tokenizer=None, max_new_tokens: int = 16):
        self.model = model.eval()
        self.tokenizer = tokenizer
        self.max_new_tokens = max_new_tokens
        self.device = next(model.parameters()).device
        eos = getattr(model.generation_config, "eos_token_id", None)
        eos = eos if isinstance(eos, (list, tuple)) else [eos]
        if tokenizer is not None:
            eos = list(eos) + [tokenizer.eos_token_id]
        self.eos = {e for e in eos if e is not None}

    @torch.no_grad()
    def forward(self, ids: list[int], past: KV | None = None, start: int | None = None):
        """Encode `ids` after the cache `past`, at absolute positions start..start+len(ids)-1.

        `start` defaults to the length of `past`.  A larger `start` places a document at its target position while it
        attends only to `past`; this is how prefix-conditioned document caches are built.
        Returns the extended cache and the logits of the last token.
        """
        past = past or []
        start = kv_len(past) if start is None else start
        x = torch.tensor([ids], device=self.device)
        pos = torch.arange(start, start + len(ids), device=self.device)[None]
        mask = torch.ones(1, kv_len(past) + len(ids), dtype=torch.long, device=self.device)
        out = self.model(input_ids=x, position_ids=pos, attention_mask=mask,
                         past_key_values=to_cache(past) if past else DynamicCache(), use_cache=True)
        return to_kv(out.past_key_values), out.logits[0, -1]

    # (1) reference
    def full_prefill(self, prompt: Prompt) -> KV:
        """Context cache (prefix + documents) computed in one causal pass."""
        kv, _ = self.forward(prompt.prefix + [t for d in prompt.docs for t in d])
        return kv

    # (2) non-prefix reuse
    def compose(self, prompt: Prompt) -> KV:
        """Prefix-conditioned composition: each document encoded after the prefix alone, at its target position.

        In a serving system the per-document slices come from a cache shared across requests; here they are computed
        on the spot so that the composed cache is exactly what such a cache would hold.
        """
        P = len(prompt.prefix)
        prefix_kv = self.forward(prompt.prefix)[0] if P else []
        slices = []
        for d, s in zip(prompt.docs, prompt.doc_starts):
            kv, _ = self.forward(d, prefix_kv, start=s)      # sees p only, sits at its target position s
            slices.append(kv_slice(kv, P, P + len(d)))
        return kv_cat(prefix_kv, *slices)

    # (3) repair
    def repair(self, prompt: Prompt, composed: KV, start: int | None, mode: str = "suffix") -> tuple[KV, int]:
        """Repair the composed context cache from document index `start` (0-based).

        mode="suffix":   SAFE-KV. Keep composed[:d_start], re-encode d_start..d_m in order (actual forwarding).
        mode="document": re-encode d_start only; later slices keep their mismatched histories.
        Returns the repaired context cache and the number of document tokens re-encoded.
        """
        if start is None:
            return composed, 0
        a = prompt.doc_starts[start]
        kept = kv_slice(composed, 0, a)
        if mode == "suffix":
            ids = [t for d in prompt.docs[start:] for t in d]
            kv, _ = self.forward(ids, kept)
            return kv, len(ids)
        if mode == "document":
            ids = prompt.docs[start]
            kv, _ = self.forward(ids, kept)
            return kv_cat(kv, kv_slice(composed, a + len(ids), prompt.context_len)), len(ids)
        raise ValueError(mode)

    # (4) the contract
    @torch.no_grad()
    def answer(self, prompt: Prompt, context: KV) -> str:
        """Re-encode the query after the context cache and decode greedily (the query is never reused)."""
        kv, logits = self.forward(prompt.query, context)
        return self.decode(self.greedy(kv, logits))

    @torch.no_grad()
    def greedy(self, kv: KV, logits) -> list[int]:
        out = []
        for _ in range(self.max_new_tokens):
            t = int(logits.argmax())
            if t in self.eos:
                break
            out.append(t)
            if self.tokenizer is not None and "\n" in self.tokenizer.decode(out):
                break
            kv, logits = self.forward([t], kv)
        return out

    def decode(self, ids: list[int]) -> str:
        if self.tokenizer is None:
            return " ".join(map(str, ids))
        text = self.tokenizer.decode(ids, skip_special_tokens=True)
        text = text.split("\n")[0]
        for s in STOP_STRINGS:
            text = text.split(s)[0]
        return text.strip()

    def run(self, prompt: Prompt, start: int | None) -> dict:
        """Full prefill, composition, document-only repair and suffix repair from `start`, with answers and cost."""
        n_doc = sum(len(d) for d in prompt.docs)
        ref = self.answer(prompt, self.full_prefill(prompt))
        composed = self.compose(prompt)
        rows = {"full_prefill": (ref, 1.0), "prefix_composition": (self.answer(prompt, composed), 0.0)}
        for mode in ("document", "suffix"):
            ctx, n = self.repair(prompt, composed, start, mode)
            rows[f"{mode}_repair"] = (self.answer(prompt, ctx), n / max(1, n_doc))
        return {name: {"answer": a, "equivalent": normalize_answer(a) == normalize_answer(ref), "recompute_ratio": r}
                for name, (a, r) in rows.items()}


# ----------------------------------------------------------------------------------------------- selectors + metric
def lexical_terms(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[A-Za-z0-9]+", text) if t.lower() not in _STOPWORDS}


def query_scores(question: str, documents: list[dict]) -> list[float]:
    """Question-term recall of each document (the paper's query selector)."""
    q = lexical_terms(question)
    return [len(q & lexical_terms(f"{d.get('title', '')} {d['text']}")) / len(q) if q else 0.0 for d in documents]


def risk_scores(record: dict) -> list[float]:
    """The paper's risk selector, imported unchanged from code/safekv/doc_selector.py (repository checkout only)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    from safekv.data_schema import DiagnosticExample
    from safekv.doc_selector import risk_guided_doc_scores
    by_id = {s.doc_id: s.score for s in risk_guided_doc_scores(DiagnosticExample.from_dict(record))}
    return [by_id[int(d["doc_id"])] for d in record["documents"]]


def select_start(scores: list[float], k: int, doc_ids: list[int] | None = None) -> int:
    """Top-k documents by score (ties: lower document id); the suffix starts at the earliest of them."""
    ids = doc_ids if doc_ids is not None else list(range(len(scores)))
    top = sorted(range(len(scores)), key=lambda i: (-scores[i], ids[i]))[:k]
    return min(top)


def normalize_answer(text: str) -> str:
    text = "".join(" " if ch in string.punctuation else ch for ch in text.lower())
    return " ".join(re.sub(r"\b(a|an|the)\b", " ", text).split())


# ----------------------------------------------------------------------------------------------- CLI
EXAMPLE = {  # fictional, so the answer cannot come from the model's memory
    "question": "In which city was the director of the film Lanterns over Varn born?",
    "documents": [
        {"title": "Varn Peninsula", "text": "The Varn Peninsula is a rocky headland known for its lighthouses and "
                                            "its winter fishing season."},
        {"title": "Northern Coast Film Festival", "text": "The Northern Coast Film Festival is held every August in "
                                                          "the harbour town of Kessel."},
        {"title": "Lanterns over Varn", "text": "Lanterns over Varn is a 1994 drama film directed by Ilse Moravec. "
                                                "It follows a lighthouse keeper on the northern coast."},
        {"title": "Ilse Moravec", "text": "Ilse Moravec (born 12 March 1951 in Graz) is an Austrian film director "
                                          "and screenwriter."},
    ],
}


def _print_rows(res: dict):
    print(f"{'method':<20} {'re-encoded':>10}  {'= full prefill':>14}  answer")
    for name, r in res.items():
        print(f"{name:<20} {100 * r['recompute_ratio']:>9.1f}%  {('yes' if r['equivalent'] else 'NO'):>14}  {r['answer']!r}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--dtype", default="auto", choices=["auto", "float32", "float16", "bfloat16"])
    ap.add_argument("--jsonl", help="evaluate a JSONL file in the artifact's schema (id, question, documents[...])")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--k", type=int, default=2, help="selector top-k; the suffix starts at the earliest selected doc")
    ap.add_argument("--selector", default="query", choices=["query", "risk"])
    ap.add_argument("--start", type=int, help="1-based start document (overrides the selector)")
    ap.add_argument("--max-new-tokens", type=int, default=16)
    ap.add_argument("--out", help="write per-example results to this JSONL file")
    a = ap.parse_args(argv)

    dtype = {"auto": torch.float32 if a.device == "cpu" else torch.float16, "float32": torch.float32,
             "float16": torch.float16, "bfloat16": torch.bfloat16}[a.dtype]
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=dtype).to(a.device)
    skv = SafeKV(model, tok, a.max_new_tokens)

    def start_for(rec):
        if a.start is not None:
            return a.start - 1
        docs = rec["documents"]
        scores = risk_scores(rec) if a.selector == "risk" else query_scores(rec["question"], docs)
        return select_start(scores, a.k, [int(d.get("doc_id", i)) for i, d in enumerate(docs)])

    if not a.jsonl:
        s = start_for(EXAMPLE)
        print(f"Q: {EXAMPLE['question']}\n{len(EXAMPLE['documents'])} documents; suffix repair starts at document {s + 1}"
              f" ({'--start' if a.start else f'{a.selector} selector, K={a.k}'})\n")
        _print_rows(skv.run(render_prompt(tok, EXAMPLE["documents"], EXAMPLE["question"]), s))
        return

    rows = [json.loads(l) for l in open(a.jsonl, encoding="utf-8") if l.strip()][: a.limit]
    agg: dict[str, list] = {}
    out = open(a.out, "w", encoding="utf-8") if a.out else None
    t0 = time.time()
    for n, rec in enumerate(rows, 1):
        s = start_for(rec)
        res = skv.run(render_prompt(tok, rec["documents"], rec["question"]), s)
        for name, r in res.items():
            agg.setdefault(name, []).append((r["equivalent"], r["recompute_ratio"]))
        if out:
            out.write(json.dumps({"id": rec.get("id"), "start_doc": s + 1, **res}) + "\n")
        print(f"\r{n}/{len(rows)} examples ({time.time() - t0:.0f}s)", end="", file=sys.stderr)
    print(file=sys.stderr)
    how = f"start document {a.start}" if a.start is not None else f"{a.selector} selector, K={a.k}"
    print(f"{a.jsonl}: {len(rows)} examples, {how}")
    print(f"{'method':<20} {'answer preservation':>20} {'avg re-encoded':>15}")
    for name, v in agg.items():
        print(f"{name:<20} {100 * sum(e for e, _ in v) / len(v):>19.1f}% {100 * sum(r for _, r in v) / len(v):>14.1f}%")


if __name__ == "__main__":
    main()
