# INVALID — DO NOT CITE

This two-example development smoke temporarily set `logits_to_keep=1` in the
answer evaluator.  That changed first-token KL at tiny floating-point scale and
was intentionally reverted to preserve the submitted answer-evaluation
semantics.  The run is retained only to document why the optimization is limited
to the latency evaluator.  Use the later `_v2` regression and final fresh runs.
