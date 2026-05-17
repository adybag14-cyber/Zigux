# Phase 14 Scripts-Root Summary Gap

## Scope
- lane: `P14-L18`
- phase: `Phase 14`
- packet: shared rollback-threshold and release-boundary reminder surfaces
- status: `current-master gap`

## Why this note exists
The Phase 14 roadmap keeps the core-adjacent packet bounded, study-only, and reviewability-first. That means the shared reminder surfaces need to stay aligned on the same current validator and checker packet instead of letting one summary surface fall behind after substantive same-family note work lands.

## Current repo readback
Fresh current-`master` readback on 2026-05-17 shows that the shared Phase 14 docs-root summary still names the current smoke packet through:
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-core-boundary-traceability.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

The same reread also shows that `scripts/zigux/README.md` currently stops at `## Phase 13` and does not carry any `## Phase 14` reminder block.

Current `zigux/tests/README.md` likewise does not currently carry a Phase 14 summary block.

## Why this matters
This is a reminder-surface truthfulness gap, not a new delivery request:
- the shared docs-root summary still presents a live Phase 14 packet
- the scripts-root summary no longer mirrors that packet at all
- the rollback-threshold sequencing checker and release-boundary exact-counts checker are therefore visible in the docs-root summary but absent from the scripts-root inventory contributors are expected to scan for shipped validation helpers
- the tests-root summary also no longer provides a Phase 14 shared packet companion, which means later same-lane reminder work should re-read both summary surfaces together instead of assuming either one still mirrors the docs-root packet

## Smallest honest same-lane repair
The next bounded `P14-L18` follow-through should stay notes-only and shared-surface-local:
1. restore a compact `## Phase 14` block in `scripts/zigux/README.md` that mirrors the current shared smoke packet, including `validate-phase14.py`, the docs-root and tests-root smoke-summary checkers, the rollback-threshold sequencing checker, the release-boundary exact-counts checker, and the shared `make -C zigux phase14-*` routes
2. decide in the same reread whether `zigux/tests/README.md` should regain a matching compact Phase 14 summary block or stay intentionally silent with that omission recorded here
3. keep the repair bounded to summary truthfulness without reopening anchor-local bridge notes, validator behavior, or Phase 15 governance wording

## Non-goals
- do not claim a new Phase 14 validator, bridge, or status change
- do not reopen workqueue, ring-buffer, skbuff, or RCU anchor-local packet ownership
- do not widen into attached-toolchain guidance ownership, which remains a separate shared guidance gap if the scripts-root reminder is restored later
- do not treat this reminder drift as proof that the executable Phase 14 packet changed