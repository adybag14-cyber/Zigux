# Phase 1 and Phase 2 Release Sequencing

This note is the compact PMO coordination companion for the parked early-phase tranche.

It is a release-planning artifact, not a closure rewrite and not a claim that broader historical validator stacks have returned on current `master`.

## Status

- `EARLY_PHASE_RELEASE_PACKET_STATE=parked`
- `EARLY_PHASE_RELEASE_CLOSED=no`
- release owner: `PMO / Release Management`
- Phase 1 closure anchor: `Documentation/zigux/phase1-closure.md`
- Phase 1 sequencing anchor: `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- Phase 2 closure anchor: `Documentation/zigux/phase2-closure.md`
- Phase 2 sequencing anchor: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`

## Release Order

Keep early release wording tied to the current bounded tranche order:

1. confirm the parked Phase 1 helper closure packet remains truthful on current `master`
2. confirm the parked Phase 2 toolchain and kbuild closure packet remains truthful on current `master`
3. leave later Phase 3 and beyond surfaces outside this early-phase release handle unless a separate roadmap-backed release note explicitly widens scope

This preserves the roadmap order from host-side helper closure into toolchain and kbuild closure without turning later ABI or driver work into an implied prerequisite for the early tranche handoff.

## Shared Release Handle

The current early-phase release handle is:

1. `Documentation/zigux/phase1-closure.md`
2. `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
3. `Documentation/zigux/phase2-closure.md`
4. `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
5. `Documentation/zigux/phase1-phase2-release-sequencing.md`

That is the compact release-planning surface for the parked early tranche.

## Repo-Reality Gaps

Keep broader historical closure companions recorded as repo-reality gaps instead of early-release proof:

- `scripts\zigux/validate_phase1.zig`
- `scripts\zigux/check_phase1_parity.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `scripts\zigux/validate_phase2_closure.zig`
- `scripts/zigux/install_zig.zig`
- `scripts\zigux/check_phase2_cross.zig`
- `zigux/tests/fixtures/phase2_cross_targets.json`

The ledger still records those earlier closure-train members as historical tranche context, but this release note should not treat them as current shipped evidence until fresh current-`master` readback restores them.

## Review Use

When early release wording changes:

1. reread the two closure notes and their two sequencing companions beside this note
2. keep Phase 1 and Phase 2 parked unless one of those current reminder surfaces drifts
3. leave helper-local, tool-local, and later-phase replay widening to their own lanes instead of reopening the whole early tranche in one PMO pass

## Boundaries

- This note does not close the early tranche by itself.
- This note does not claim that the missing validator-first, installer, or direct cross-route companions have returned.
- This note does not widen the release handle beyond Phase 1 and Phase 2.
