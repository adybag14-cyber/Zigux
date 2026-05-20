# Phase 2 fixdep next step note

Lane: `P2-Y01`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, and the live fixdep governance packet is broader and healthier than this note currently says.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so the family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/fixdep.zig`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/validate-phase2.py`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, `Documentation/zigux/phase2-fixdep-next-step-note.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/fixtures/fixdep/cases.json`.
- `zigux/tests/fixtures/fixdep/cases.json` currently inventories 12 external fixdep cases, including `sample_dependency_continuation`, `sample_comment_continuation`, and the current stdout-failure replay cases.
- The live bootstrap workflow and `zigux/Makefile` still expose direct fixdep replay routes through `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig`.
- The stale surface is this note and adjacent reminder wording that still describe the diff checker, fixture roster, or direct replay routes as absent even though current `master` materializes them.

## Survey result

- The same-lane gap is reminder-surface truthfulness, not missing fixdep artifact support and not helper-local parser drift.
- The fixdep helper, checker pair, fixture roster, and direct replay routes are already reviewable on current `master`.
- Widening this lane into parser or new expected-output work would skip over the smaller governance correction still needed on the reminder side.

## Next safe step

1. Refresh `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md` so it stops describing `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, and direct `phase2-fixdep` replay routes as missing on current `master`.
2. Keep the follow-through to one same-family reminder correction only; do not reopen `fixdep.zig` parser behavior, fixture expected outputs, genksyms, kconfig bridge, or the broader shared Phase 2 route inventory from this governance lane.
3. Only if a fresh current-master reread finds a new mismatch between the live checker pair, the 12-case fixture roster, and the direct fixdep replay routes should this lane widen back into checker or expected-output follow-through.
