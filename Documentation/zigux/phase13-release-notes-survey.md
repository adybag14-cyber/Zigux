# Phase 13 Release Notes Survey

This note records the current release-facing reading for the active Phase 13 shared-helper tranche without claiming global phase closure.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_TRANCHE=shared-helper-bundle`
- `PHASE13_RELEASE_SURVEY=present`
- `PHASE13_RELEASE_VALIDATOR=present`
- scope: roadmap traceability, validator-first entrypoints, the four manifest-backed roadmap anchors already present on `master`, the roadmap-adjacent notifier-list reviewability packet, and the helper-first `devres` DMA or scatterlist boundary plus its adjacent coherent-DMA, scatterlist, `devm_iounmap()`, `devm_of_iomap()`, and direct managed-wrapper reviewability replays
- adjacent same-anchor boundary: current `master` already promotes the helper-first scatterlist bookkeeping slice into `zigux/tests/phase13_devres_manifest.json` and `zigux/tests/phase13_build.zig`, so the shared release packet now treats that slice as bounded release evidence while continuing to block live DMA-backed mappings and live scatterlist ownership
- product boundary:
  - `scripts/zigux/validate-phase13-release.py`
  - `scripts/zigux/check-phase13-libfs-packet.py`
  - `scripts/zigux/check-phase13-devres-packet.py`
  - `scripts/zigux/check-phase13-devres-inventory-contract.py`
  - `scripts/zigux/check-phase13-notifier-packet.py`
  - `scripts/zigux/check-phase13-release-replay-exact-counts.py`
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase13-roadmap-traceability.md`
  - `Documentation/zigux/phase13-devres-survey.md`
  - `Documentation/zigux/phase13-devres-scatterlist-slice.md`
  - `.github/workflows/zigux-bootstrap.yml`
  - `zigux/Makefile`
  - `zigux/tests/phase13_build.zig`
  - `zigux/tests/phase13_libfs_manifest.json`
  - `zigux/tests/phase13_devres_manifest.json`
  - `zigux/tests/phase13_landlock_ruleset_manifest.json`
  - `zigux/tests/phase13_landlock_syscalls_manifest.json`
  - `zigux/tests/phase13_notifier_list_manifest.json`
  - `zigux/tests/phase13_libfs.zig`
  - `zigux/tests/phase13_libfs_reviewability.zig`
  - `zigux/tests/phase13_devres.zig`
  - `zigux/tests/phase13_devres_dma_coherent.zig`
  - `zigux/tests/phase13_devres_scatterlist.zig`
  - `zigux/tests/phase13_devres_iounmap_reviewability.zig`
  - `zigux/tests/phase13_devres_iomap_reviewability.zig`
  - `zigux/tests/phase13_devres_reviewability.zig`
  - `zigux/tests/phase13_devres_wrapper_reviewability.zig`
  - `zigux/tests/phase13_landlock_ruleset.zig`
  - `zigux/tests/phase13_landlock_ruleset_reviewability.zig`
  - `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
  - `zigux/tests/phase13_landlock_syscalls.zig`
  - `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  - `zigux/tests/phase13_notifier_list_reviewability.zig`
  - `zigux/bindings/notifier_abi.zig`
  - `include/zigux/notifier_abi.h`
  - `zigux/helpers/notifier_chain_view.zig`

## Why this record exists

The Phase 13 roadmap names four shared-helper anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

The live repo already carries real helper code, dedicated tests, manifest-backed survey packets, and one shared replay route for those anchors. This note keeps the release-facing reading of that bundle explicit so later runs do not mistake helper-first reviewability work for broader runtime closure.

## Current release reading

