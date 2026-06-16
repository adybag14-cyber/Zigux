# Phase 4 Validator Gate-Evidence Exactness Gap

## Status

- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_LANE_KEY=validation-perf`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SCOPE=validator_local_truthfulness_only`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_STATUS_BUCKET=historical_followthrough_waiting_for_republish`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_OWNER=Validation and Perf Team`
- `PHASE4_VALIDATOR_TARGET=scripts\zigux/validate_phase4.zig`
- `PHASE4_VALIDATOR_LAST_KNOWN_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
- `PHASE4_GATE_EVIDENCE_LAST_KNOWN_NOTE=Documentation/zigux/phase4-gate-evidence.md`
- `PHASE4_GATE_EVIDENCE_LAST_KNOWN_BLOB_SHA=8f604959c5250433c5fca14b20d7ff75341c8d33`
- `PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=9`
- `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7`

## Why this gap note still exists

This note now records a parked validator-local follow-through, not a current-head
exactness claim.

Current `master` no longer exposes direct authenticated readback for
`scripts\zigux/validate_phase4.zig` or
`Documentation/zigux/phase4-gate-evidence.md`. The live shared Phase 4 packet is
instead the repo-reality warning anchored by:

- `Documentation/zigux/phase4-reversible-delivery-evidence.md`
- `scripts\zigux/check_phase4_repo_reality_warning.zig`
- `scripts\zigux/check_phase4_reversible_delivery_pins.zig`

The live direct checker pair currently publishes
`PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=9` and
`PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=7`, so this parked
validator-local note stays pinned to the exact current repo-reality packet
instead of only the broader missing-file story.

Those directly readable reminder surfaces currently say the broader Phase 4
validator, lab-matrix, and local-only perf companions remain missing on current
`master`. That means the validator exactness follow-through is still a real
historical next step, but it is not current-head proof today.

## Historical bounded gap

The last directly verified validator-local gap was:

- `scripts\zigux/validate_phase4.zig` accepted prefix-only markers for the gate-evidence
  self-test count, the self-test catalog, the shared validator target count, and
  the shared validator self-test count
- `Documentation/zigux/phase4-gate-evidence.md` carried the exact `34` / `19`
  contract that the validator still needed to exact-check

That is why the last-known validator and gate-evidence blob SHAs stay pinned in
the status block above. They remain the bounded follow-through target if the
missing broader Phase 4 packet is republished or becomes directly readable again.

## Guardrail

`scripts\zigux/check_phase4_validator_gate_evidence_exactness_gap.zig` keeps this
note honest against current repo reality. It fail-closes on four narrow rules:

- this note must describe the validator exactness work as a historical parked
  follow-through rather than claiming live current-head validator evidence
- this note must point at the live repo-reality warning packet in
  `Documentation/zigux/phase4-reversible-delivery-evidence.md`,
  `scripts\zigux/check_phase4_repo_reality_warning.zig`, and
  `scripts\zigux/check_phase4_reversible_delivery_pins.zig`
- this note must keep the published repo-reality checker self-test counts exact
  so it stays pinned to the current live reminder packet
- the note must keep the last-known validator and gate-evidence blob SHAs explicit
  so the follow-through can resume exactly once those broader companions return

## Non-goals

This note does not claim:

- the validator rewrite is landed on current `master`
- `Documentation/zigux/phase4-gate-evidence.md` is directly readable today
- broader Phase 4 rollback-ownership or perf-threshold policy changed

## Next bounded step

Reopen this validator-local exactness follow-through only after a same-family
lane republishes one missing broader Phase 4 companion or direct readback once
again proves that `scripts\zigux/validate_phase4.zig` and
`Documentation/zigux/phase4-gate-evidence.md` are present on current `master`.
At that point, rerun the exactness helper against the re-materialized validator
body and then either retire this note or narrow it to any exactness drift that
still survives the republished packet.
