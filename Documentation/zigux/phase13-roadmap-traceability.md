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
- the shared replay currently routes sixteen named steps on `master`: the four anchor-local test gates, the eight anchor-local reviewability or sync gates, the adjacent coherent-DMA and scatterlist `devres` support replays, and the two roadmap-adjacent notifier reviewability or helper-view steps
- `Documentation/zigux/phase13-release-notes-survey.md` keeps the active validator-first release reading for those same four roadmap anchors visible instead of leaving the current survey packet implicit outside this traceability note
- the same shared packet now also keeps `zigux/tests/phase13_landlock_syscalls_reviewability.zig` visible as dedicated reviewability evidence for the landed `phase13-landlock-syscalls-reviewability-tests` replay step, so the syscall anchor does not look smaller than the current shared build on `master`
- `lib/devres.c` is represented by real helper code, real tests, a manifest-backed survey packet, and explicit blocked DMA/scatterlist boundary evidence
- the same shared packet also keeps `zigux/tests/phase13_devres_dma_coherent.zig` and `phase13-devres-dma-coherent-tests` visible as adjacent helper-first coherent DMA alloc/free bookkeeping evidence, so the current shared replay exposes that bounded support slice without turning the blocked `devres` DMA/scatterlist boundary into a live mapping claim
- the same shared packet also keeps `zigux/tests/phase13_devres_iounmap_reviewability.zig`, `zigux/tests/phase13_devres_iomap_reviewability.zig`, `zigux/tests/phase13_devres_wrapper_reviewability.zig`, and `zigux/tests/phase13_landlock_ruleset_reviewability.zig` visible as dedicated reviewability evidence for the landed `phase13-devres-iounmap-reviewability-tests`, `phase13-devres-iomap-reviewability-tests`, `phase13-devres-wrapper-reviewability-tests`, and `phase13-landlock-ruleset-reviewability-tests` replay steps, so the `devres` and ruleset anchors do not look smaller than the current shared build on `master`
- the same shared packet also keeps `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `Documentation/zigux/phase13-notifier-list-survey.md` visible as roadmap-adjacent release-facing evidence without changing the roadmap's four-anchor count

## Anchor-to-repo map

### `fs/libfs.c`

Current repo evidence:
- implementation anchor: `fs/libfs.zig`
- dedicated tests: `zigux/tests/phase13_libfs.zig`
- reviewability gate: `zigux/tests/phase13_libfs_reviewability.zig`
- manifest: `zigux/tests/phase13_libfs_manifest.json`
- manifest `surveyed_commit`: `a8bb936df1520e7be16d3fdf9ee1875de398ead6`
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
- landed `phase13-libfs-addressability-helper`
- blocked `phase13-libfs-dcache-cursor-helpers`
- blocked `phase13-libfs-inode-and-pseudofs-lifecycle`

Traceability summary:
- this anchor stays roadmap-aligned and manifest-backed, and the helper packet now includes the tiny `dcache_dir_close()` release-bookkeeping boundary, the pure `simple_open()` private-data handoff, and the pure `generic_check_addressable()` addressability planner while still stopping at broader cursor traversal, inode lifecycle, and pseudo-filesystem ownership.

### `lib/devres.c`

Current repo evidence:
- implementation anchor: `lib/devres.zig`
- dedicated tests: `zigux/tests/phase13_devres.zig`
- adjacent coherent-DMA replay: `zigux/tests/phase13_devres_dma_coherent.zig`
- adjacent scatterlist helper: `lib/devres_scatterlist.zig`
- adjacent scatterlist replay: `zigux/tests/phase13_devres_scatterlist.zig`
- reviewability gates: `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_iounmap_reviewability.zig`, `zigux/tests/phase13_devres_iomap_reviewability.zig`, and `zigux/tests/phase13_devres_wrapper_reviewability.zig`
- manifest: `zigux/tests/phase13_devres_manifest.json`
- manifest `surveyed_commit`: `aa01b37be5500e6a1e4f959c9fe07f0e39d39bfb`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-devres-slice.md`
- survey note: `Documentation/zigux/phase13-devres-survey.md`
- adjacent scatterlist slice note: `Documentation/zigux/phase13-devres-scatterlist-slice.md`

