# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::all_document_patch | 0.996 | 0.452 | 0.546 | 2 | 0.960 |
| all_document_patch | 0.998 | 0.452 | 0.545 | 1 | 0.960 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::all_document_patch::external_2wiki | 0.996 | 0.452 | 2 |
| all_document_patch::external_2wiki | 0.998 | 0.452 | 1 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
