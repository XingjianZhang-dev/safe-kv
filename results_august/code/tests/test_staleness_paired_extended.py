from __future__ import annotations

from collections import defaultdict

import numpy as np
import pytest

from scripts.summarize_staleness_paired import (
    PAIRWISE_METHODS,
    endpoint_interaction_summaries,
    pairwise_method_summaries,
)


METHODS = (
    "mixed_no_repair",
    "query_actual_doc_only_k1",
    "query_actual_downstream_w4_k1",
    "query_actual_suffix_k1",
    "risk_actual_suffix_k1",
    "risk_actual_suffix_k2",
    "earliest_stale_actual_suffix_oracle",
)


def synthetic_values():
    values = defaultdict(list)
    for example_id in ("a", "b"):
        for num_documents in (1, 2):
            for probability in (0.0, 1.0):
                for method in METHODS:
                    answer = 1.0
                    if num_documents == 2 and probability == 1.0:
                        if method in {
                            "mixed_no_repair",
                            "query_actual_doc_only_k1",
                            "query_actual_downstream_w4_k1",
                        }:
                            answer = 0.0
                    for _seed in (13, 29, 47):
                        values[(example_id, num_documents, probability, method)].append(
                            {
                                "answer_equivalence_to_fresh_reference": answer,
                                "generated_token_sequence_equivalent_to_fresh_reference": answer,
                                "recomputed_token_ratio": (
                                    0.8 if "suffix" in method else 0.2
                                ),
                            }
                        )
    return values


def test_pairwise_suffix_minus_local_and_endpoint_interaction() -> None:
    values = synthetic_values()
    examples = ["a", "b"]
    cells = [(1, 0.0), (1, 1.0), (2, 0.0), (2, 1.0)]
    bootstrap = np.asarray([[0, 1], [1, 1], [0, 0]], dtype=np.int64)
    pairwise = pairwise_method_summaries(
        values=values,
        example_ids=examples,
        cells=cells,
        bootstrap_indices=bootstrap,
    )
    target = next(
        row
        for row in pairwise
        if row["comparison"] == "query_suffix_vs_query_doc_only_k1"
        and row["num_documents"] == 2
        and row["stale_probability"] == 1.0
    )
    assert target["normalized_answer_delta"] == 1.0
    assert target["recomputed_context_ratio_delta"] == pytest.approx(0.6)
    assert len(pairwise) == len(cells) * len(PAIRWISE_METHODS)

    interactions = endpoint_interaction_summaries(
        values=values,
        example_ids=examples,
        methods=list(METHODS),
        cells=cells,
        bootstrap_indices=bootstrap,
    )
    no_repair = next(row for row in interactions if row["method"] == "mixed_no_repair")
    suffix = next(row for row in interactions if row["method"] == "query_actual_suffix_k1")
    assert no_repair["normalized_answer_endpoint_interaction"] == -1.0
    assert suffix["normalized_answer_endpoint_interaction"] == 0.0
