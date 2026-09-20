import math

from scripts.summarize_latency_paired_bootstrap import (
    example_method_medians,
    paired_values,
)


def test_paired_bootstrap_inputs_take_repeat_median_before_example_pairing():
    rows = []
    for example_id, full_times, candidate_times in (
        ("e0", [2.0, 2.0, 100.0], [1.0, 1.0, 1.0]),
        ("e1", [4.0, 4.0, 4.0], [2.0, 2.0, 50.0]),
    ):
        for repeat, value in enumerate(full_times):
            rows.append(
                {
                    "example_id": example_id,
                    "method": "full_prefill",
                    "repeat": str(repeat),
                    "time_to_first_logit_s": str(value),
                }
            )
        for repeat, value in enumerate(candidate_times):
            rows.append(
                {
                    "example_id": example_id,
                    "method": "candidate",
                    "repeat": str(repeat),
                    "time_to_first_logit_s": str(value),
                }
            )

    medians = example_method_medians(rows)
    assert medians[("e0", "full_prefill")] == 2.0
    assert medians[("e1", "candidate")] == 2.0
    values = paired_values(["e0", "e1"], "candidate", medians)
    assert [item["speedup"] for item in values] == [2.0, 2.0]
    assert [item["time_saved_s"] for item in values] == [1.0, 2.0]
    assert math.isclose(sum(item["speedup"] for item in values), 4.0)
