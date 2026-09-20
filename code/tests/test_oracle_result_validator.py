import hashlib

from scripts.validate_oracle_kv_drift_results import (
    CandidatePositionAudit,
    validate_range_audit_fields,
)


def positions_hash(positions):
    digest = hashlib.sha256()
    for position in positions:
        digest.update(int(position).to_bytes(8, byteorder="big", signed=False))
    return digest.hexdigest()


def range_row(*, ranges, positions, context_count=8, candidate_count=3):
    return {
        "example_id": "example",
        "method": "oracle_kv_drift_token_local_p1",
        "context_token_count": context_count,
        "candidate_document_token_count": candidate_count,
        "patched_token_count": len(positions),
        "patched_ranges": ranges,
        "patched_positions_sha256": positions_hash(positions),
        "patched_context_ratio": len(positions) / context_count,
        "patched_document_token_ratio": len(positions) / candidate_count,
    }


def test_range_audit_accepts_reconstructed_document_positions():
    expected = CandidatePositionAudit(
        context_token_count=8,
        candidate_positions=(2, 3, 4),
    )
    row = range_row(
        ranges=[{"start": 2, "end": 5}],
        positions=[2, 3, 4],
    )
    failures = []

    validate_range_audit_fields(
        row,
        failures,
        required=True,
        expected=expected,
        reconstruction_required=True,
    )

    assert failures == []


def test_range_audit_rejects_equal_count_prefix_substitution():
    """Same count, ratio, and valid hash must not substitute prefix for docs."""

    expected = CandidatePositionAudit(
        context_token_count=8,
        candidate_positions=(2, 3, 4),
    )
    row = range_row(
        ranges=[{"start": 0, "end": 3}],
        positions=[0, 1, 2],
    )
    failures = []

    validate_range_audit_fields(
        row,
        failures,
        required=True,
        expected=expected,
        reconstruction_required=True,
    )

    assert any("leave reconstructed document candidates" in item for item in failures)


def test_range_audit_recomputes_saved_ratios():
    expected = CandidatePositionAudit(
        context_token_count=8,
        candidate_positions=(2, 3, 4),
    )
    row = range_row(
        ranges=[{"start": 2, "end": 5}],
        positions=[2, 3, 4],
    )
    row["patched_document_token_ratio"] = 0.5
    failures = []

    validate_range_audit_fields(
        row,
        failures,
        required=True,
        expected=expected,
        reconstruction_required=True,
    )

    assert any("document ratio/count mismatch" in item for item in failures)

