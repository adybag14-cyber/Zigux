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
- `lib/devres.c` is represented by real helper code, real tests, a manifest-backed survey packet, and explicit blocked DMA/scatterlist boundary evidence

## Anchor-to-repo map

### `fs/libfs.c`

Current repo evidence:
- implementation anchor: `fs/libfs.zig`
- dedicated tests: `zigux/tests/phase13_libfs.zig`
- reviewability gate: `zigux/tests/phase13_libfs_reviewability.zig`
- manifest: `zigux/tests/phase13_libfs_manifest.json`
- manifest `surveyed_commit`: `ba74bb197b16b020ec02b876efdd154663c6a146`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice notes: `Documentation/zigux/phase13-libfs-slice.md`
- survey note: `Documentation/zigux/phase13-libfs-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-libfs-helper-starter`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-dcache-cursor-preconditions`
- landed `phase13-libfs-dcache-cursor-reposition-bookkeeping`
- landed `phase13-libfs-dcache-dir-close-release-bookkeeping`
- blocked `phase13-libfs-dcache-cursor-helpers`
- blocked `phase13-libfs-inode-and-pseudofs-lifecycle`

Traceability summary:
- this anchor stays roadmap-aligned and manifest-backed, and the helper packet now includes the tiny `dcache_dir_close()` release-bookkeeping boundary while still refusing to claim broader cursor traversal, inode lifecycle, or pseudo-filesystem ownership.

### `lib/devres.c`

Current repo evidence:
- implementation anchor: `lib/devres.zig`
- dedicated tests: `zigux/tests/phase13_devres.zig`
- reviewability gate: `zigux/tests/phase13_devres_reviewability.zig`
- manifest: `zigux/tests/phase13_devres_manifest.json`
- manifest `surveyed_commit`: `aa01b37be5500e6a1e4f959c9fe07f0e39d39bfb`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-devres-slice.md`
- survey note: `Documentation/zigux/phase13-devres-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-devres-starter`
- landed `phase13-devres-tests`
- landed `phase13-devres-reviewability-gate`
- landed `phase13-devres-survey-note`
- landed `phase13-devres-managed-ioremap-lifetime`
- landed `phase13-devres-managed-ioremap-np-wrapper`
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
- this anchor stays roadmap-aligned and manifest-backed, and the helper packet now covers managed ioremap, resource-planner, ioport, direct non-posted wrapper, and arch write-combine bookkeeping helpers while still refusing to claim live MMIO side effects, live DMA-backed mappings, scatterlist ownership, live device-tree walking, or global arch-memtype mutation.

### `security/landlock/ruleset.c`

Current repo evidence:
- implementation anchor: `security/landlock/ruleset.zig`
- dedicated tests: `zigux/tests/phase13_landlock_ruleset.zig`
- manifest: `zigux/tests/phase13_landlock_ruleset_manifest.json`
- manifest `surveyed_commit`: `c2e6f75f05a6f935d21d06d21494d71883a5fa49`
- slice notes: `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- survey note: `Documentation/zigux/phase13-landlock-ruleset-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-landlock-rule-materialization-followup`
- landed `phase13-landlock-rule-release-followup`
- blocked `phase13-landlock-live-tree-state-blocker`

Traceability summary:
- this anchor stays helper-first and reviewable: the current ruleset helper lab now includes canonical layer-shape validation around `create_rule()`-style copied or appended layer stacks beside the earlier materialization and release planners, while the still-blocked live Landlock tree-state, release ownership, and hierarchy-lifetime work remains outside this pure in-memory slice.

### `security/landlock/syscalls.c`

Current repo evidence:
- implementation anchor: `security/landlock/syscalls.zig`
- dedicated tests: `zigux/tests/phase13_landlock_syscalls.zig`
- manifest: `zigux/tests/phase13_landlock_syscalls_manifest.json`
- manifest `surveyed_commit`: `09229747ad125661be1d17d3d55d87ef11cd33e4`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- survey note: `Documentation/zigux/phase13-landlock-syscalls-survey.md`

Current lane state recorded in the manifest:
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
- this anchor stays roadmap-aligned and manifest-backed, and the helper packet now covers ABI sizing, bounded user-struct copy discipline, create-ruleset validation, restrict-self logging translation, add-rule planning, ruleset-FD lookup, path-FD lookup, path-beneath handoff, net-port handoff, and ruleset-FD creation handoff planning while still refusing to claim live user-memory access, live FD ownership, anonymous inode internals, credential updates, domain merges, or syscall enforcement.
