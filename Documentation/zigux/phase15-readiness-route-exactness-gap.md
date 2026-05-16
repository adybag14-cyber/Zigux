# Phase 15 Readiness Route Exactness Gap

This note records one bounded Architecture Council governance gap in the parked
Phase 15 packet: the shipped `phase15-validate` route, the validator-side route
inventory, and the readiness manifest do not currently describe the same checker
set.

## Scope

- lane: `arch-council`
- phase: `Phase 15`
- target family: review boundaries, freeze-map compliance, and architecture
  decisions
- bounded subject: the exact checker inventory for the shared `phase15-validate`
  governance route

## Current repo reality

Current dated `master` readback for this gap shows three different packets for
the same route:

- `zigux/Makefile` runs four checker surfaces before `phase15-test`:
  - `scripts/zigux/check-phase15-docs-readme-alignment.py`
  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `scripts/zigux/check-phase15-review-process-handoff.py`
  - `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/validate-phase15.py` keeps the Make-route markers aligned with
  the docs, scripts, review-process, and shared-summary guards, but its
  `READINESS_CHECKERS` packet still undercounts the route by omitting the docs
  alignment checker.
- `zigux/tests/phase15_readiness_gate_manifest.json` is narrower again and still
  records only the scripts-readme and review-process checkers.

That leaves one exactness gap inside the same governance family: the route that
reviewers are supposed to trust is broader than the validator inventory, and the
machine-readable readiness manifest is narrower than both.

## Why this belongs in Architecture Council lane work

This is not a helper-port or driver-delivery task.

It changes the truthfulness of the governance packet that reviewers use when a
freeze-map-adjacent status discussion needs replayable evidence. If the route
inventory is inconsistent, the parked no-approval posture is harder to review and
future Architecture Council follow-through can inherit stale route claims.

## Machine-checkable guard

`scripts/zigux/check-phase15-readiness-route-exactness.py` keeps this gap
explicit and fail-closed.

The checker currently passes only when repo reality still matches the bounded
exactness gap described here:

- Make route: four checkers
- validator readiness inventory: three checkers, missing only the docs
  alignment checker
- readiness manifest: two checkers, missing the docs alignment checker and the
  shared-summary gap checker

If any of those packets move, the checker fails so the note can be updated or
retired instead of silently drifting.

## Non-goals

This note does not claim:

- any Architecture Council approval for a freeze-map status change
- a change to the freeze-in-C or study-only anchor sets
- a repair to `scripts/zigux/validate-phase15.py`,
  `zigux/tests/phase15_readiness_gate_manifest.json`, or `zigux/Makefile`

## Replay

- `python3 scripts/zigux/check-phase15-readiness-route-exactness.py --self-test`
- `python3 scripts/zigux/check-phase15-readiness-route-exactness.py`

## Next bounded step

When a publish-capable runtime can safely rewrite the live validator packet, fix
the exactness drift in `scripts/zigux/validate-phase15.py` and
`zigux/tests/phase15_readiness_gate_manifest.json`, then retire this gap note
instead of widening the lane.
