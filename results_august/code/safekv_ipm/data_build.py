"""Build leakage-controlled RAG inputs from official multi-hop QA releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol

BUILDER_SCHEMA_VERSION = 1
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


@dataclass(frozen=True)
class SourceDocument:
    source_index: int
    title: str
    text: str
    evidence_texts: tuple[str, ...]


@dataclass(frozen=True)
class SourceExample:
    source_id: str
    category: str
    question: str
    answer: str
    documents: tuple[SourceDocument, ...]


class DenseRanker(Protocol):
    model_name: str
    revision: str

    def scores(self, question: str, documents: list[str]) -> list[float]: ...


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_key(seed: int, namespace: str, value: str) -> str:
    return hashlib.sha256(f"{seed}:{namespace}:{value}".encode()).hexdigest()


def normalize_scores(scores: list[float]) -> list[float]:
    if not scores:
        return []
    low, high = min(scores), max(scores)
    if math.isclose(low, high, rel_tol=0.0, abs_tol=1e-12):
        return [0.0 for _ in scores]
    return [(score - low) / (high - low) for score in scores]


def bm25_scores(question: str, documents: list[str]) -> list[float]:
    from rank_bm25 import BM25Okapi

    corpus = [TOKEN_RE.findall(text.lower()) for text in documents]
    query = TOKEN_RE.findall(question.lower())
    if not query or not any(corpus):
        return [0.0 for _ in documents]
    return [float(value) for value in BM25Okapi(corpus).get_scores(query)]


class SentenceTransformerRanker:
    def __init__(
        self,
        load_source: str,
        model_name: str,
        revision: str,
        device: str,
    ) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.revision = revision
        self._model = SentenceTransformer(
            load_source,
            revision=revision,
            device=device,
        )

    def scores(self, question: str, documents: list[str]) -> list[float]:
        import numpy as np

        query = "Represent this sentence for searching relevant passages: " + question
        query_vector = self._model.encode([query], normalize_embeddings=True)[0]
        document_vectors = self._model.encode(
            documents,
            normalize_embeddings=True,
            batch_size=64,
        )
        return [float(value) for value in np.asarray(document_vectors) @ query_vector]


def _join_sentences(sentences: Iterable[Any]) -> str:
    return " ".join(str(sentence).strip() for sentence in sentences if str(sentence).strip())


def parse_hotpot(path: Path) -> list[SourceExample]:
    import pyarrow.parquet as pq

    examples: list[SourceExample] = []
    for row in pq.read_table(path).to_pylist():
        context = row["context"]
        support = row["supporting_facts"]
        support_by_title: dict[str, list[int]] = {}
        for title, sentence_id in zip(support["title"], support["sent_id"]):
            support_by_title.setdefault(str(title), []).append(int(sentence_id))
        documents: list[SourceDocument] = []
        for index, (title, sentences) in enumerate(
            zip(context["title"], context["sentences"])
        ):
            title = str(title)
            sentences = [str(sentence).strip() for sentence in sentences]
            evidence_texts = tuple(
                sentences[sentence_id]
                for sentence_id in support_by_title.get(title, [])
                if 0 <= sentence_id < len(sentences) and sentences[sentence_id]
            )
            documents.append(
                SourceDocument(index, title, _join_sentences(sentences), evidence_texts)
            )
        examples.append(
            SourceExample(
                source_id=str(row["id"]),
                category="external_hotpotqa",
                question=str(row["question"]),
                answer=str(row["answer"]),
                documents=tuple(documents),
            )
        )
    return examples


def parse_2wiki(path: Path) -> list[SourceExample]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    examples: list[SourceExample] = []
    for row in rows:
        support_by_title: dict[str, list[int]] = {}
        for title, sentence_id in row.get("supporting_facts", []):
            support_by_title.setdefault(str(title), []).append(int(sentence_id))
        documents: list[SourceDocument] = []
        for index, (title, sentences) in enumerate(row["context"]):
            title = str(title)
            sentences = [str(sentence).strip() for sentence in sentences]
            evidence_texts = tuple(
                sentences[sentence_id]
                for sentence_id in support_by_title.get(title, [])
                if 0 <= sentence_id < len(sentences) and sentences[sentence_id]
            )
            documents.append(
                SourceDocument(index, title, _join_sentences(sentences), evidence_texts)
            )
        examples.append(
            SourceExample(
                source_id=str(row["_id"]),
                category="external_2wiki",
                question=str(row["question"]),
                answer=str(row["answer"]),
                documents=tuple(documents),
            )
        )
    return examples


def parse_musique(path: Path) -> list[SourceExample]:
    examples: list[SourceExample] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if not bool(row.get("answerable", True)):
                continue
            documents: list[SourceDocument] = []
            for source_index, paragraph in enumerate(row["paragraphs"]):
                text = str(paragraph["paragraph_text"]).strip()
                evidence_texts = (text,) if paragraph.get("is_supporting") else ()
                documents.append(
                    SourceDocument(
                        source_index=source_index,
                        title=str(paragraph["title"]),
                        text=text,
                        evidence_texts=evidence_texts,
                    )
                )
            examples.append(
                SourceExample(
                    source_id=str(row["id"]),
                    category="external_musique",
                    question=str(row["question"]),
                    answer=str(row["answer"]),
                    documents=tuple(documents),
                )
            )
    return examples


def validate_source(example: SourceExample) -> str | None:
    if not example.question.strip() or not example.answer.strip():
        return "missing_question_or_answer"
    if len(example.documents) < 2:
        return "fewer_than_two_documents"
    if any(not document.text for document in example.documents):
        return "empty_document"
    evidence_documents = [doc for doc in example.documents if doc.evidence_texts]
    if len(evidence_documents) < 2:
        return "fewer_than_two_evidence_documents"
    for document in evidence_documents:
        if any(text not in document.text for text in document.evidence_texts):
            return "evidence_not_in_document"
    return None


def order_documents(
    example: SourceExample,
    condition: str,
    seed: int,
    dense_ranker: DenseRanker | None,
) -> tuple[list[SourceDocument], list[float]]:
    documents = list(example.documents)
    texts = [f"{doc.title}\n{doc.text}" for doc in documents]
    if condition == "natural":
        return documents, [0.0] * len(documents)
    if condition == "shuffle":
        rng = random.Random(int(stable_key(seed, "shuffle", example.source_id)[:16], 16))
        order = list(range(len(documents)))
        rng.shuffle(order)
        return [documents[index] for index in order], [0.0] * len(documents)
    if condition == "bm25":
        scores = normalize_scores(bm25_scores(example.question, texts))
    elif condition == "dense":
        if dense_ranker is None:
            raise ValueError("dense condition requires a dense ranker")
        scores = normalize_scores(dense_ranker.scores(example.question, texts))
    else:
        raise ValueError(f"unknown retrieval condition: {condition}")
    order = sorted(range(len(documents)), key=lambda index: (-scores[index], index))
    return [documents[index] for index in order], [scores[index] for index in order]


def convert_example(
    example: SourceExample,
    *,
    dataset: str,
    split: str,
    condition: str,
    seed: int,
    dense_ranker: DenseRanker | None,
) -> dict[str, Any]:
    ordered, ordered_scores = order_documents(example, condition, seed, dense_ranker)
    documents: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    evidence_ranks: list[int] = []
    source_doc_indices: list[int] = []
    for new_id, (document, score) in enumerate(zip(ordered, ordered_scores)):
        source_doc_indices.append(document.source_index)
        is_evidence = bool(document.evidence_texts)
        documents.append(
            {
                "doc_id": new_id,
                "title": document.title,
                "text": document.text,
                "role": "evidence" if is_evidence else "distractor",
                "retrieval_score": float(score),
                "source_doc_index": document.source_index,
            }
        )
        if is_evidence:
            evidence_ranks.append(new_id + 1)
            for text in dict.fromkeys(document.evidence_texts):
                evidence.append({"doc_id": new_id, "text": text})
    return {
        "id": f"{dataset}_{example.source_id}",
        "category": example.category,
        "documents": documents,
        "question": example.question,
        "gold_answer": example.answer,
        "evidence": evidence,
        "conflicting_docs": [],
        "requires_cross_doc": len(evidence_ranks) > 1,
        "source_metadata": {
            "dataset": dataset,
            "source_id": example.source_id,
            "split": split,
            "retrieval_condition": condition,
            "source_doc_indices_in_prompt_order": source_doc_indices,
            "evidence_ranks_one_based": evidence_ranks,
            "gold_labels_used_for_ranking": False,
            "ranking_model": (
                {
                    "name": dense_ranker.model_name,
                    "revision": dense_ranker.revision,
                }
                if condition == "dense" and dense_ranker is not None
                else None
            ),
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_path = Path(args.input).resolve()
    parsers = {"hotpotqa": parse_hotpot, "2wiki": parse_2wiki, "musique": parse_musique}
    parsed = parsers[args.dataset](source_path)
    rejection_counts: Counter[str] = Counter()
    valid: list[SourceExample] = []
    for example in parsed:
        reason = validate_source(example)
        if reason is None:
            valid.append(example)
        else:
            rejection_counts[reason] += 1
    valid.sort(key=lambda example: stable_key(args.seed, "split", example.source_id))
    required = args.calibration_size + args.test_size
    if len(valid) < required:
        raise ValueError(f"need {required} valid examples, found {len(valid)}")
    split_examples = {
        "calibration": valid[: args.calibration_size],
        "test": valid[args.calibration_size : required],
    }
    conditions = [item.strip() for item in args.conditions.split(",") if item.strip()]
    if len(conditions) != len(set(conditions)):
        raise ValueError("conditions must not contain duplicates")
    unknown = set(conditions) - {"natural", "shuffle", "bm25", "dense"}
    if unknown:
        raise ValueError(f"unknown conditions: {sorted(unknown)}")
    dense_ranker: DenseRanker | None = None
    if "dense" in conditions:
        if not args.dense_model or not args.dense_revision:
            raise ValueError("dense condition requires --dense-model and --dense-revision")
        dense_ranker = SentenceTransformerRanker(
            args.dense_model,
            args.dense_model_id or args.dense_model,
            args.dense_revision,
            args.dense_device,
        )
    output_dir = Path(args.output_dir).resolve()
    outputs: dict[str, Any] = {}
    for condition in conditions:
        for split, examples in split_examples.items():
            rows = [
                convert_example(
                    example,
                    dataset=args.dataset,
                    split=split,
                    condition=condition,
                    seed=args.seed,
                    dense_ranker=dense_ranker,
                )
                for example in examples
            ]
            path = output_dir / f"{args.dataset}_{condition}_{split}.jsonl"
            write_jsonl(path, rows)
            evidence_ranks = [
                rank
                for row in rows
                for rank in row["source_metadata"]["evidence_ranks_one_based"]
            ]
            outputs[f"{condition}:{split}"] = {
                "path": str(path),
                "sha256": sha256_file(path),
                "num_examples": len(rows),
                "mean_document_count": sum(len(row["documents"]) for row in rows) / len(rows),
                "mean_evidence_rank": sum(evidence_ranks) / len(evidence_ranks),
                "max_evidence_rank": max(evidence_ranks),
            }
    manifest = {
        "schema_version": BUILDER_SCHEMA_VERSION,
        "dataset": args.dataset,
        "source_path": str(source_path),
        "source_sha256": sha256_file(source_path),
        "source_url": args.source_url,
        "source_revision": args.source_revision,
        "source_license": args.source_license,
        "seed": args.seed,
        "calibration_size": args.calibration_size,
        "test_size": args.test_size,
        "conditions": conditions,
        "num_source_examples": len(parsed),
        "num_valid_examples": len(valid),
        "rejection_counts": dict(sorted(rejection_counts.items())),
        "gold_labels_used_for_ranking": False,
        "dense_model": (
            args.dense_model_id or args.dense_model
            if "dense" in conditions
            else None
        ),
        "dense_model_load_source": args.dense_model if "dense" in conditions else None,
        "dense_revision": args.dense_revision if "dense" in conditions else None,
        "outputs": outputs,
    }
    manifest_path = output_dir / f"{args.dataset}_build_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=["hotpotqa", "2wiki", "musique"])
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--source-license", required=True)
    parser.add_argument("--conditions", default="natural,shuffle,bm25")
    parser.add_argument("--calibration-size", type=int, default=300)
    parser.add_argument("--test-size", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--dense-model")
    parser.add_argument("--dense-model-id")
    parser.add_argument("--dense-revision")
    parser.add_argument("--dense-device", default="cuda")
    return parser.parse_args()


def main() -> None:
    manifest = build(parse_args())
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
