# Phase 4 Validator Gate-Evidence Exactness Gap

## Status

- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_LANE_KEY=validation-perf`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SCOPE=validator_local_truthfulness_only`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_STATUS_BUCKET=shared_validator_prefix_drift`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_OWNER=Validation and Perf Team`
- `PHASE4_VALIDATOR_TARGET=scripts/zigux/validate-phase4.py`
- `PHASE4_VALIDATOR_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
- `PHASE4_GATE_EVIDENCE_NOTE=Documentation/zigux/phase4-gate-evidence.md`
- `PHASE4_GATE_EVIDENCE_BLOB_SHA=8f604959c5250433c5fca14b20d7ff75341c8d33`

## Why this gap note exists

Current `master` already records the exact Phase 4 gate-evidence contract in
`Documentation/zigux/phase4-gate-evidence.md`, including:

- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`
- the shipped `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=` catalog that now includes
  `shared_validator_reruns_gate_evidence_check_drift`

But current `master` still keeps the shared validator prefix-only for the same
contract in `scripts/zigux/validate-phase4.py`.

## Current bounded gap

Inside `REQUIRED_GATE_EVIDENCE_MARKERS`, the shared validator still accepts:

- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=`

That means the validator can still pass while the gate-evidence note drifts away
from the exact current `34`-case catalog or the exact shared target count `19`
that the surrounding Phase 4 packet already treats as shipped evidence.

## Guardrail

`scripts/zigux/check-phase4-validator-gate-evidence-exactness-gap.py` keeps
this note honest against current repo reality. It fail-closes on one narrow
rule:

- the note may only claim this gap while `scripts/zigux/validate-phase4.py`
  still exposes the four prefix-only marker lines above
- the note must keep the exact `34` / `19` gate-evidence contract explicit so a
  later validator rewrite cannot leave this gap note behind as stale evidence

## Non-goals

This note does not claim:

- the validator rewrite is landed
- the gate-evidence note is wrong today
- broader Phase 4 rollback-ownership or perf-threshold policy changed

## Next bounded step

When a publish-capable runtime can safely materialize and rewrite the full live
validator body, apply the exactness helper to `scripts/zigux/validate-phase4.py`
and then either delete this gap note or narrow it to any remaining exactness
drift that still survives the validator rewrite.
