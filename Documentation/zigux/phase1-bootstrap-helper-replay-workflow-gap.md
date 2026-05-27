# Phase 1 Bootstrap Helper-Replay Workflow Gap

This note records the current Lane 09 truthfulness gap between the focused
Phase 1 helper replay route already shipped in the tests root and the narrower
bootstrap workflow packet still checked in on current `master`.

## Current Live Packet

- authority packet:
  - `.github/workflows/zigux-bootstrap.yml`
  - `zigux/tests/phase1_helpers_build.zig`
  - `zigux/tests/README.md`
  - `scripts/zigux/README.md`
- focused helper replay route:
  - `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
- current shared bootstrap Phase 1 replay route:
  - `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`

## Current Mismatch

- `zigux/tests/phase1_helpers_build.zig` directly exposes the focused
  `phase1-helpers` step as the focused `phase1-helpers` step
- `zigux/tests/README.md` already treats
  `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
  as current tests-root replay evidence
- `scripts/zigux/README.md` already treats the same focused helper replay as
  current scripts-root reminder evidence
- `.github/workflows/zigux-bootstrap.yml` still does not run
  `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
  on current `master`

## Why This Matters

- the focused fixture-backed helper replay can drift behind the live bootstrap
  packet even while the broader shared smoke route continues to pass
- future Lane 09 follow-through needs one direct place to confirm that the
  missing workflow route is known current-master state rather than a silently
  missed parity replay

## Next Safe Step

- restack `.github/workflows/zigux-bootstrap.yml` so the bootstrap packet runs
  `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
  after the pinned Zig toolchain is installed
- keep that follow-up separate from broader README rewrites unless the reminder
  packet still lags the workflow after the focused helper replay route lands
