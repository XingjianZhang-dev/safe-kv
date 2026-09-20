"""External multi-hop QA conversion for SAFE-KV Milestone 6C."""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from safekv.build_diagnostic import write_jsonl
from safekv.data_schema import DiagnosticExample, Document, EvidenceSpan
from safekv.patch_recompute import lexical_terms


YES_NO_ANSWERS = {"yes", "no"}
DEFAULT_MAX_DISTRACTORS = 3
DEFAULT_MAX_DOC_CHARS = 1800
DEFAULT_MAX_CONTEXT_DOCS = 12


@dataclass(frozen=True)
class ExternalBuildResult:
    examples: list[DiagnosticExample]
    summary: dict[str, Any]


def build_hotpotqa_examples(
    records: Iterable[dict[str, Any]],
    *,
    n: int,
    seed: int = 13,
    max_distractors: int = DEFAULT_MAX_DISTRACTORS,
) -> ExternalBuildResult:
    return _build_examples(
        records,
        n=n,
        seed=seed,
        dataset_name="hotpotqa",
        category="external_hotpotqa",
        converter=lambda record, index: hotpotqa_record_to_example(
            record,
            example_index=index,
            max_distractors=max_distractors,
        ),
    )


def build_2wiki_examples(
    records: Iterable[dict[str, Any]],
    *,
    n: int,
    seed: int = 13,
    max_distractors: int = DEFAULT_MAX_DISTRACTORS,
) -> ExternalBuildResult:
    return _build_examples(
        records,
        n=n,
        seed=seed,
        dataset_name="2wiki",
        category="external_2wiki",
        converter=lambda record, index: twowiki_record_to_example(
            record,
            example_index=index,
            max_distractors=max_distractors,
        ),
    )


def hotpotqa_record_to_example(
    record: dict[str, Any],
    *,
    example_index: int,
    max_distractors: int = DEFAULT_MAX_DISTRACTORS,
) -> DiagnosticExample | None:
    answer = _clean_answer(record.get("answer"))
    if not answer or answer.lower() in YES_NO_ANSWERS:
        return None

    contexts = _parse_context(record.get("context"))
    if not contexts:
        return None

    support_by_title = _parse_supporting_facts(record.get("supporting_facts"))
    support_titles = set(support_by_title)
    if len(support_titles) < 2:
        return None

    selected = _select_contexts(
        contexts,
        question=str(record.get("question", "")),
        evidence_titles=support_titles,
        max_distractors=max_distractors,
    )
    if len([item for item in selected if item[0] in support_titles]) < 2:
        return None

    return _contexts_to_example(
        selected,
        answer=answer,
        question=str(record.get("question", "")).strip(),
        category="external_hotpotqa",
        example_id=f"hotpotqa_{example_index:04d}",
        evidence_titles=support_titles,
        support_by_title=support_by_title,
    )


def twowiki_record_to_example(
    record: dict[str, Any],
    *,
    example_index: int,
    max_distractors: int = DEFAULT_MAX_DISTRACTORS,
) -> DiagnosticExample | None:
    answer = _clean_answer(record.get("answer"))
    if not answer or answer.lower() in YES_NO_ANSWERS:
        return None

    contexts = _parse_context(record.get("context"))
    if not contexts:
        return None

    support_by_title = _parse_2wiki_support(record, contexts, answer)
    support_titles = set(support_by_title)
    if len(support_titles) < 2:
        return None

    selected = _select_contexts(
        contexts,
        question=str(record.get("question", "")),
        evidence_titles=support_titles,
        max_distractors=max_distractors,
    )
    if len([item for item in selected if item[0] in support_titles]) < 2:
        return None

    raw_id = record.get("_id") or record.get("id") or record.get("qid")
    suffix = _safe_id(str(raw_id)) if raw_id else f"{example_index:04d}"
    return _contexts_to_example(
        selected,
        answer=answer,
        question=str(record.get("question", "")).strip(),
        category="external_2wiki",
        example_id=f"2wiki_{suffix}",
        evidence_titles=support_titles,
        support_by_title=support_by_title,
    )


