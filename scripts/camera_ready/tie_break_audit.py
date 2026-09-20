#!/usr/bin/env python3
"""Audit how often the selectors' ascending-document-id tie-break decides the selection.

Uses the shipped selector code unchanged. Emits paper/tables/appendix_tie_break.tex and
scratch/tie_break_audit.json (consumed by check_numbers.py and cited in NUMBERS.md §20).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

SUB = Path(__file__).resolve().parents[2]
REB = Path(__file__).resolve().parents[2] / "results_rebuttal"
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SUB / "code"))
from safekv.data_schema import DiagnosticExample  # noqa: E402
from safekv.doc_selector import query_similarity_doc_scores, risk_guided_doc_scores  # noqa: E402


def load(path: Path, n: int | None = None):
    out = []
    with open(path) as f:
        for line in f:
            if line.strip():
                out.append(DiagnosticExample.from_dict(json.loads(line)))
            if n and len(out) >= n:
                break
    return out


def audit(exs, scorer, k):
    n = len(exs); tie = 0; start_diff = 0; tie_to_ev = 0; id_is_pos = 0; asc_earlier = 0
    for ex in exs:
        sc = scorer(ex)
        pos = {d.doc_id: i for i, d in enumerate(ex.documents)}
        if all(d.doc_id == i for i, d in enumerate(ex.documents)):
            id_is_pos += 1
        asc = sorted(sc, key=lambda s: (-s.score, s.doc_id))
        desc = sorted(sc, key=lambda s: (-s.score, -s.doc_id))
        s1 = [s.doc_id for s in asc[:k]]; s2 = [s.doc_id for s in desc[:k]]
        tied = len(sc) > k and math.isclose(asc[k - 1].score, asc[k].score)
        if tied:
            tie += 1
            ev = {e.doc_id for e in ex.evidence}
            if min(s1, key=lambda i: pos[i]) in ev:
                tie_to_ev += 1
        st1 = min(pos[i] for i in s1); st2 = min(pos[i] for i in s2)
        if st1 != st2:
            start_diff += 1
            if st1 < st2:
                asc_earlier += 1
    return dict(n=n, tie=tie, start_diff=start_diff, tie_start_is_evidence=tie_to_ev, id_equals_position=id_is_pos,
                ascending_start_earlier=asc_earlier)


def audit_hybrid(exs):
    """Hybrid K1 = union of query top-1 and risk top-1; start = earliest position."""
    from safekv.doc_selector import select_top_k_doc_ids
    n = len(exs); start_diff = 0; asc_earlier = 0
    for ex in exs:
        pos = {d.doc_id: i for i, d in enumerate(ex.documents)}
        q, r = query_similarity_doc_scores(ex), risk_guided_doc_scores(ex)
        a = set(select_top_k_doc_ids(q, 1)) | set(select_top_k_doc_ids(r, 1))
        qd = sorted(q, key=lambda s: (-s.score, -s.doc_id))[:1]; rd = sorted(r, key=lambda s: (-s.score, -s.doc_id))[:1]
        b = {s.doc_id for s in qd} | {s.doc_id for s in rd}
        st1 = min(pos[i] for i in a); st2 = min(pos[i] for i in b)
        if st1 != st2:
            start_diff += 1
            if st1 < st2:
                asc_earlier += 1
    return dict(n=n, start_diff=start_diff, ascending_start_earlier=asc_earlier)


SETS = [
    ("HotpotQA-500, gold-first", SUB / "data/external_hotpotqa_500.jsonl", None),
    ("2Wiki-500, gold-first", SUB / "data/external_2wiki_500.jsonl", None),
    ("2Wiki-100, gold-first (Table 3)", SUB / "data/external_2wiki_500.jsonl", 100),
    ("HotpotQA-100, score-neutral shuffle 101", REB / "data/hotpot_zero_shuffle101.jsonl", 100),
    ("2Wiki-100, score-neutral shuffle 101", REB / "data/2wiki_zero_shuffle101.jsonl", 100),
    ("Position sweep (Noise16, 19 docs)", SUB / "data/position_sweep_noise16_single_50x5_docs19.jsonl", None),
    ("Noise16-250", SUB / "data/noise_sweep_16_250.jsonl", None),
    ("Noisy diagnostic (Mistral rows, first 250)", SUB / "data/diagnostic_1000_noisy.jsonl", 250),
    ("Noise64-50", SUB / "data/noise_sweep_64_50.jsonl", None),
    ("Nested $N{=}16$, layout 101", REB / "data/single_nested_n16_zero_layout101.jsonl", 50),
]


def start_histograms():
    """Selected-start position histograms on the nested staleness inputs (cited in Section 6.4)."""
    from collections import Counter
    from safekv.doc_selector import select_top_k_doc_ids
    out = {}
    for n in (4, 8, 16):
        exs = load(REB / f"data/single_nested_n{n}_zero_layout101.jsonl", 50)
        for name, scorer, k in [("QueryK1", query_similarity_doc_scores, 1), ("RiskK1", risk_guided_doc_scores, 1), ("RiskK2", risk_guided_doc_scores, 2)]:
            c = Counter()
            for ex in exs:
                pos = {d.doc_id: i for i, d in enumerate(ex.documents)}
                S = select_top_k_doc_ids(scorer(ex), k)
                c[min(pos[i] for i in S)] += 1
            out[f"N{n}|{name}"] = dict(sorted(c.items()))
    return out


if __name__ == "__main__":
    dump = {}
    lines = []
    for lab, path, n in SETS:
        exs = load(path, n)
        row = {}
        for sname, scorer in [("Query", query_similarity_doc_scores), ("Risk", risk_guided_doc_scores)]:
            for k in (1, 2):
                row[f"{sname}K{k}"] = audit(exs, scorer, k)
        row["HybridK1"] = audit_hybrid(exs)
        dump[lab] = row
        q1, q2, r1, r2, h1 = row["QueryK1"], row["QueryK2"], row["RiskK1"], row["RiskK2"], row["HybridK1"]
        idpos = "yes" if q1["id_equals_position"] == q1["n"] else "no"
        cells = [f"{x['start_diff']}/{x['n']}" for x in (q1, q2, h1, r1, r2)]
        lines.append(f"{lab} & {idpos} & " + " & ".join(cells) + f" & {q1['tie_start_is_evidence']}/{q1['tie']} \\\\")
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{llrrrrrr}
\toprule
Data & id $=$ pos. & Query K1 & Query K2 & Hybrid K1 & Risk K1 & Risk K2 & Q-K1 tie $\to$ evid. \\
\midrule
""" + "\n".join(lines) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Tie-break audit of the shipped selectors. For each dataset and selector, the middle columns count examples whose suffix-recompute start would change if score ties were broken by descending instead of ascending document id, i.e., examples where the id tie-break decides the start (for hybrid K1, through its query top-1 component). Wherever ids equal positions, the ascending rule always picks the earlier start, i.e., a longer suffix. ``id $=$ pos.'' states whether document ids equal prompt positions in that file. The last column (``Q-K1 tie $\to$ evid.'') counts, among Query-K1 examples with a top-1 tie, how many the ascending-id rule resolves to a gold evidence document. In the synthetic generator ids are assigned before shuffling and evidence documents receive the smallest ids, so a tie there favors evidence; in the external conversions ids equal prompt positions and evidence documents come first, so a tie favors evidence there too; only the score-neutral shuffled variants make the tie-break position-only. The risk selector is rarely tie-decided when retrieval scores are present; on the zero-score nested inputs it is tie-decided in 35 and 28 of 50 examples.}
\label{tab:app-tie-break}
\end{table*}
"""
    (ROOT / "paper_reference/camera_ready_tables/appendix_tie_break.tex").write_text(body)
    dump["start_histograms"] = start_histograms()
    (ROOT / "paper_reference/camera_ready_tables/tie_break_audit.json").write_text(json.dumps(dump, indent=1))
    print(json.dumps(dump["start_histograms"]))
    for lab, row in dump.items():
        if lab == "start_histograms":
            continue
        print(lab, {k: f"{v['start_diff']}/{v['n']}" for k, v in row.items()}, "Q1 tie->ev", f"{row['QueryK1']['tie_start_is_evidence']}/{row['QueryK1']['tie']}")
