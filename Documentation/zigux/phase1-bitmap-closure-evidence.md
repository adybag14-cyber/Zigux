# Phase 1 Bitmap Closure Evidence

This note records the current `tools/lib/bitmap.zig` closure evidence for the Phase 1 host-helper tranche without reopening helper implementation scope.

## Grounding

- Roadmap target: Phase 1 Alpha Host-Side Helpers, specifically `tools/lib/bitmap.c` to `tools/lib/bitmap.zig`.
- Ledger anchors: entries 6, 7, 9, 15, and 16 covering the Phase 1 helper port, helper harness, golden parity fixtures, tranche closure note, and hardened closure gates.
- Live bitmap helper blob read during this pass: `eb8e8cffd3d62e730ade1ede5ebe9324916ad781`.
- Live closure note blob read during this pass: `78b2c440a409ef50bb245ad7a16f97b6454bab69`.
- Live helper manifest blob read during this pass: `ed5e9de4344916c5288f37271da2772113d99e6c`.
- Live bitmap direct-anchor checker blob read during this pass: `db01679ab42c7afb984a4b39b7e0ecaad426241d`.
- Live closure validator blob read during this pass: `951d9c723759bb433a68eef2e682604c3f3e0d77`.

## Evidence Summary

The current bitmap helper remains a parked direct-anchor helper in the closed Phase 1 tranche. The committed helper manifest still lists `tools/lib/bitmap.zig` in `direct_anchor_followup_helpers`, and its bitmap anchor list includes the zero-bit logical helper test, copy and extension boundary tests, raw-copy alias coverage, tail-masked predicates and weights, caller-window `xor` and `or` clamps, weighted tail counts, cross-word `scnprintf()` behavior, empty-buffer preservation, Linux-style alias mirrors, and allocator optional-reset coverage.

The live bitmap helper now carries the zero-bit logical assertion in the corrected `std.testing.expect(...)` form, so the older one-argument `std.testing.expectEqual(...)` compile blocker is no longer present in the current closure packet. The same helper also keeps the boundary and alias tests named by the manifest-backed bitmap direct-anchor checker.

The live `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py` delegates the bitmap direct-anchor checker before the find_bit, rbtree, and string review guards. That keeps bitmap evidence anchored by executable marker checks rather than by this note alone.

## Lane Decision

No helper implementation, fixture, manifest, or closure-validator edit is required from this notes lane unless a later fresh reread finds drift in one of these files:

- `tools/lib/bitmap.zig`
- `Documentation/zigux/phase1-closure.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `scripts/zigux/validate-phase1-closure.py`
- `scripts/zigux/check-phase1-bitmap-direct-anchors.py`
- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`

If this lane reopens, the smallest useful next step is to rerun the same closure-packet comparison first, then edit only the stale evidence surface. Do not widen into helper behavior, shared Phase 1 replay, fixture expansion, or Phase 4 bitmap-drift scope unless the reread proves that the current bitmap closure evidence is no longer truthful.