Current lane state recorded in the manifest:
- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-devres-starter`
- landed `phase13-devres-tests`
- landed `phase13-devres-slice-note`
- landed `phase13-devres-reviewability-gate`
- landed `phase13-devres-survey-note`
- landed `phase13-devres-managed-ioremap-lifetime`
- landed `phase13-devres-managed-ioremap-np-wrapper`
- landed `phase13-devres-managed-resource-planner`
- landed `phase13-devres-devicetree-iomap-planner`
- landed `phase13-devres-ioport-lifetime-planner`
- landed `phase13-devres-arch-phys-wc-token-planner`
- landed `phase13-devres-arch-io-memtype-planner`
- landed `phase13-devres-dma-coherent-lifetime-planner`
- blocked `phase13-devres-live-mmio-side-effects`
- blocked `phase13-devres-live-dma-mappings`
- blocked `phase13-devres-live-scatterlist-ownership`
- blocked `phase13-devres-live-device-tree-walk`
- blocked `phase13-devres-live-arch-memtype-state`
- the same manifest-backed packet now also records the already-landed helper-first scatterlist bookkeeping slice in `lib/devres_scatterlist.zig` and `zigux/tests/phase13_devres_scatterlist.zig`, while keeping that evidence explicitly bounded to retained-record bookkeeping rather than live `sg_*` ownership

Traceability summary:
- this anchor stays roadmap-aligned and manifest-backed, and the helper packet now covers the shared build gate, make target, dedicated slice note, managed ioremap, resource-planner, ioport, direct non-posted wrapper, direct plain/UC/WC/NP ioremap wrapper-family reviewability, arch write-combine bookkeeping helpers, adjacent coherent DMA alloc/free bookkeeping, and the already-promoted helper-first scatterlist bookkeeping slice inside the shared replay.
- even with those adjacent helper slices visible, the devres anchor still refuses to claim live MMIO side effects, live DMA-backed mappings, full scatterlist ownership, live device-tree walking, or global arch-memtype mutation.
- the next honest same-family follow-up is to keep this manifest-backed packet, shared replay, and directly coupled survey note aligned if another bounded coherent-DMA or scatterlist bookkeeping step lands, rather than reopening helper implementation or widening into live DMA-backed behavior.

### `security/landlock/ruleset.c`

Current repo evidence:
- implementation anchor: `security/landlock/ruleset.zig`
- dedicated tests: `zigux/tests/phase13_landlock_ruleset.zig`
- reviewability gate: `zigux/tests/phase13_landlock_ruleset_reviewability.zig`
- manifest: `zigux/tests/phase13_landlock_ruleset_manifest.json`
- manifest `surveyed_commit`: `8812ad875b0307da2cc0fa3588b9a24325b85e17`
- shared build entry: `zigux/tests/phase13_build.zig`
- shared make entry: `zigux/Makefile` via `make -C zigux phase13`
- slice note: `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- survey note: `Documentation/zigux/phase13-landlock-ruleset-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-ruleset-starter`
- landed `phase13-landlock-ruleset-test-gate`
- landed `phase13-landlock-ruleset-reviewability-gate`
- landed `phase13-landlock-ruleset-slice-note`
- landed `phase13-landlock-ruleset-survey-note`
- landed `phase13-landlock-rule-layer-merge-followup`
- landed `phase13-landlock-tree-search-followup`
- landed `phase13-landlock-tree-link-followup`
- landed `phase13-landlock-rule-lookup-followup`
- landed `phase13-landlock-rule-materialization-followup`
- landed `phase13-landlock-rule-replacement-followup`
- landed `phase13-landlock-rule-release-followup`
- blocked `phase13-landlock-live-tree-state-blocker`

Traceability summary:
- this anchor stays helper-first and manifest-backed: the current ruleset helper packet is wired through the shared Phase 13 build and make entrypoints, records its dedicated reviewability gate plus slice and survey notes, and now includes layer-merge, tree-search, tree-link, rule-lookup, materialization, replacement, and release planners while still refusing to claim actual `rb_replace_node()` mutation, live object ownership transfer, hierarchy lifetime, or workqueue-backed teardown as pure in-memory slice work.

### `security/landlock/syscalls.c`

