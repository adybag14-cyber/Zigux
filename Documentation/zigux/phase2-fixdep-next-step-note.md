# Phase 2 fixdep next step note

Lane: `P2-L06`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, but the surviving fixdep closure packet is now narrower than older reminder surfaces implied.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so the family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` still directly serves `scripts/zigux/fixdep.zig`, `scripts/zigux/check-phase2-fixdep-gate.py`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-fixdep-next-step-note.md`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`.
- Current `master` still returns missing for `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, and `Documentation/zigux/artifact-diff.md`, so the older note about a fully materialized external fixdep parity packet is no longer truthful on current head.
- The live bootstrap workflow and `zigux/Makefile` do not expose dedicated fixdep replay routes, and `zigux/tests/README.md` now carries only the shared Phase 2 review packet rather than a fixdep-local route inventory.
- `scripts/zigux/check-phase2-fixdep-gate.py` still pins those broader shared surfaces together with the missing artifact-diff companion, so the current mismatch is governance drift inside the fixdep closure packet rather than parser drift inside `fixdep.zig` itself.

## Survey result

- The same-lane gap is still closure-note and checker drift, not helper-local parser drift.
- `scripts/zigux/fixdep.zig` remains directly reviewable on current `master`, but the surviving reminder packet is smaller than the gate script currently enforces.
- Rebuilding older Makefile or workflow fixdep routes from this lane would widen the packet beyond the smallest truthful repair.

## Next safe step

1. Narrow `scripts/zigux/check-phase2-fixdep-gate.py` so it fails closed on the live fixdep-local closure packet only, instead of pinning `Documentation/zigux/artifact-diff.md`, dedicated fixdep route lines in `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml`, or fixdep-local wording in `zigux/tests/README.md` that current `master` no longer materializes.
2. Keep the follow-through to one same-family governance correction only; do not reopen `fixdep.zig` parser behavior, fixture expected outputs, genksyms, kconfig bridge, or the broader shared Phase 2 route inventory from this note lane.
3. Only if a fresh current-master reread restores one of the missing external fixdep companions should this note widen back toward artifact-diff or route-level follow-through.
