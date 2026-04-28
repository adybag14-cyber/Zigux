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

Adjacent Phase 13 reviewability evidence already present on `master`:
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `Documentation/zigux/phase13-notifier-list-survey.md`

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
- reviewability gate: `zigux/tests/phase13_devres_reviewability.zig`
- manifest: `zigux/tests/phase13_devres_manifest.json`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-devres-slice.md`
- survey note: `Documentation/zigux/phase13-devres-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-devres-starter`
- landed `phase13-devres-tests`
- landed `phase13-devres-slice-note`
- landed `phase13-devres-reviewability-gate`
- landed `phase13-devres-survey-note`
- landed `phase13-devres-managed-ioremap-lifetime`
- landed `phase13-devres-managed-resource-planner`
- landed `phase13-devres-devicetree-iomap-planner`
- landed `phase13-devres-ioport-lifetime-planner`
- landed `phase13-devres-arch-phys-wc-token-planner`
- landed `phase13-devres-arch-io-memtype-planner`
- blocked `phase13-devres-live-mmio-side-effects`
- blocked `phase13-devres-live-dma-mappings`
- blocked `phase13-devres-live-scatterlist-ownership`
- blocked `phase13-devres-live-device-tree-walk`
- blocked `phase13-devres-live-arch-memtype-state`

Traceability summary:
- `lib/devres.c` is represented by real helper code, real tests, a manifest-backed survey packet, and explicit blocked DMA/scatterlist boundary evidence, so it is no longer the asymmetric Phase 13 anchor even though its live MMIO, device-tree, DMA, scatterlist, and arch-memtype behavior remain intentionally out of scope.

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
- landed `phase13-landlock-rule-release-followup`
- blocked `phase13-landlock-live-tree-state-blocker`

Traceability summary:
- this anchor is roadmap-aligned and manifest-backed, with the current repo explicitly separating the helper-only in-memory lab from the still-blocked live Landlock tree-state, release ownership, and hierarchy-lifetime work.

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
- landed `phase13-landlock-path-beneath-handoff-followup`
- landed `phase13-landlock-net-port-import-followup`
- landed `phase13-landlock-ruleset-fd-creation-handoff-followup`

Traceability summary:
- this anchor is also roadmap-aligned and manifest-backed, with the current repo keeping the syscall helper slice explicit about ABI, create-ruleset, add-rule, ruleset-FD lookup, path-FD lookup, path-beneath handoff, net-port handoff, and ruleset-FD creation handoff planning while still blocking live path import, credential mutation, and enforcement claims.

## Phase 13 traceability status

What is fully traceable today:
- the roadmap-to-repo path for `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls`
- the shared Phase 13 tranche entrypoints through `zigux/tests/phase13_build.zig` and `make -C zigux phase13`
- the current landed versus blocked follow-ups for all four manifest-backed roadmap anchors

What is additionally reviewable today without being a new roadmap anchor:
- the shared `phase13_notifier_list_reviewability` packet records how the existing Phase 3 `list` and `hlist` ABI footholds, the current `list_view` and `hlist_view` helpers, and the chrdev-local notifier planner relate to the still-missing generic notifier ABI and helper surface
- this packet lives in `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, and `Documentation/zigux/phase13-notifier-list-survey.md`
- it should be read as Phase 13 reviewability evidence around preexisting shared-helper surfaces, not as a fifth roadmap anchor beside `libfs`, `devres`, or the two Landlock slices

What stays intentionally blocked today:
- `fs/libfs.c` still keeps the ready-next dcache-cursor reposition bookkeeping step separate from the blocked dcache-cursor helpers and inode or pseudofs lifecycle work, so the current helper packet does not overstate broader inode-state handling
- `lib/devres.c` still keeps live MMIO side effects, live DMA-backed mappings, live scatterlist ownership, live device-tree walking, and live arch memtype state out of scope even though its helper-first survey packet is now manifest-backed
- `security/landlock/ruleset.c` still keeps live Landlock tree-state ownership, rule-release ownership, and hierarchy-lifetime behavior outside the current in-memory helper lab even though the ruleset anchor is manifest-backed
- `security/landlock/syscalls.c` still keeps live path import, credential mutation, and enforcement claims out of scope even though the syscall helper slice already records the current bounded handoff planning

## Next bounded step

If the Phase 13 traceability lane reopens, the next honest follow-up is to keep this note aligned with the shared release-discipline packet and any future manifest-backed status changes inside the four roadmap anchors, without widening into new helper behavior.