Current repo evidence:
- implementation anchor: `security/landlock/syscalls.zig`
- dedicated tests: `zigux/tests/phase13_landlock_syscalls.zig`
- reviewability gate: `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- same-family sync guard: `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
- manifest: `zigux/tests/phase13_landlock_syscalls_manifest.json`
- manifest `surveyed_commit`: `9c17b0790799d8240ef9f964903f5ce2db64af89`
- shared build entry: `zigux/tests/phase13_build.zig`
- slice note: `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- survey note: `Documentation/zigux/phase13-landlock-syscalls-survey.md`

Current lane state recorded in the manifest:
- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-landlock-syscalls-starter`
- landed `phase13-landlock-syscalls-test-gate`
- landed `phase13-landlock-syscalls-reviewability-gate`
- landed `phase13-landlock-syscalls-slice-note`
- landed `phase13-landlock-syscalls-survey-note`
- landed `phase13-landlock-initialization-gate-followup`
- landed `phase13-landlock-copy-min-struct-followup`
- landed `phase13-landlock-add-rule-followup`
- landed `phase13-landlock-ruleset-fd-mode-followup`
- landed `phase13-landlock-path-fd-followup`
- landed `phase13-landlock-path-beneath-handoff-followup`
- landed `phase13-landlock-net-port-import-followup`
- landed `phase13-landlock-ruleset-fd-creation-handoff-followup`
- landed `phase13-landlock-restrict-self-credential-handoff-followup`
- landed `phase13-landlock-ruleset-fops-followup`

Traceability summary:
- this anchor stays roadmap-aligned and manifest-backed, and the helper packet now covers the shared build gate, make target, the dedicated manifest-backed reviewability gate, the same-family ruleset-FD creation and `ruleset_fops` sync guard, ABI sizing, the shared boot-disabled initialization gate, bounded user-struct copy discipline, create-ruleset validation, restrict-self logging translation, restrict-self credential handoff ordering, add-rule planning, ruleset-FD lookup, path-FD lookup, path-beneath handoff, net-port handoff, ruleset-FD creation handoff planning, and the dedicated ruleset file-operations contract while still refusing to claim live user-memory access, live FD ownership, anonymous inode internals, credential updates, domain merges, or syscall enforcement.

## Roadmap-adjacent evidence that is not a fifth anchor

The shared Phase 13 replay on `master` also includes one adjacent reviewability packet that helps explain current repo footing without changing the roadmap anchor count:

- reviewability gate: `zigux/tests/phase13_notifier_list_reviewability.zig`
- manifest: `zigux/tests/phase13_notifier_list_manifest.json`
- manifest `lane_key`: `P13-L19`
- manifest `surveyed_commit`: `66b55d8a9a800345097f3c04b9f95130b1f8d0b8`
- survey note: `Documentation/zigux/phase13-notifier-list-survey.md`
- read-only generic notifier ABI foothold: `zigux/bindings/notifier_abi.zig`
- dedicated exported C header foothold: `include/zigux/notifier_abi.h`
- bounded raw-notifier traversal helper: `zigux/helpers/notifier_chain_view.zig`

Why this packet belongs here but stays outside the anchor count:

- it documents roadmap-adjacent shared-helper footing around preexisting `list_head` or `hlist` ABI surfaces, public generic-notifier header anchors, and the now-landed Zigux-side generic notifier ABI, dedicated exported C header, or helper foothold
- it is already part of the shared `zigux/tests/phase13_build.zig` replay through both `phase13-notifier-list-reviewability-tests` and `phase13-notifier-chain-view-tests`, so future runs need to see why those tests exist without mistaking them for a new roadmap closure claim
- it keeps the next honest same-family follow-up explicit: preserve this tiny read-only notifier ABI, exported C header, and helper foothold as roadmap-adjacent support evidence, and only widen later work if the shared-helper tranche genuinely needs more than the bounded helper-first linkage survey already landed here

Traceability consequence:
- the four roadmap anchors above remain the only Phase 13 anchor count for this note
- the notifier-list packet is supporting evidence for the current shared-helper tranche, not a substitute for `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, or `security/landlock/syscalls.c`
- future docs-root, release-note, or checklist updates should keep the current sixteen-step shared replay visible together with the dedicated `zigux/tests/phase13_landlock_syscalls_reviewability.zig` gate and the same-family `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` guard, plus the roadmap-adjacent notifier packet including `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`, while continuing to describe Phase 13 closure through the four manifest-backed roadmap anchors only