- `fs/libfs.c`: helper slice landed, dedicated tests present, dedicated reviewability gate present, roadmap traceability present, and manifest-backed survey present
- `lib/devres.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey present, and helper-first MMIO or resource planners still keep live DMA-backed mappings and live scatterlist ownership explicitly blocked
- the shared replay now also keeps the adjacent helper-first coherent-DMA alloc or free bookkeeping replay visible through `phase13-devres-dma-coherent-tests` without turning the blocked devres DMA or scatterlist boundary into a live DMA-backed mapping claim
- the shared replay now also keeps the adjacent helper-first scatterlist bookkeeping replay visible through `phase13-devres-scatterlist-tests` and `zigux/tests/phase13_devres_scatterlist.zig` so the already-landed retained-record and exact-unmap-match slice is release-visible without turning the blocked devres DMA or scatterlist boundary into a live scatterlist ownership claim
- the shared replay now also keeps the dedicated `phase13-devres-iounmap-reviewability-tests`, `phase13-devres-iomap-reviewability-tests`, and `phase13-devres-wrapper-reviewability-tests` gates visible so the helper-advertised `devres` release, device-tree iomap, and direct managed-wrapper surfaces do not look smaller than the actual shared replay on current `master`
- `security/landlock/ruleset.c`: helper slice landed, dedicated tests present, dedicated reviewability gate present, roadmap traceability present, and manifest-backed survey present
- `security/landlock/syscalls.c`: helper slice landed, dedicated tests present, dedicated reviewability gate present, roadmap traceability present, and manifest-backed survey present
- the roadmap-adjacent notifier-list packet remains useful release evidence through `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`, but it does not change the roadmap anchor count
- `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zig build test --build-file zigux/tests/phase13_build.zig --summary all`, and `make -C zigux phase13` are the published validator-first and shared replay path for the current packet
- the shared release packet also keeps the dedicated `scripts/zigux/check-phase13-libfs-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-inventory-contract.py`, `scripts/zigux/check-phase13-notifier-packet.py`, and `scripts/zigux/check-phase13-release-replay-exact-counts.py` guards visible, so route, manifest, and replay-count drift fail closed before the shared build claims reviewable coverage

- `PHASE13_ROADMAP_ANCHOR_COUNT=4`
- `PHASE13_MANIFEST_BACKED_SURVEY_COUNT=4`
- `PHASE13_ACTIVE_ASYMMETRIC_ANCHOR_COUNT=0`
- `PHASE13_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase13-release.py`
- `PHASE13_VALIDATE_ENTRYPOINT=make -C zigux phase13-validate`
- `PHASE13_SHARED_BUILD_PRESENT=yes`
- `PHASE13_SHARED_MAKE_TARGET_PRESENT=yes`
- `PHASE13_SHARED_REPLAY_STEP_COUNT=16`
- `PHASE13_RELEASE_CLOSED=no`

## Manifest Lane Ownership

The current manifest lane ownership carried by this release packet is:

- `fs/libfs.c` through `zigux/tests/phase13_libfs_manifest.json` lane `P13-L04`
- `lib/devres.c` through `zigux/tests/phase13_devres_manifest.json` lane `P13-L10`
- `security/landlock/ruleset.c` through `zigux/tests/phase13_landlock_ruleset_manifest.json` lane `P13-L12`
- `security/landlock/syscalls.c` through `zigux/tests/phase13_landlock_syscalls_manifest.json` lane `P13-L16`
- roadmap-adjacent notifier-list reviewability evidence through `zigux/tests/phase13_notifier_list_manifest.json` lane `P13-L19`

## Shared Replay Inventory

The current shared replay inventory is:

- `phase13-libfs-tests`
- `phase13-devres-tests`
- `phase13-devres-dma-coherent-tests`
- `phase13-devres-scatterlist-tests`
- `phase13-devres-iounmap-reviewability-tests`
- `phase13-devres-iomap-reviewability-tests`
- `phase13-landlock-ruleset-tests`
- `phase13-landlock-ruleset-reviewability-tests`
- `phase13-landlock-syscalls-tests`
- `phase13-landlock-syscalls-reviewability-tests`
- `phase13-landlock-ruleset-fops-sync-tests`
- `phase13-libfs-reviewability-tests`
- `phase13-devres-reviewability-tests`
- `phase13-devres-wrapper-reviewability-tests`
- `phase13-notifier-list-reviewability-tests`
- `phase13-notifier-chain-view-tests`

## Evidence Set

The current bounded release-evidence set is:

- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/check-phase13-libfs-packet.py`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-devres-inventory-contract.py`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `scripts/zigux/check-phase13-release-replay-exact-counts.py`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_iounmap_reviewability.zig`
- `zigux/tests/phase13_devres_iomap_reviewability.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_wrapper_reviewability.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_reviewability.zig`
- `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/notifier_chain_view.zig`

## Gates

1. validate the shared release-discipline packet
- `python3 scripts/zigux/validate-phase13-release.py`

2. run the make-level validation entrypoint
- `make -C zigux phase13-validate`

3. run the shared Phase 13 helper replay
- `zig build test --build-file zigux/tests/phase13_build.zig --summary all`

4. run the Linux-style convenience entrypoint
- `make -C zigux phase13`

## Non-goals

This survey does not claim:

- global Phase 13 closure
- live MMIO mappings, live device-resource teardown parity, or generic devres-group ownership
- live DMA-backed helpers, live scatterlist ownership, or detach-time scatter-gather cleanup beyond the current helper-first coherent-DMA and scatterlist bookkeeping slices
- live Landlock enforcement, live tree-state ownership transfer, or broader syscall-enforcement parity
- notifier registration, callback execution, SRCU, blocking-notifier semantics, or a fifth roadmap anchor beyond the current roadmap-adjacent notifier evidence packet

## Next Bounded Step

If this shared Phase 13 release lane reopens, keep the release note and release-facing validators aligned with the current sixteen-step replay and the manifest-backed `devres` DMA or scatterlist boundary packet. The next honest follow-up is another release-local anti-drift correction only if a later helper-family lane changes the shared replay inventory or the release-facing boundary reading again.