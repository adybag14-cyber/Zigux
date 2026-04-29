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

Current shared replay inventory recorded in `zigux/tests/phase13_build.zig`:
- `phase13-libfs-tests`
- `phase13-devres-tests`
- `phase13-landlock-ruleset-tests`
- `phase13-landlock-syscalls-tests`
- `phase13-libfs-reviewability-tests`
- `phase13-devres-reviewability-tests`
- `phase13-notifier-list-reviewability-tests`

Adjacent Phase 13 reviewability evidence already present on `master`:
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `Documentation/zigux/phase13-notifier-list-survey.md`

## Lane and validation map

The roadmap asks each active commit series to stay reviewable through an explicit phase, status bucket, and validation gate. For the current Phase 13 shared-helper tranche, those details are already carried by the per-anchor manifests plus the shared release and replay entrypoints:

- `fs/libfs.c`: manifest lane `P13-L04` in `zigux/tests/phase13_libfs_manifest.json`; dedicated gates `zigux/tests/phase13_libfs.zig` and `zigux/tests/phase13_libfs_reviewability.zig`; shared gates `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zigux/tests/phase13_build.zig`, and `make -C zigux phase13`
- `lib/devres.c`: manifest lane `P13-L08` in `zigux/tests/phase13_devres_manifest.json`; dedicated gates `zigux/tests/phase13_devres.zig` and `zigux/tests/phase13_devres_reviewability.zig`; shared gates `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zigux/tests/phase13_build.zig`, and `make -C zigux phase13`
- `security/landlock/ruleset.c`: manifest lane `P13-L12` in `zigux/tests/phase13_landlock_ruleset_manifest.json`; dedicated gate `zigux/tests/phase13_landlock_ruleset.zig`; shared gates `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zigux/tests/phase13_build.zig`, and `make -C zigux phase13`
- `security/landlock/syscalls.c`: manifest lane `P13-L16` in `zigux/tests/phase13_landlock_syscalls_manifest.json`; dedicated gate `zigux/tests/phase13_landlock_syscalls.zig`; shared gates `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zigux/tests/phase13_build.zig`, and `make -C zigux phase13`

The adjacent notifier-list reviewability packet stays separate from the four roadmap anchors, but its current release-facing ownership is also explicit through manifest lane `P13-L17` in `zigux/tests/phase13_notifier_list_manifest.json`, its dedicated gate `zigux/tests/phase13_notifier_list_reviewability.zig`, and the same shared Phase 13 validator-plus-replay entrypoints.

This traceability note does not add a new rollback-owner record. It only surfaces the lane-key and validation-gate evidence that is already present in the published Phase 13 packet.

## Anchor-to-repo map

### `fs/libfs.c`

Current repo evidence:
- implementation anchor: `fs/libfs.zig`
- dedicated tests: `zigux/tests/phase13_libfs.zig`
- reviewability gate: `zigux/tests/phase13_libfs_reviewability.zig`
- manifest: `zigux/tests/phase13_libfs_manifest.json`
- manifest `surveyed_commit`: `ff87456109937e1ffbe7f2a91a79c2661874ef88`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice notes: `Documentation/zigux/phase13-libfs-slice.md`
- survey note: `Documentation/zigux/phase13-libfs-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-libfs-helper-starter`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-dcache-cursor-preconditions`
- landed `phase13-libfs-dcache-cursor-reposition-bookkeeping`
- ready-next `phase13-libfs-dcache-dir-close-release-bookkeeping`
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
- manifest `surveyed_commit`: `3f74e747aa08fd80bf4db8d7b085aa5293bb53ef`
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
- manifest `surveyed_commit`: `c2e6f75f05a6f935d21d06d21494d71883a5fa49`
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
- manifest `surveyed_commit`: `c8c16be55d6f9ae1adc2860fde3aabf9d64cf95d`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- survey note: `Documentation/zigux/phase13-landlock-syscalls-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-syscalls-starter`
- landed `phase13-landlock-syscalls-test-gate`
- landed `phase13-landlock-syscalls-slice-note`
- landed `phase13-landlock-syscalls-survey-note`
- landed `phase13-landlock-copy-min-struct-followup`
- landed `phase13-landlock-add-rule-followup`
- landed `phase13-landlock-ruleset-fd-mode-followup`
- landed `phase13-landlock-path-fd-followup`
- landed `phase13-landlock-path-beneath-handoff-followup`
- landed `phase13-landlock-net-port-import-followup`
- landed `phase13-landlock-ruleset-fd-creation-handoff-followup`

Traceability summary:
- this anchor is roadmap-aligned and manifest-backed, with the current repo keeping the syscall helper slice explicit about ABI sizing, bounded `copy_min_struct_from_user()` discipline, create-ruleset query and mask validation, `landlock_restrict_self()` logging-flag translation, add-rule validation, ruleset-FD lookup, path-FD lookup, path-beneath handoff, net-port handoff, and ruleset-FD creation handoff planning while still blocking live user-memory access, live path import, credential mutation, and enforcement claims.

## Phase 13 traceability status

What is fully traceable today:
- the roadmap-to-repo path for `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls`
- the shared Phase 13 tranche entrypoints through `zigux/tests/phase13_build.zig` and `make -C zigux phase13`
- the exact shared replay inventory of seven named test or reviewability steps inside `zigux/tests/phase13_build.zig`
- the per-anchor lane-key owners and dedicated-versus-shared validation gates carried by the four roadmap-anchor manifests
- the per-anchor manifest `surveyed_commit` anchors for `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls`
- the current landed versus blocked follow-ups for all four manifest-backed roadmap anchors

What is additionally reviewable today without being a new roadmap anchor:
- the shared `phase13_notifier_list_reviewability` packet records how the existing Phase 3 `list` and `hlist` ABI footholds, the current `list_view` and `hlist_view` helpers, and the chrdev-local notifier planner relate to the still-missing generic notifier ABI and helper surface
- this packet lives in `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, and `Documentation/zigux/phase13-notifier-list-survey.md`
- it should be read as Phase 13 reviewability evidence around preexisting shared-helper surfaces, not as a fifth roadmap anchor beside `libfs`, `devres`, or the two Landlock slices

What stays intentionally blocked today:
- `fs/libfs.c` now records the landed cursor-reposition bookkeeping step and keeps the next close-path release planner separate from the blocked dcache-cursor helpers and inode or pseudofs lifecycle work, so the current helper packet still does not overstate broader inode-state handling
- `lib/devres.c` still keeps live MMIO side effects, live DMA-backed mappings, live scatterlist ownership, live device-tree walking, and live arch memtype state out of scope even though its helper-first survey packet is now manifest-backed
- `security/landlock/ruleset.c` still keeps live Landlock tree-state ownership, rule-release ownership, and hierarchy-lifetime behavior outside the current in-memory helper lab even though the ruleset anchor is manifest-backed
- `security/landlock/syscalls.c` still keeps live user-memory access, live path import, credential mutation, and enforcement claims out of scope even though the syscall helper packet now records ABI sizing, bounded struct-copy discipline, create-ruleset and restrict-self planning, and the current FD or path handoff planners

## Next bounded step

If the Phase 13 traceability lane reopens, the next honest follow-up is to keep this note aligned with the shared release-discipline packet and any future manifest-backed status, lane-key, or validation-gate changes inside the four roadmap anchors, without widening into new helper behavior.
