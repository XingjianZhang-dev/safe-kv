# Budget Gate Failure Analysis

## Pareto Summary

| target | actual | safe equiv | random mean | percentile | changed+wrong |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.099 | 0.600 | 0.500 | 1.000 | 2 |
| 0.25 | 0.211 | 0.800 | 0.560 | 1.000 | 1 |
| 0.40 | 0.428 | 0.800 | 0.740 | 1.000 | 1 |

# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.800 | 0.836 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.400 | 0.600 | 0.673 | 2 | 0.000 |
| random_gate_budget_0.10_seed000 | 0.600 | 0.400 | 0.509 | 2 | 0.110 |
| random_gate_budget_0.10_seed001 | 0.600 | 0.400 | 0.509 | 2 | 0.110 |
| random_gate_budget_0.10_seed002 | 0.600 | 0.400 | 0.509 | 2 | 0.110 |
| random_gate_budget_0.10_seed003 | 0.400 | 0.600 | 0.673 | 2 | 0.133 |
| random_gate_budget_0.10_seed004 | 0.400 | 0.600 | 0.673 | 2 | 0.123 |
| random_gate_budget_0.10_seed005 | 0.400 | 0.600 | 0.673 | 2 | 0.133 |
| random_gate_budget_0.10_seed006 | 0.400 | 0.600 | 0.673 | 2 | 0.123 |
| random_gate_budget_0.10_seed007 | 0.600 | 0.800 | 0.800 | 1 | 0.070 |
| random_gate_budget_0.10_seed008 | 0.400 | 0.600 | 0.673 | 2 | 0.123 |
| random_gate_budget_0.10_seed009 | 0.600 | 0.800 | 0.800 | 1 | 0.070 |
| random_gate_budget_0.25_seed000 | 0.600 | 0.400 | 0.509 | 2 | 0.243 |
| random_gate_budget_0.25_seed001 | 0.600 | 0.400 | 0.509 | 2 | 0.233 |
| random_gate_budget_0.25_seed002 | 0.600 | 0.400 | 0.509 | 2 | 0.243 |
| random_gate_budget_0.25_seed003 | 0.600 | 0.400 | 0.509 | 2 | 0.243 |
| random_gate_budget_0.25_seed004 | 0.600 | 0.800 | 0.800 | 1 | 0.193 |
| random_gate_budget_0.25_seed005 | 0.400 | 0.600 | 0.673 | 2 | 0.266 |
| random_gate_budget_0.25_seed006 | 0.600 | 0.400 | 0.509 | 2 | 0.233 |
| random_gate_budget_0.25_seed007 | 0.600 | 0.800 | 0.800 | 1 | 0.203 |
| random_gate_budget_0.25_seed008 | 0.400 | 0.600 | 0.673 | 2 | 0.256 |
| random_gate_budget_0.25_seed009 | 0.600 | 0.800 | 0.800 | 1 | 0.203 |
| random_gate_budget_0.40_seed000 | 0.800 | 0.600 | 0.636 | 1 | 0.447 |
| random_gate_budget_0.40_seed001 | 0.800 | 0.600 | 0.636 | 1 | 0.437 |
| random_gate_budget_0.40_seed002 | 0.800 | 0.600 | 0.636 | 1 | 0.437 |
| random_gate_budget_0.40_seed003 | 0.800 | 0.600 | 0.636 | 1 | 0.437 |
| random_gate_budget_0.40_seed004 | 0.800 | 0.600 | 0.636 | 1 | 0.437 |
| random_gate_budget_0.40_seed005 | 0.600 | 0.400 | 0.509 | 2 | 0.499 |
| random_gate_budget_0.40_seed006 | 0.600 | 0.400 | 0.509 | 2 | 0.499 |
| random_gate_budget_0.40_seed007 | 0.600 | 0.800 | 0.800 | 1 | 0.459 |
| random_gate_budget_0.40_seed008 | 0.800 | 0.600 | 0.636 | 1 | 0.437 |
| random_gate_budget_0.40_seed009 | 0.800 | 0.600 | 0.636 | 1 | 0.447 |
| risk_guided_doc_patch_k2 | 0.800 | 0.600 | 0.636 | 1 | 0.570 |
| safe_gate_budget_0.10 | 0.600 | 0.400 | 0.509 | 2 | 0.110 |
| safe_gate_budget_0.25 | 0.800 | 0.600 | 0.636 | 1 | 0.181 |
| safe_gate_budget_0.40 | 0.800 | 0.600 | 0.636 | 1 | 0.437 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::boundary_sensitive | 1.000 | 1.000 | 0 |
| full_prefill::conflict | 1.000 | 0.000 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 1.000 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.000 | 0.000 | 1 |
| prefix_conditioned_naive_global::conflict | 0.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::distractor_heavy | 0.000 | 0.000 | 1 |
| prefix_conditioned_naive_global::multi_hop | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed000::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed000::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.10_seed000::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed000::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed001::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed001::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.10_seed001::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed001::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed002::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed002::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.10_seed002::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed002::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed003::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed003::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed004::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed004::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed005::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed005::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed005::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed005::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed006::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed006::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed007::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed008::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed008::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.10_seed009::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.10_seed009::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed000::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed000::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.25_seed000::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed000::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed001::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed001::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.25_seed001::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed001::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed002::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed002::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.25_seed002::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed002::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed003::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed003::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.25_seed003::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed003::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed004::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed005::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed005::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed006::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed006::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.25_seed006::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed006::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed007::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed008::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed008::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.25_seed009::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.25_seed009::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed000::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed000::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed000::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed000::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed000::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed001::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed001::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed001::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed002::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed002::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed002::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed003::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed003::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed003::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed004::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed004::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed004::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed005::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed005::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed005::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed005::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed006::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed006::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed006::distractor_heavy | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed006::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed006::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed007::conflict | 0.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed007::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed008::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed008::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed008::single_evidence | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::boundary_sensitive | 0.000 | 0.000 | 1 |
| random_gate_budget_0.40_seed009::conflict | 1.000 | 0.000 | 0 |
| random_gate_budget_0.40_seed009::distractor_heavy | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::multi_hop | 1.000 | 1.000 | 0 |
| random_gate_budget_0.40_seed009::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::boundary_sensitive | 0.000 | 0.000 | 1 |
| risk_guided_doc_patch_k2::conflict | 1.000 | 0.000 | 0 |
| risk_guided_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::multi_hop | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.10::boundary_sensitive | 0.000 | 0.000 | 1 |
| safe_gate_budget_0.10::conflict | 1.000 | 0.000 | 0 |
| safe_gate_budget_0.10::distractor_heavy | 0.000 | 0.000 | 1 |
| safe_gate_budget_0.10::multi_hop | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.10::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.25::boundary_sensitive | 0.000 | 0.000 | 1 |
| safe_gate_budget_0.25::conflict | 1.000 | 0.000 | 0 |
| safe_gate_budget_0.25::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.25::multi_hop | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.25::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.40::boundary_sensitive | 0.000 | 0.000 | 1 |
| safe_gate_budget_0.40::conflict | 1.000 | 0.000 | 0 |
| safe_gate_budget_0.40::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.40::multi_hop | 1.000 | 1.000 | 0 |
| safe_gate_budget_0.40::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| conflict_0000_noisy | conflict | 4.01709 | `According to the official schedule, the Qorlan observatory opens at 8` | `8 AM` | `8 AM` |
| distractor_0000_noisy | distractor_heavy | 0.499889 | `Eren Cal` | `Eren Cal received the 2010 Orison Prize for beacon transport` | `Eren Cal` |
| boundary_0000_noisy | boundary_sensitive | 0.0494842 | `1990` | `1970` | `1990` |

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
