# Phase 13 Roadmap Traceability

This note maps the Phase 13 roadmap anchors to the current Zigux repo evidence so future runs can see which shared-helper slices are already landed, which ones are manifest-backed, and where the next bounded follow-up still belongs.

## Roadmap frame

Phase 13 in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` is the shared subsystem helper tranche.

Primary Linux anchors:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Recommended Zigux destinations:
- `fs/libfs.zig`
- `lib/devres.zig`
- `security/landlock/*.zig`

Shared tranche entrypoints already present on `master`:
- `zigux/tests/phase13_build.zig`
- `zigux/Makefile` via `make -C zigux phase13`

## Anchor-to-repo map

### `fs/libfs.c`

Current repo evidence:
- implementation anchor: `fs/libfs.zig`
- dedicated tests: `zigux/tests/phase13_libfs.zig`
- reviewability gate: `zigux/tests/phase13_libfs_reviewability.zig`
- manifest: `zigux/tests/phase13_libfs_manifest.json`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice notes: `Documentation/zigux/phase13-libfs-slice.md`
- survey note: `Documentation/zigux/phase13-libfs-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-libfs-helper-starter`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-dcache-cursor-preconditions`
- ready-next `phase13-libfs-dcache-cursor-reposition-bookkeeping`
- blocked `phase13-libfs-dcache-cursor-helpers`
- blocked `phase13-libfs-inode-and-pseudofs-lifecycle`

Traceability summary:
- this anchor is the most fully traced Phase 13 slice right now because the roadmap anchor, helper implementation, dedicated tests, manifest, slice note, survey note, and shared tranche build are all present and mutually named.

### `lib/devres.c`

Current repo evidence:
- implementation anchor: `lib/devres.zig`
- dedicated tests: `zigux/tests/phase13_devres.zig`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-devres-slice.md`

Current lane state visible in the repo:
- the helper slice is real and reviewable through the shared Phase 13 build
- the slice note records the current helper-first boundary around managed ioremap lifetime planning, resource-backed ioremap planning, `devm_of_iomap()`, `devm_arch_phys_wc_add()`, and `devm_arch_io_reserve_memtype_wc()`

Current traceability gap:
- unlike `libfs` and the two Landlock anchors, `devres` does not yet have a committed Phase 13 manifest-backed survey packet in `zigux/tests/` and `Documentation/zigux/`
- that means the roadmap anchor is present in code, tests, and one slice note, but not yet in the same manifest-backed traceability shape as the other active Phase 13 slices

Traceability summary:
- `devres` is landed as a helper slice, but it is currently the asymmetric Phase 13 anchor and the clearest candidate for the next documentation-or-survey follow-up if this lane reopens.

### `security/landlock/ruleset.c`

Current repo evidence:
- implementation anchor: `security/landlock/ruleset.zig`
- dedicated tests: `zigux/tests/phase13_landlock_ruleset.zig`
- manifest: `zigux/tests/phase13_landlock_ruleset_manifest.json`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- survey note: `Documentation/zigux/phase13-landlock-ruleset-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-landlock-ruleset-starter`
- landed `phase13-landlock-rule-layer-merge-followup`
- landed `phase13-landlock-tree-search-followup`
- landed `phase13-landlock-tree-link-followup`
- landed `phase13-landlock-rule-materialization-followup`
- blocked `phase13-landlock-live-tree-state-blocker`

Traceability summary:
- this anchor is roadmap-aligned and manifest-backed, with the current repo explicitly separating the helper-only in-memory lab from the still-blocked live Landlock tree-state and ownership work.

### `security/landlock/syscalls.c`

Current repo evidence:
- implementation anchor: `security/landlock/syscalls.zig`
- dedicated tests: `zigux/tests/phase13_landlock_syscalls.zig`
- manifest: `zigux/tests/phase13_landlock_syscalls_manifest.json`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- survey note: `Documentation/zigux/phase13-landlock-syscalls-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-landlock-syscalls-starter`
- landed `phase13-landlock-add-rule-followup`
- landed `phase13-landlock-ruleset-fd-mode-followup`
- landed `phase13-landlock-path-fd-followup`
- ready-next `phase13-landlock-path-beneath-handoff-followup`

Traceability summary:
- this anchor is also roadmap-aligned and manifest-backed, with the current repo keeping the syscall helper slice explicit about ABI, create-ruleset, add-rule, ruleset-FD, and path-FD planning while still blocking live path import, credential mutation, and enforcement claims.

## Phase 13 traceability status

What is fully traceable today:
- the roadmap-to-repo path for `libfs`, `landlock/ruleset`, and `landlock/syscalls`
- the shared Phase 13 tranche entrypoints through `zigux/tests/phase13_build.zig` and `make -C zigux phase13`
- the current ready-next and blocked follow-ups for the three manifest-backed anchors

What is still asymmetric today:
- `lib/devres.c` is represented by real helper code, real tests, and a slice note, but not yet by a committed manifest-backed survey packet like the other active Phase 13 anchors

## Next bounded step

If the Phase 13 traceability lane reopens, the next honest follow-up is to give `lib/devres.c` the same manifest-backed survey shape already used by `libfs`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c`, without widening into new helper behavior.
