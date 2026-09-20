import numpy as np
import json

from scripts.analyze_answer_grid_bootstrap import (
    METRIC_FIELDS,
    build_dataset_arrays,
    load_source,
    make_scope_rows,
)


def test_answer_grid_arrays_require_and_preserve_pairing():
    records = []
    for condition in ("natural", "shuffle"):
        for group_index in range(2):
            for method_index, method in enumerate(("full", "reuse")):
                records.append(
                    {
                        "dataset": "toy",
                        "condition": condition,
                        "group_id": f"toy:{group_index}",
                        "example_id": f"{condition}:{group_index}",
                        "method": method,
                        "values": [float(method_index)] * len(METRIC_FIELDS),
                    }
                )
    arrays, groups = build_dataset_arrays(
        records,
        datasets=["toy"],
        conditions=["natural", "shuffle"],
        methods=["full", "reuse"],
    )
    assert groups == {"toy": ["toy:0", "toy:1"]}
    assert arrays["toy"].shape == (2, 2, 2, len(METRIC_FIELDS))
    assert np.all(arrays["toy"][:, :, 0] == 0.0)
    assert np.all(arrays["toy"][:, :, 1] == 1.0)


def test_scope_rows_report_paired_delta():
    point = np.asarray([[1.0] * len(METRIC_FIELDS), [0.25] * len(METRIC_FIELDS)])
    draws = np.stack([point, point], axis=0)
    methods, pairs = make_scope_rows(
        point,
        draws,
        scope="overall",
        methods=["left", "right"],
        pairs=[("left", "right")],
        n_groups=2,
        n_condition_rows=4,
    )
    assert len(methods) == 2 * len(METRIC_FIELDS)
    assert len(pairs) == len(METRIC_FIELDS)
    assert all(row["delta_left_minus_right"] == 0.75 for row in pairs)


def test_load_answer_source_maps_test_metadata_and_metrics(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    data_path = tmp_path / "data.jsonl"
    data_path.write_text(
        json.dumps(
            {
                "id": "e1",
                "source_metadata": {
                    "dataset": "toy",
                    "retrieval_condition": "natural",
                    "split": "test",
                    "source_id": "s1",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    from safekv_ipm.run_registry import sha256_file

    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "exit_code": 0,
                "inputs": [{"path": str(data_path), "sha256": sha256_file(data_path)}],
            }
        ),
        encoding="utf-8",
    )
    rows = []
    for method in ("full", "reuse"):
        row = {"example_id": "e1", "method": method}
        for _metric, field, boolean in METRIC_FIELDS:
            row[field] = True if boolean else 0.5
        row["context_token_count"] = 2
        row["online_context_prefill_token_count"] = 1
        rows.append(row)
    (run_dir / "answer_eval_outputs.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )

    records, source = load_source(
        run_dir, data_path, methods=["full", "reuse"], expected_examples=1
    )
    assert len(records) == 2
    assert records[0]["group_id"] == "toy:s1"
    assert source["dataset"] == "toy"


def test_analysis_uses_explicit_online_compute_not_legacy_patch_ratio(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    data_path = tmp_path / "data.jsonl"
    data_path.write_text(
        json.dumps(
            {
                "id": "e1",
                "source_metadata": {
                    "dataset": "toy",
                    "retrieval_condition": "natural",
                    "split": "test",
                    "source_id": "s1",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    from safekv_ipm.run_registry import sha256_file

    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "exit_code": 0,
                "inputs": [{"path": str(data_path), "sha256": sha256_file(data_path)}],
            }
        ),
        encoding="utf-8",
    )
    row = {"example_id": "e1", "method": "full"}
    for _metric, field, boolean in METRIC_FIELDS:
        row[field] = True if boolean else 0.5
    row["online_context_prefill_fraction"] = 1.0
    row["context_token_count"] = 10
    row["online_context_prefill_token_count"] = 10
    row["patched_token_ratio"] = 0.0
    (run_dir / "answer_eval_outputs.jsonl").write_text(
        json.dumps(row) + "\n", encoding="utf-8"
    )

    records, _source = load_source(
        run_dir, data_path, methods=["full"], expected_examples=1
    )
    metric_index = [name for name, _field, _boolean in METRIC_FIELDS].index(
        "online_context_prefill_fraction"
    )
    assert records[0]["values"][metric_index] == 1.0
