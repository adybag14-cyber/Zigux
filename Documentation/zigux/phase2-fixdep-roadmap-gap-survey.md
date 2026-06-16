# Phase 2 fixdep roadmap-gap survey

Lane: `P2-L01`

## Roadmap anchors

- `ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` places `scripts/basic/fixdep.c` inside Phase 2 and names `scripts/zigux/fixdep.zig` as the bounded Zigux destination for selected dual-implementation work.
- The same roadmap keeps `wrapper-first path for parser-heavy tooling` and `selected dual implementations` as the Phase 2 rule for risky build tooling instead of a flag-day replacement story.
- `BOOTSTRAP_COMMIT_LEDGER.md` records the shipped fixdep lane in commit 11 and the widened parity-fixture packet in commit 13.

## Current repo evidence

- `scripts/zigux/fixdep.zig` is the live Zig dual-implementation surface for the roadmap-backed `fixdep` lane.
- `scripts\zigux/check_fixdep_diff.zig` keeps the current C-versus-Zig fixture packet explicit.
- `scripts\zigux/check_phase2_fixdep_gate.zig` keeps the fixdep-local review packet aligned across the dedicated note, closure note, fixtures, workflow, and tests-facing reminder surfaces.
- `zigux/tests/fixtures/fixdep/cases.json` is the live twelve-case fixture packet for the current `fixdep` slice.
- `Documentation/zigux/phase2-closure.md` records that same twelve-case packet and keeps the direct `zig test scripts/zigux/fixdep.zig` replay explicit in the closure story.

## Gap assessment

- The current repo does not show a roadmap gap in the core dual-implementation requirement for `fixdep`: the Zig surface, the C comparison checker, the dedicated fixdep gate, and the twelve-case fixture packet are all present.
- The bounded remaining risk is reminder-surface drift, not missing parser work. Future Phase 2 follow-through should keep the fixdep-local survey, fixture packet, and direct Zig replay aligned before widening into broader toolchain or kconfig cleanup.

## Next bounded step

- Keep fixdep-local truthfulness tied to `scripts/zigux/fixdep.zig`, `scripts\zigux/check_fixdep_diff.zig`, `scripts\zigux/check_phase2_fixdep_gate.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `Documentation/zigux/phase2-closure.md` instead of reopening parser implementation work that the current lane evidence already covers.
