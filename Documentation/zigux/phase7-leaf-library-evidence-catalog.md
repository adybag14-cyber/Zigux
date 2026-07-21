- packet: `phase7-leaf-library-evidence`
- phase: `Phase 7`
- lane scope: shared leaf-library evidence rows and validation foothold only

## Current direct-readback companions

- `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts\zigux/check_phase7_shared_surface.zig`
- `scripts\zigux/check_phase7_build_wiring.zig`
- `scripts\zigux/check_phase7_make_wrapper_selftest_alignment.zig`
- `scripts\zigux/check_phase7_cmdline_packet.zig`
- `scripts\zigux/check_phase7_argv_split_packet.zig`
- `scripts\zigux/check_phase7_string_helpers_format_boundary_packet.zig`
- `scripts\zigux/check_phase7_rbtree_parity.zig`
- `scripts\zigux/validate_phase7.zig`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase7_leaf_library_evidence_manifest.json`
- `zigux/tests/phase7_build.zig`
- `zigux/Makefile`
- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

## Roadmap anchors

- `lib/string_helpers.c`
- `lib/cmdline.c`
- `lib/argv_split.c`
- `lib/rbtree.c`

## Current direct helper evidence

- `lib/string_helpers.zig` keeps the returned string-unit, escape, unescape, `kasprintf`, `kstrdupQuotable()`, `kstrdupQuotableCmdline()`, and `parseIntArray()` support packet readable on current `master`.
- `lib/cmdline.zig` keeps the current option parsing, `memparse`, and integer-range handling packet readable on current `master`.
- `lib/argv_split.zig` keeps the current whitespace-tokenization helper family readable on current `master`.
- `lib/rbtree.zig` now keeps the returned tree-node, cached-root, insertion, and cached-find helper surface readable on current `master`.

## Current replay inventory

- `zig run scripts/zigux/check_phase7_shared_surface.zig`
- `zig run scripts/zigux/check_phase7_shared_surface.zig -- --self-test`
- `zig run scripts/zigux/check_phase7_build_wiring.zig`
- `zig run scripts/zigux/check_phase7_build_wiring.zig -- --self-test`
- `zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig`
- `zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test`
- `zig run scripts/zigux/check_phase7_cmdline_packet.zig`
- `zig run scripts/zigux/check_phase7_cmdline_packet.zig -- --self-test`
- `zig run scripts/zigux/check_phase7_argv_split_packet.zig`
- `zig run scripts/zigux/check_phase7_argv_split_packet.zig -- --self-test`
- `zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig`
- `zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig -- --self-test`
- `zig run scripts/zigux/check_phase7_rbtree_parity.zig`
- `zig run scripts/zigux/check_phase7_rbtree_parity.zig -- --self-test`
- `zig run scripts/zigux/validate_phase7.zig`
- `zig run scripts/zigux/validate_phase7.zig -- --self-test`
- `make -C zigux phase7-validate`

## Current build-wiring evidence

- `zigux/tests/phase7_build.zig` wires `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` into the shared Phase 7 build graph.
- `zigux/tests/phase7_build.zig` still exposes the dedicated helper, survey, sample-boundary, and format-boundary routes through `phase7-string-helpers-test`, `phase7-string-helpers-survey`, `phase7-string-helpers-sample-boundary`, `phase7-string-helpers-format-boundary`, `phase7-cmdline-test`, `phase7-cmdline-survey`, `phase7-argv-split-test`, `phase7-argv-split-survey`, `phase7-rbtree-test`, and `phase7-rbtree-survey`.
- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper, survey, sample-boundary, and format-boundary replay through the current `test_step.dependOn(...)` handoff list.
- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.

## Current repo-reality gaps

- shared `Documentation/zigux/README.md` Phase 7 reminder text still omits the shipped `scripts\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory
- shared `Documentation/zigux/review-checklist.md` Phase 7 reminder text still omits the shipped `scripts\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory
- shared `scripts/zigux/README.md` and `zigux/tests/README.md` Phase 7 reminder text still omits the shipped `scripts\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory

## Review posture

- keep the current Phase 7 packet bounded to returned leaf-library helper evidence, the shared docs-root, scripts-root, and tests-root reminder packet, the dedicated build-wiring guard, the dedicated `cmdline` packet guard, the dedicated `argv_split` packet guard, the dedicated `string_helpers` format-boundary packet guard, the dedicated `rbtree` parity guard, the make-wrapper self-test alignment guard, and one Makefile-backed validation foothold
- do not widen this packet into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes
