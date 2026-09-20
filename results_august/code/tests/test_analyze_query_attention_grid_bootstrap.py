import json

from scripts.analyze_query_attention_grid_bootstrap import (
    METRIC_FIELDS,
    load_source,
    method_contract,
)


def test_attention_method_contract_pairs_each_budget_with_seed_mean():
    actual, virtual, pairs = method_contract([0.1, 0.25], [13, 29, 47])
    assert len(actual) == 2 + 2 * 4
    assert virtual == [
        "random_local_actual_p0p1_seed_mean",
        "random_local_actual_p0p25_seed_mean",
    ]
    assert pairs == [
        (
            "query_attention_local_actual_p0p1",
            "random_local_actual_p0p1_seed_mean",
        ),
        (
            "query_attention_local_actual_p0p25",
            "random_local_actual_p0p25_seed_mean",
        ),
    ]


def test_load_attention_source_builds_virtual_seed_mean(tmp_path):
    actual, virtual, _pairs = method_contract([0.1], [13, 29])
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "query_attention_local_summary.json").write_text(
        json.dumps(
            {
                "official_cache_craft_implementation": False,
                "budgets": [0.1],
                "random_seeds": [13, 29],
                "num_examples": 1,
            }
        ),
        encoding="utf-8",
    )
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
    for index, method in enumerate(actual):
        row = {"example_id": "e1", "method": method}
        for _metric, field, boolean in METRIC_FIELDS:
            row[field] = bool(index % 2) if boolean else float(index)
        rows.append(row)
    (run_dir / "query_attention_local_outputs.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )

    records, source = load_source(
        run_dir,
        data_path,
        actual_methods=actual,
        virtual_methods=virtual,
        budgets=[0.1],
        random_seeds=[13, 29],
        expected_examples=1,
    )
    by_method = {row["method"]: row for row in records}
    random_values = [
        by_method["random_local_actual_p0p1_seed13"]["values"],
        by_method["random_local_actual_p0p1_seed29"]["values"],
    ]
    assert by_method[virtual[0]]["values"] == (
        __import__("numpy").asarray(random_values).mean(axis=0).tolist()
    )
    assert source["condition"] == "natural"