def load_hotpotqa_records(input_json: str | Path | None = None) -> list[dict[str, Any]]:
    if input_json is not None:
        return load_local_records(input_json)

    from datasets import get_dataset_config_names, load_dataset

    errors: list[str] = []
    repos = ["hotpotqa/hotpot_qa", "hotpot_qa"]
    configs: list[str | None] = ["distractor", None]
    try:
        names = get_dataset_config_names(repos[0])
        configs = ["distractor"] if "distractor" in names else list(names) + [None]
    except Exception as exc:  # pragma: no cover - network dependent
        errors.append(f"get_dataset_config_names({repos[0]!r}) failed: {exc!r}")

    for repo in repos:
        for config in configs:
            for split in ("validation", "dev", "train"):
                try:
                    dataset = load_dataset(repo, config, split=split) if config else load_dataset(
                        repo,
                        split=split,
                    )
                    return [dict(row) for row in dataset]
                except Exception as exc:  # pragma: no cover - network dependent
                    errors.append(f"{repo} config={config!r} split={split!r}: {exc!r}")
    raise RuntimeError(
        "Could not load HotpotQA from Hugging Face. Use --input-json with a local "
        "HotpotQA distractor-format JSON file. Errors: " + " | ".join(errors[-5:])
    )


def load_2wiki_records(input_json: str | Path | None = None) -> list[dict[str, Any]]:
    if input_json is not None:
        return load_local_records(input_json)

    from datasets import load_dataset

    errors: list[str] = []
    for repo in ("xanhho/2WikiMultihopQA", "framolfese/2WikiMultihopQA"):
        for split in ("validation", "dev", "train"):
            try:
                dataset = load_dataset(repo, split=split)
                return [dict(row) for row in dataset]
            except Exception as exc:  # pragma: no cover - network dependent
                errors.append(f"{repo} split={split!r}: {exc!r}")
    raise RuntimeError(
        "Could not load 2WikiMultihopQA from Hugging Face. Use --input-json with a "
        "local 2Wiki JSON file. Errors: " + " | ".join(errors[-5:])
    )


