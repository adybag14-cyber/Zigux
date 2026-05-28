# Phase 7 leaf libraries packet

This note records one bounded validation packet for the existing Phase 7 in-kernel leaf-library ports.
On current `master`, the four roadmap anchors already exist as `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig`.
The honest remaining gap in this lane is not another port file.
It is shared validation substrate wiring that makes those live helpers reviewable as one reusable packet.

## Current packet

- `Documentation/zigux/phase7-leaf-libraries.md`
- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`
- `zigux/tests/phase7_leaf_libraries_starter_packet.zig`
- `zigux/tests/phase7_leaf_libraries_starter_packet_build.zig`
- `zigux/tests/fixtures/phase7_leaf_libraries_manifest.json`
- `scripts/zigux/check-phase7-leaf-libraries.py`

## Bounded contract

- `phase7_leaf_libraries_starter_packet.zig` keeps one cross-helper replay path explicit instead of treating the four live ports as unrelated islands.
- The starter packet checks borrowed command-line parsing, owned argv splitting, string-helper duplication and quoting, bounded integer-option expansion, cached rbtree ordering, and duplicate-key match iteration.
- `phase7_leaf_libraries_starter_packet_build.zig` gives the lane a focused replay route without widening the shared top-level `zigux/tests/build.zig` bundle yet.
- `phase7_leaf_libraries_manifest.json` makes the packet inventory and replay routes explicit so later runs can detect drift without inventing broader closure than the repo has earned.
- `check-phase7-leaf-libraries.py` fail-closes the doc, packet, build entry, and manifest so the lane can advance with a reviewable boundary.

## Replay routes

- `python3 scripts/zigux/check-phase7-leaf-libraries.py --self-test`
- `python3 scripts/zigux/check-phase7-leaf-libraries.py --repo-root . --skip-exec`
- `zig build phase7-leaf-libraries-starter-packet --build-file zigux/tests/phase7_leaf_libraries_starter_packet_build.zig`

## Scope

This packet is intentionally narrow.
It does not claim a full Phase 7 tranche closure, shared top-level test-bundle wiring, or broader kernel-consumer integration.
It only makes the already-landed leaf-library ports reviewable as one bounded validation slice.
