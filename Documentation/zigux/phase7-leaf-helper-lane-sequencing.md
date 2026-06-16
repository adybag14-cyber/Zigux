# Phase 7 Leaf-Helper Lane Sequencing

This note keeps the roadmap-backed Phase 7 runtime leaf-helper packet reviewable without widening into runtime pilots, deep-core freeze anchors, or neighboring subsystem work.

## Scope

Phase 7 stays limited to the first reusable runtime-safe leaf-helper families named by the product roadmap:

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

These helpers are allowed to reopen only for bounded helper-local semantics, ownership, validation, or direct-anchor truthfulness repairs.

Do not use this lane to widen into:

- Phase 8 tooling expansion under `tools/lib/*`
- Phase 9 runtime pilot modules or samples
- deep-core freeze-in-C anchors covered by the Phase 15 freeze-map governance packet
- driver, MMIO, DMA, or queue work from later phases

## Current Repo Reality

Fresh repo-first inspection shows the roadmap-backed Phase 7 family is only partially materialized on current `master`.

That means the honest current lane split is helper-local and direct-readback-aware rather than a four-helper landed batch:

- `lib/string_helpers.zig` plus its helper-local survey, manifest, and no-string-sample boundary packet are directly readable and remain the clearest same-lane reopen surface
- `argv_split` now directly rereads as `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts\zigux/check_phase7_argv_split_packet.zig`, so treat `P7-L09` as the returned fixture-backed helper-local packet instead of a narrower helper-plus-survey-manifest-checker foothold; keep shared validator, Makefile, workflow, tests-root, and broader docs-root reminders routed outside this helper-local packet
- `cmdline` now directly rereads as `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `scripts\zigux/check_phase7_cmdline_packet.zig`, and the no-standalone-cmdline-sample boundary in `samples/zigux/README.md`, so treat `P7-L10` as the returned helper-local packet instead of a helper-plus-survey-manifest foothold; keep shared validator, Makefile, workflow, tests-root, and broader docs-root reminders routed outside this helper-local packet
- the surviving `rbtree` helper-local packet now directly rereads as `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts\zigux/check_phase7_rbtree_parity.zig`, `tools/lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json`, while the roadmap-path helper `lib/rbtree.zig` and the dedicated fixture pair still do not directly materialize on current `master`; keep same-lane follow-through inside that returned helper-local packet without implying the roadmap-path helper or fixture pair has returned

No helper in this packet should be treated as a generic stand-in for the others.
Reopen one directly readable helper family or surviving direct-anchor packet at a time.

## Validation Discipline

Use the narrowest honest replay that matches the chosen helper family and the files you can directly prove are present on current `master`.

- `lib/string_helpers.zig`: `zig test lib/string_helpers.zig`
- `lib/argv_split.zig`: `zig test lib/argv_split.zig`
- `lib/cmdline.zig`: `zig test lib/cmdline.zig`
- `lib/rbtree.zig`: use `zig test lib/rbtree.zig` only after a fresh reread proves the roadmap-path helper has returned on current `master`
- returned `rbtree` helper-local packet work: validate by rereading `Documentation/zigux/phase7-leaf-helper-lane-sequencing.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts\zigux/check_phase7_rbtree_parity.zig`, `tools/lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json` together so the returned packet stays explicit without implying that the missing roadmap-path helper or dedicated fixture pair have returned

If a future change adds shared Phase 7 tests-root wiring, keep that route additive. Do not replace the helper-local Zig replay with a broader route unless the broader route proves the same boundary more clearly.

## Anti-Overlap Rules

When this lane reopens, stay inside one bounded step only.

- Do not batch two helper families into one run.
- Prefer validation and ownership repairs before semantic expansion.
- Keep borrowed-buffer and sentinel-termination contracts explicit for `cmdline` and `argv_split`.
- Keep leftmost-cache, duplicate-search, iterator ownership, direct-helper packet truthfulness, and surviving-anchor truthfulness explicit for `rbtree`.
- Keep C-string boundary, sysfs newline-equivalence, and counted-search ownership explicit for `string_helpers`.
- If a helper-local test already covers the questioned edge, do not invent a second packet for the same proof.

## Freeze-Map Posture

This Phase 7 packet is outside the deep-core freeze map.

That does not authorize broader runtime work.
It only means these runtime-safe leaf helpers may continue to evolve inside their bounded helper-owned contracts while deep-core freeze-in-C anchors remain governed by the separate Phase 15 packet.

## Next Bounded Step

Start from one directly readable helper family or surviving direct-anchor packet only and pick the smallest truthful follow-up:

- `lib/string_helpers.zig`: helper-local boundary or ownership drift in string, sysfs, or counted-search behavior
- `lib/argv_split.zig`: helper-local drift in empty-view reuse, copied-storage tokenization, or null-terminated argv export, or one shared reminder-surface truthfulness repair that explicitly names the returned slice-helper-test-fixture-survey-manifest-checker packet in `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, and `scripts\zigux/check_phase7_argv_split_packet.zig` plus its `zig test lib/argv_split.zig` replay without widening into shared validator, Makefile, workflow, tests-root, or broader docs-root ownership
- `lib/cmdline.zig`: helper-local drift in borrowed-slice parsing, `nextArg()` quoting, or `memparse()` ownership behavior, or one shared reminder-surface truthfulness repair that explicitly names the returned slice-helper-test-survey-manifest-checker-plus-boundary packet in `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_manifest.json`, `scripts\zigux/check_phase7_cmdline_packet.zig`, and `samples/zigux/README.md` plus its `zig test lib/cmdline.zig` replay without widening into shared validator, Makefile, workflow, tests-root, or broader docs-root ownership
- returned `rbtree` helper-local packet: keep same-lane follow-through inside `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts\zigux/check_phase7_rbtree_parity.zig`, `tools/lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, or `zigux/tests/phase7_rbtree_manifest.json` while the roadmap-path helper `lib/rbtree.zig` and the dedicated fixture pair remain missing; route broader shared validator, Makefile, workflow, or build-route drift outside this helper-local packet

If current helper-local tests, surviving direct anchors, and ownership notes already agree, leave the helper parked and do not widen to a second family in the same lane.