def load_local_records(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [dict(row) for row in data]
    if isinstance(data, dict):
        for key in ("data", "examples", "records", "validation", "dev", "train"):
            value = data.get(key)
            if isinstance(value, list):
                return [dict(row) for row in value]
    raise ValueError(f"unsupported local JSON structure: {path}")


def write_external_jsonl(result: ExternalBuildResult, path: str | Path) -> None:
    out_path = Path(path)
    write_jsonl(result.examples, out_path)
    summary_path = out_path.with_suffix(out_path.suffix + ".summary.json")
    summary_path.write_text(
        json.dumps(result.summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _build_examples(
    records: Iterable[dict[str, Any]],
    *,
    n: int,
    seed: int,
    dataset_name: str,
    category: str,
    converter,
) -> ExternalBuildResult:
    if n <= 0:
        raise ValueError("n must be positive")

    indexed = list(enumerate(records))
    rng = random.Random(seed)
    rng.shuffle(indexed)

    examples: list[DiagnosticExample] = []
    skipped: Counter[str] = Counter()
    seen_ids: set[str] = set()
    for raw_index, record in indexed:
        if len(examples) >= n:
            break
        reason = _skip_reason(record)
        if reason is not None:
            skipped[reason] += 1
            continue
        try:
            example = converter(record, raw_index)
        except Exception as exc:
            skipped[f"parse_error:{type(exc).__name__}"] += 1
            continue
        if example is None:
            skipped["conversion_filter"] += 1
            continue
        if example.id in seen_ids:
            skipped["duplicate_id"] += 1
            continue
        try:
            example.validate()
        except Exception as exc:
            skipped[f"validation_error:{type(exc).__name__}"] += 1
            continue
        examples.append(example)
        seen_ids.add(example.id)

    summary = _summary(
        examples,
        dataset_name=dataset_name,
        category=category,
        requested_n=n,
        total_records=len(indexed),
        skipped=skipped,
        seed=seed,
    )
    return ExternalBuildResult(examples=examples, summary=summary)


def _skip_reason(record: dict[str, Any]) -> str | None:
    answer = _clean_answer(record.get("answer"))
    if not answer:
        return "empty_answer"
    if answer.lower() in YES_NO_ANSWERS:
        return "yes_no_answer"
    if not str(record.get("question", "")).strip():
        return "empty_question"
    return None


def _contexts_to_example(
    contexts: list[tuple[str, list[str]]],
    *,
    answer: str,
    question: str,
    category: str,
    example_id: str,
    evidence_titles: set[str],
    support_by_title: dict[str, set[int]],
) -> DiagnosticExample | None:
    documents: list[Document] = []
    evidence: list[EvidenceSpan] = []
    evidence_doc_count = 0

    for doc_id, (title, sentences) in enumerate(contexts):
        trimmed_sentences = [_normalize_sentence(sentence) for sentence in sentences]
        trimmed_sentences = [sentence for sentence in trimmed_sentences if sentence]
        if not trimmed_sentences:
            continue
        text = " ".join(trimmed_sentences)
        if len(text) > DEFAULT_MAX_DOC_CHARS:
            text = _truncate_doc_text(text, answer=answer)
        role = "evidence" if title in evidence_titles else "distractor"
        retrieval_score = 1.0 if role == "evidence" else round(max(0.05, 0.55 - 0.05 * doc_id), 3)
        documents.append(
            Document(
                doc_id=doc_id,
                title=title,
                text=text,
                role=role,
                retrieval_score=retrieval_score,
            )
        )
        if role == "evidence":
            evidence_doc_count += 1
            span_texts = _evidence_texts_for_doc(title, trimmed_sentences, support_by_title, answer)
            for span_text in span_texts:
                if span_text in text:
                    evidence.append(EvidenceSpan(doc_id=doc_id, text=span_text))

    if len(documents) < 2 or evidence_doc_count < 2 or not evidence:
        return None
    example = DiagnosticExample(
        id=example_id,
        category=category,  # type: ignore[arg-type]
        documents=documents,
        question=question,
        gold_answer=answer,
        evidence=evidence,
        conflicting_docs=[],
        requires_cross_doc=True,
    )
    example.validate()
    return example


def _parse_context(raw: Any) -> list[tuple[str, list[str]]]:
    contexts: list[tuple[str, list[str]]] = []
    if isinstance(raw, dict):
        titles = raw.get("title") or raw.get("titles")
        sentences = raw.get("sentences") or raw.get("sentence") or raw.get("text")
        if isinstance(titles, list) and isinstance(sentences, list):
            for title, sentence_list in zip(titles, sentences, strict=False):
                contexts.append((_clean_title(title), _coerce_sentences(sentence_list)))
    elif isinstance(raw, list):
        for item in raw:
            parsed = _parse_context_item(item)
            if parsed is not None:
                contexts.append(parsed)

    deduped: list[tuple[str, list[str]]] = []
    seen: set[str] = set()
    for title, sentences in contexts[:DEFAULT_MAX_CONTEXT_DOCS]:
        if not title or not sentences or title in seen:
            continue
        deduped.append((title, sentences))
        seen.add(title)
    return deduped


def _parse_context_item(item: Any) -> tuple[str, list[str]] | None:
    if isinstance(item, dict):
        title = item.get("title") or item.get("name") or item.get("doc_title")
        sentences = item.get("sentences") or item.get("sentence") or item.get("text")
        return (_clean_title(title), _coerce_sentences(sentences))
    if isinstance(item, (list, tuple)) and len(item) >= 2:
        return (_clean_title(item[0]), _coerce_sentences(item[1]))
    return None


def _parse_supporting_facts(raw: Any) -> dict[str, set[int]]:
    support: dict[str, set[int]] = {}
    if isinstance(raw, dict):
        titles = raw.get("title") or raw.get("titles")
        sent_ids = raw.get("sent_id") or raw.get("sent_ids") or raw.get("sentence_id")
        if isinstance(titles, list):
            for index, title in enumerate(titles):
                sent_id = sent_ids[index] if isinstance(sent_ids, list) and index < len(sent_ids) else None
                support.setdefault(_clean_title(title), set()).add(_coerce_int(sent_id, -1))
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                title = item.get("title") or item.get("doc_title") or item.get("name")
                sent_id = item.get("sent_id") or item.get("sentence_id") or item.get("sent_idx")
                support.setdefault(_clean_title(title), set()).add(_coerce_int(sent_id, -1))
            elif isinstance(item, (list, tuple)) and item:
                title = item[0]
                sent_id = item[1] if len(item) > 1 else -1
                support.setdefault(_clean_title(title), set()).add(_coerce_int(sent_id, -1))
    return {title: ids for title, ids in support.items() if title}


def _parse_2wiki_support(
    record: dict[str, Any],
    contexts: list[tuple[str, list[str]]],
    answer: str,
) -> dict[str, set[int]]:
    for key in ("supporting_facts", "supporting_facts_filtered", "evidence", "evidences"):
        parsed = _parse_supporting_facts(record.get(key))
        if parsed:
            return parsed

    titles = {title for title, _ in contexts}
    support: dict[str, set[int]] = {}
    for key in ("evidence", "evidences", "reasoning_path", "reasoning_paths"):
        raw = record.get(key)
        for title in _extract_titles_from_nested(raw, titles):
            support.setdefault(title, set()).add(-1)
    if support:
        return support

    answer_norm = answer.lower()
    for title, sentences in contexts:
        for index, sentence in enumerate(sentences):
            if answer_norm and answer_norm in sentence.lower():
                support.setdefault(title, set()).add(index)
    return support


def _extract_titles_from_nested(raw: Any, known_titles: set[str]) -> set[str]:
    found: set[str] = set()
    if raw is None:
        return found
    if isinstance(raw, str):
        for title in known_titles:
            if title and title in raw:
                found.add(title)
        return found
    if isinstance(raw, dict):
        for value in raw.values():
            found.update(_extract_titles_from_nested(value, known_titles))
        return found
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str) and item in known_titles:
                found.add(item)
            found.update(_extract_titles_from_nested(item, known_titles))
    return found


def _select_contexts(
    contexts: list[tuple[str, list[str]]],
    *,
    question: str,
    evidence_titles: set[str],
    max_distractors: int,
) -> list[tuple[str, list[str]]]:
    evidence = [item for item in contexts if item[0] in evidence_titles]
    distractors = [item for item in contexts if item[0] not in evidence_titles]
    question_terms = lexical_terms(question)

    def distractor_score(item: tuple[str, list[str]]) -> tuple[float, str]:
        title, sentences = item
        text = f"{title} {' '.join(sentences)}"
        terms = lexical_terms(text)
        overlap = len(question_terms & terms) / max(1, len(question_terms))
        return (-overlap, title)

    ranked_distractors = sorted(distractors, key=distractor_score)
    selected = evidence + ranked_distractors[:max_distractors]
    return selected


def _evidence_texts_for_doc(
    title: str,
    sentences: list[str],
    support_by_title: dict[str, set[int]],
    answer: str,
) -> list[str]:
    texts: list[str] = []
    for sent_id in sorted(support_by_title.get(title, set())):
        if 0 <= sent_id < len(sentences):
            texts.append(sentences[sent_id])
    if not texts:
        answer_norm = answer.lower()
        texts = [sentence for sentence in sentences if answer_norm in sentence.lower()]
    if not texts and sentences:
        texts = [sentences[0]]
    return texts[:3]


def _summary(
    examples: list[DiagnosticExample],
    *,
    dataset_name: str,
    category: str,
    requested_n: int,
    total_records: int,
    skipped: Counter[str],
    seed: int,
) -> dict[str, Any]:
    doc_counts = [len(example.documents) for example in examples]
    evidence_doc_counts = [
        len({evidence.doc_id for evidence in example.evidence}) for example in examples
    ]
    return {
        "dataset": dataset_name,
        "category": category,
        "seed": seed,
        "requested_n": requested_n,
        "num_examples": len(examples),
        "total_records_seen": total_records,
        "num_skipped": int(sum(skipped.values())),
        "skip_reasons": dict(sorted(skipped.items())),
        "yes_no_answers_removed": int(skipped.get("yes_no_answer", 0)),
        "avg_documents": _mean(doc_counts),
        "avg_evidence_documents": _mean(evidence_doc_counts),
        "min_documents": min(doc_counts) if doc_counts else 0,
        "max_documents": max(doc_counts) if doc_counts else 0,
    }


def _clean_answer(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _clean_title(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _coerce_sentences(value: Any) -> list[str]:
    if isinstance(value, str):
        return [_normalize_sentence(value)]
    if isinstance(value, list):
        sentences: list[str] = []
        for item in value:
            if isinstance(item, list):
                sentences.extend(_coerce_sentences(item))
            else:
                sentence = _normalize_sentence(str(item))
                if sentence:
                    sentences.append(sentence)
        return sentences
    return []


def _normalize_sentence(value: str) -> str:
    return " ".join(str(value).strip().split())


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _truncate_doc_text(text: str, *, answer: str) -> str:
    if len(text) <= DEFAULT_MAX_DOC_CHARS:
        return text
    answer_index = text.lower().find(answer.lower()) if answer else -1
    if answer_index >= 0:
        start = max(0, answer_index - DEFAULT_MAX_DOC_CHARS // 2)
        return text[start : start + DEFAULT_MAX_DOC_CHARS].strip()
    return text[:DEFAULT_MAX_DOC_CHARS].strip()


def _safe_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip())
    return safe[:80] or "unknown"


def _mean(values: Iterable[int | float]) -> float:
    values = [float(value) for value in values]
    return sum(values) / len(values) if values else 0.0


__all__ = [
    "ExternalBuildResult",
    "build_2wiki_examples",
    "build_hotpotqa_examples",
    "hotpotqa_record_to_example",
    "load_2wiki_records",
    "load_hotpotqa_records",
    "load_local_records",
    "twowiki_record_to_example",
    "write_external_jsonl",
]
