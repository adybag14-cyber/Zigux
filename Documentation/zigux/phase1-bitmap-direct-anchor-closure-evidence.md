# Phase 1 Bitmap Direct-Anchor Closure Evidence

This note records the current `tools/lib/bitmap.zig` closure evidence for the Phase 1 helper tranche. It is intentionally bitmap-local: it does not reopen shared fixture ownership, older Phase 1 route names, or neighboring direct-anchor helpers.

## Scope

- lane: `P1-L06`
- phase: `Phase 1`
- helper: `tools/lib/bitmap.zig`
- roadmap anchor: host-side helper port with reviewable parity and validation evidence
- ledger anchor: `feat(tools/lib): start phase-1 helper ports` and the Phase 1 helper harness/parity tranche

## Current Readback

Current `master` exposes the bitmap closure packet through these directly readable files:

- `tools/lib/bitmap.zig` at blob `eb8e8cffd3d62e730ade1ede5ebe9324916ad781`
- `zigux/tests/fixtures/phase1_helper_manifest.json` at blob `ed5e9de4344916c5288f37271da2772113d99e6c`
- `Documentation/zigux/phase1-closure.md` at blob `78b2c440a409ef50bb245ad7a16f97b6454bab69`
- `scripts\zigux/check_phase1_bitmap_direct_anchors.zig` at blob `db01679ab42c7afb984a4b39b7e0ecaad426241d`
- `.github/workflows/zigux-bootstrap.yml` at blob `5bdb136b8b6710c08c19566879d5a9da42b63445`
- `scripts/zigux/README.md` at blob `91e603865057d10f27f37fef5bb314d3f807acb1`

## Closure Evidence

The helper surface now keeps the bitmap direct anchors explicit in `tools/lib/bitmap.zig`, including copy alias behavior, copy-clear-tail and copy-and-extend semantics, zero-sized destination-view no-op behavior, zero-bit logical short-circuit behavior, caller-window xor/or clamping, weighted tail-count clamping, complement tail clamping, cross-word `scnprintf()` range merging, empty-buffer preservation, Linux-style alias mirrors, and allocator optional-reset coverage.

The dedicated checker `scripts\zigux/check_phase1_bitmap_direct_anchors.zig` exact-checks those bitmap-local source and test markers. The bootstrap workflow runs both the self-test and live checker steps:

- `zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig -- --self-test`
- `zig run scripts/zigux/check_phase1_bitmap_direct_anchors.zig`

The scripts-root reminder note also records that the bitmap checker is directly readable on current `master` and should stay wired into the scripts-root reminder packet and bootstrap workflow rather than being treated as lane-note-only context.

## Parking Rule

Keep `P1-L06` parked unless a fresh reread finds drift between the bitmap helper, the manifest-backed review anchors, the closure note, the bitmap direct-anchor checker, or the workflow steps above. If the lane reopens, first rerun the bitmap direct-anchor checker and the Phase 1 closure validator on a writable checkout before changing helper semantics or shared fixtures.
