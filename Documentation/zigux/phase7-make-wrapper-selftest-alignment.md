# Phase 7 Make-Wrapper Selftest Alignment

This note tracks the checker-local shared-control guard for the parked Phase 7 make-wrapper posture.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=make-wrapper-shared-control-surface`
- `PHASE7_LANE_KEY=P7-Y05`

## Current Repo Reality

- current `master` keeps `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py` as the dedicated checker for the parked Phase 7 make-wrapper posture
- current `master` keeps `scripts/zigux/check-phase7-shared-control-gap.py` as the broader shared-control checker that already guards the parked-path contract across the sequencing note, string-helpers slice, workflow, readable non-owner files, and direct shared-control packet
- current `master` now replays both checkers directly in `.github/workflows/zigux-bootstrap.yml` through explicit self-test and live-check steps, so the checker-local make-wrapper contract is enforced without reviving the older `phase7-validate` or `phase7-test` wrapper routes
- current `master` still does not materialize `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/validate-phase7.py`, or `zigux/tests/phase7_build.zig`, so treat those older wrapper, validator, and shared-build paths as parked reminder vocabulary rather than direct current-tree proof
- current `master` keeps `zigux/Makefile` readable again, but its live body still omits `phase7-validate`, `phase7-test`, and `phase7`, so the make-wrapper note should stay parked on checker-backed workflow evidence instead of older route-present assumptions

## Shared-Control Boundaries

- keep helper-local owner routing under `Documentation/zigux/phase7-helper-lane-sequencing.md`; this shared-control note is not the owner for reopening `string_helpers`, `cmdline`, `argv_split`, or `rbtree` helper semantics
- keep `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, and `Documentation/zigux/phase7-rbtree-slice.md` framed as helper-local review packets while this note stays limited to parked shared-control enforcement
- keep `scripts/zigux/README.md`, `zigux/tests/README.md`, `samples/zigux/README.md`, and `.github/workflows/zigux-bootstrap.yml` aligned around the same parked shared-control story: the helper-local packets are directly readable, the old shared validator and shared build routes are still absent, and the workflow-backed checker pair is the current enforcement surface

## Next Bounded Step

If a future reread shows new Phase 7 shared-control drift, keep the next step inside `scripts/zigux/check-phase7-shared-control-gap.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase7-helper-lane-sequencing.md`, or this note before widening into helper-local packets or trying to resurrect the older `phase7-*` wrapper stack.
