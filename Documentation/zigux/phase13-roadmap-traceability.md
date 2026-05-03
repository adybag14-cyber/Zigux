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
- `Documentation/zigux/phase13-release-notes-survey.md` keeps the active validator-first release reading for those same four roadmap anchors visible instead of leaving the current survey packet implicit outside this traceability note
- the same shared packet now also keeps `zigux/tests/phase13_landlock_syscalls_reviewability.zig` visible as dedicated reviewability evidence for the landed `phase13-landlock-syscalls-reviewability-tests` replay step, so the syscall anchor does not look smaller than the actual ten-step shared build on current `master`
- `lib/devres.c` is represented by real helper code, real tests, a manifest-backed survey packet, and explicit blocked DMA/scatterlist boundary evidence
- the same shared packet also keeps `zigux/tests/phase13_devres_dma_coherent.zig` and `phase13-devres-dma-coherent-tests` visible as adjacent helper-first coherent DMA alloc/free bookkeeping evidence, so the current shared replay exposes that bounded support slice without turning the blocked `devres` DMA/scatterlist boundary into a live mapping claim
- the same shared packet also keeps `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `Documentation/zigux/phase13-notifier-list-survey.md` visible as roadmap-adjacent release-facing evidence without changing the roadmap's four-anchor count

## Anchor-to-repo map

### `fs/libfs.c`

Current repo evidence:
- implementation anchor: `fs/libfs.zig`
- dedicated tests: `zigux/tests/phase13_libfs.zig`
- reviewability gate: `zigux/tests/phase13_libfs_reviewability.zig`
- manifest: `zigux/tests/phase13_libfs_manifest.json`
- manifest `surveyed_commit`: `cbc60805a6fb2cac485beb113c5d9d47f07ebdee`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice notes: `Documentation/zigux/phase13-libfs-slice.md`
- survey note: `Documentation/zigux/phase13-libfs-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-libfs-starter`
- landed `phase13-libfs-tests`
- landed `phase13-libfs-slice-note`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-survey-note`
- landed `phase13-libfs-offset-seek-helper`
- landed `phase13-libfs-directory-emit-helper`
- landed `phase13-libfs-transaction-buffer-helper`
- landed `phase13-libfs-transaction-read-release-followup`
- landed `phase13-libfs-dcache-cursor-preconditions`
- landed `phase13-libfs-dcache-cursor-reposition-bookkeeping`
- landed `phase13-libfs-dcache-dir-close-release-bookkeeping`
- landed `phase13-libfs-simple-open-private-data-planning`
- ready_next `phase13-libfs-addressability-helper`
- blocked `phase13-libfs-dcache-cursor-helpers`
- blocked `phase13-libfs-inode-and-pseudofs-lifecycle`

Traceability summary:
- this anchor stays roadmap-aligned and manifest-backed, and the helper packet now includes the tiny `dcache_dir_close()` release-bookkeeping boundary plus the pure `simple_open()` private-data handoff while still leaving one more honest pure follow-up in `generic_check_addressable()` before the lane has to stop at broader cursor traversal, inode lifecycle, or pseudo-filesystem ownership.
