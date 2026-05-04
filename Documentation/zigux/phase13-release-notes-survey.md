# Phase 13 Release Notes Survey

This document records the current release-discipline reading for the active Phase 13 shared-helper tranche without claiming that the roadmap phase is globally closed.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_TRANCHE=shared-helper-bundle`
- `PHASE13_RELEASE_SURVEY=present`
- `PHASE13_RELEASE_VALIDATOR=present`
- scope: roadmap traceability, shared helper replay entrypoints, the four manifest-backed survey packets already present on `master`, the adjacent notifier-list reviewability packet plus its landed read-only generic notifier foothold and dedicated exported C header, and the explicit helper-only `devres` DMA/scatterlist boundary plus its adjacent coherent DMA and `devm_iounmap()` plus `devm_of_iomap()` plus direct managed-ioremap-wrapper reviewability replays
- adjacent same-anchor note boundary: `Documentation/zigux/phase13-devres-survey.md` and `Documentation/zigux/phase13-roadmap-traceability.md` already record the helper-first scatterlist bookkeeping slice beside `lib/devres.zig`, but that same-anchor evidence is still note-local and not yet promoted into `zigux/tests/phase13_devres_manifest.json` or `zigux/tests/phase13_build.zig`
- product boundary:
  - `scripts/zigux/validate-phase13-release.py`
  - `scripts/zigux/check-phase13-libfs-packet.py`
  - `scripts/zigux/check-phase13-devres-packet.py`
  - `scripts/zigux/check-phase13-devres-inventory-contract.py`
  - `scripts/zigux/check-phase13-notifier-packet.py`
  - `scripts/zigux/check-phase13-release-replay-exact-counts.py`
  - `scripts/zigux/README.md`
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase13-roadmap-traceability.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `.github/workflows/zigux-bootstrap.yml`
  - `zigux/tests/phase13_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase13-libfs-slice.md`
  - `Documentation/zigux/phase13-libfs-survey.md`
  - `Documentation/zigux/phase13-devres-slice.md`
  - `Documentation/zigux/phase13-devres-survey.md`
  - `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  - `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  - `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  - `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  - `Documentation/zigux/phase13-notifier-list-survey.md`
  - `zigux/tests/phase13_libfs_manifest.json`
  - `zigux/tests/phase13_devres_manifest.json`
  - `zigux/tests/phase13_landlock_ruleset_manifest.json`
  - `zigux/tests/phase13_landlock_syscalls_manifest.json`
  - `zigux/tests/phase13_notifier_list_manifest.json`
  - `zigux/tests/phase13_libfs_reviewability.zig`
  - `zigux/tests/phase13_devres.zig`
  - `zigux/tests/phase13_devres_dma_coherent.zig`
  - `zigux/tests/phase13_devres_iounmap_reviewability.zig`
  - `zigux/tests/phase13_devres_iomap_reviewability.zig`
  - `zigux/tests/phase13_devres_reviewability.zig`
  - `zigux/tests/phase13_devres_wrapper_reviewability.zig`
  - `zigux/tests/phase13_landlock_ruleset_reviewability.zig`
  - `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  - `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
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

The live repo already carries real helper code, dedicated tests, and shared replay wiring for those anchors, plus one adjacent notifier-list reviewability packet that helps explain preexisting list or hlist helper footing without claiming a fifth roadmap anchor.

What this record needs to say, in one place, is how to read that bundle today:

- Phase 13 is active, not closed
- the current tranche is reviewable through `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zig build test --build-file zigux/tests/phase13_build.zig --summary all`, and `make -C zigux phase13`
- the shared bootstrap workflow mirrors that same validator-first release path through `Validate Phase 13 release-discipline packet` and `Run Phase 13 shared helper tests`, so release-facing reviewability is not hidden only in local commands
- the validator helper itself is part of the published evidence packet through `scripts/zigux/README.md`, so the fast-check contract is documented alongside the release note instead of living only in the script and workflow wiring
- the shared release packet also keeps the dedicated `scripts/zigux/check-phase13-libfs-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-inventory-contract.py`, and `scripts/zigux/check-phase13-notifier-packet.py` guards visible as part of that published review path, so the libfs helper packet, the stricter helper-first `devres` boundary contract, the machine-checked `devres` inventory contract, and the adjacent notifier reviewability packet are not left implicit in packet-local notes or the shared build alone
- the shared release packet also keeps the dedicated `scripts/zigux/check-phase13-release-replay-exact-counts.py` guard visible as part of that published review path, so the fifteen-step shared replay inventory and its `PHASE13_SHARED_REPLAY_STEP_COUNT=15` marker are not left implicit in `zigux/tests/phase13_build.zig`, `zigux/Makefile`, and the workflow alone
- the shared release packet now also needs to say plainly that the dedicated `phase13-devres-iounmap-reviewability-tests` and `phase13-devres-iomap-reviewability-tests` steps are part of the same shared replay packet instead of floating only in `zigux/tests/phase13_build.zig`
- the shared release packet now also needs to say plainly that the dedicated `phase13-devres-wrapper-reviewability-tests` step is part of the same shared replay packet instead of floating only in `zigux/tests/phase13_build.zig` and `Documentation/zigux/phase13-devres-survey.md`
- the shared release packet now also needs to say plainly that the dedicated `phase13-landlock-ruleset-fops-sync-tests` step is part of the same shared replay packet instead of floating only in `zigux/tests/phase13_build.zig`
- `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls` all already have manifest-backed survey packets
- the shared release packet now needs to say plainly that `devres` is manifest-backed while still blocking live DMA-backed mappings and scatterlist ownership, that the adjacent coherent DMA replay is part of the shared build without turning that blocked boundary into a live DMA-backed mapping claim, that the dedicated `scripts/zigux/check-phase13-devres-inventory-contract.py` guard keeps the helper packet's landed versus blocked inventory machine-checkable from the shared release route, and that the adjacent notifier packet now includes the dedicated exported C header `include/zigux/notifier_abi.h` alongside `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, and `phase13-notifier-list-reviewability-tests` instead of leaving that export surface visible only in the packet-local survey note
- `Documentation/zigux/README.md` now also keeps the dedicated `zigux/tests/phase13_landlock_syscalls_reviewability.zig` gate and the roadmap-adjacent notifier evidence (`zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, and `zigux/helpers/notifier_chain_view.zig`) visible from the docs root, so the top-level Phase 13 summary does not undercount the actual fifteen-step shared replay on current `master`
- the shared release packet also needs to say plainly that the dedicated `phase13-landlock-ruleset-reviewability-tests` and `phase13-landlock-syscalls-reviewability-tests` steps are part of the same shared replay packet instead of floating only in `zigux/tests/phase13_build.zig`
- the shared release packet also needs to separate historical manifest-owner lane keys from the newer helper-versus-verify sequencing lanes, so future runs do not reopen helper-local libfs or devres work from the shared release note alone

This survey keeps that release reading aligned without inventing new helper progress.

## Current release reading

The current Phase 13 release-facing reading is:

- `fs/libfs.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey present, and the landed `generic_check_addressable()` planner keeps the last pure non-live addressability step explicit while deeper cursor traversal, inode lifecycle work, and pseudo-filesystem ownership stay blocked on live VFS state
- `lib/devres.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey present, and helper-first MMIO or resource planners keep live DMA-backed mappings and scatterlist ownership explicitly blocked
- current `master` also carries adjacent helper-first scatterlist bookkeeping evidence through `Documentation/zigux/phase13-devres-survey.md` and `Documentation/zigux/phase13-roadmap-traceability.md`, but that same-anchor slice is still note-local and not yet promoted into `zigux/tests/phase13_devres_manifest.json` or `zigux/tests/phase13_build.zig`, so the shared release packet still treats live scatterlist ownership as blocked rather than implied
- `security/landlock/ruleset.c`: helper slice landed, dedicated tests present, dedicated reviewability gate present, roadmap traceability present, manifest-backed survey present
- `security/landlock/syscalls.c`: helper slice landed, dedicated tests present, dedicated reviewability gate present, roadmap traceability present, manifest-backed survey present
- the shared bootstrap workflow replays the same validator-plus-build contract through `Validate Phase 13 release-discipline packet` and `Run Phase 13 shared helper tests`
- the shared replay inventory now also keeps the dedicated `scripts/zigux/check-phase13-libfs-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-inventory-contract.py`, and `scripts/zigux/check-phase13-notifier-packet.py` guards visible, so the validator-first route still names the libfs helper packet, the stricter helper-first `devres` boundary contract, the machine-checked `devres` inventory contract, and the adjacent notifier reviewability packet before the fifteen-step replay bundle runs
- the shared replay inventory now also keeps the dedicated `scripts/zigux/check-phase13-release-replay-exact-counts.py` guard visible, so the published fifteen-step replay list and `PHASE13_SHARED_REPLAY_STEP_COUNT=15` marker do not drift behind the validator-first route
- the shared replay now also keeps the adjacent helper-first coherent DMA alloc/free bookkeeping replay visible through `phase13-devres-dma-coherent-tests` without turning the blocked devres DMA/scatterlist boundary into a live DMA-backed mapping claim
- the shared replay now also keeps the dedicated `phase13-devres-iounmap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iounmap_reviewability.zig` so the helper-advertised `devm_iounmap()` planning surface does not look smaller than the actual shared replay on current `master`
- the shared replay now also keeps the dedicated `phase13-devres-iomap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iomap_reviewability.zig` so the helper-advertised `devm_of_iomap()` planning surface does not look smaller than the actual shared replay on current `master`
- the shared replay now also keeps the dedicated `phase13-devres-wrapper-reviewability-tests` gate visible through `zigux/tests/phase13_devres_wrapper_reviewability.zig` so the direct plain, uncached, write-combined, and non-posted managed `devres` ioremap wrapper family does not look smaller than the actual shared replay on current `master`
- the shared replay now also keeps the dedicated Landlock ruleset reviewability gate visible through `phase13-landlock-ruleset-reviewability-tests` so the manifest-backed ruleset helper packet does not look smaller than the actual published replay on current `master`
- the shared replay now also keeps the dedicated `phase13-landlock-ruleset-fops-sync-tests` gate visible through `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` so the ruleset-fd creation and explicit fops planning surface does not look smaller than the actual shared replay on current `master`
- the shared replay now also keeps the dedicated Landlock syscall reviewability gate visible through `phase13-landlock-syscalls-reviewability-tests` so the manifest-backed syscall helper packet does not look smaller than the actual published replay on current `master`
- the adjacent notifier-list packet now stays visible as roadmap-adjacent release evidence, and its shared release packet includes the landed read-only generic notifier foothold through `zigux/bindings/notifier_abi.zig`, the dedicated exported C header `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`

- `PHASE13_ROADMAP_ANCHOR_COUNT=4`
- `PHASE13_MANIFEST_BACKED_SURVEY_COUNT=4`
- `PHASE13_ACTIVE_ASYMMETRIC_ANCHOR_COUNT=0`
- `PHASE13_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase13-release.py`
- `PHASE13_VALIDATE_ENTRYPOINT=make -C zigux phase13-validate`
- `PHASE13_SHARED_BUILD_PRESENT=yes`
- `PHASE13_SHARED_MAKE_TARGET_PRESENT=yes`
- `PHASE13_SHARED_REPLAY_STEP_COUNT=15`
- `PHASE13_RELEASE_CLOSED=no`

The current release packet also carries one active Phase 13 boundary reminder on `master`:

- `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zig build test --build-file zigux/tests/phase13_build.zig --summary all`, and `make -C zigux phase13` are the published validator-first and shared replay path for the current packet
- the shared release packet now also keeps the dedicated `scripts/zigux/check-phase13-libfs-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-inventory-contract.py`, and `scripts/zigux/check-phase13-notifier-packet.py` guards visible, so the libfs helper packet, the stricter helper-first `devres` boundary contract, the machine-checked `devres` inventory contract, and the adjacent notifier reviewability packet stay reviewable instead of hiding only in packet-local notes or the shared build
- the shared release packet now also keeps the dedicated `scripts/zigux/check-phase13-release-replay-exact-counts.py` guard visible, so the published fifteen-step replay inventory and `PHASE13_SHARED_REPLAY_STEP_COUNT=15` marker stay reviewable instead of hiding only in `zigux/tests/phase13_build.zig`, `zigux/Makefile`, and workflow wiring
- the shared release packet now also keeps the dedicated `phase13-devres-iounmap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iounmap_reviewability.zig` so the helper-advertised `devm_iounmap()` planning surface does not look smaller than the actual shared replay on current `master`
- the shared release packet now also keeps the dedicated `phase13-devres-iomap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iomap_reviewability.zig` so the helper-advertised `devm_of_iomap()` planning surface does not look smaller than the actual shared replay on current `master`
- the shared release packet now also keeps the dedicated `phase13-devres-wrapper-reviewability-tests` gate visible through `zigux/tests/phase13_devres_wrapper_reviewability.zig` so the direct plain, uncached, write-combined, and non-posted managed `devres` ioremap wrapper family does not look smaller than the actual shared replay on current `master`
- the shared release packet now also keeps the dedicated `phase13-landlock-ruleset-reviewability-tests` gate visible through `zigux/tests/phase13_landlock_ruleset_reviewability.zig` so the helper-advertised Landlock ruleset reviewability surface does not look smaller than the actual shared replay on current `master`
- the shared release packet now also keeps the dedicated `phase13-landlock-ruleset-fops-sync-tests` gate visible through `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` so the ruleset-fd creation and explicit fops planning surface does not look smaller than the actual shared replay on current `master`
- the earlier `expected statement, found 'EOF'` note for `zigux/tests/phase13_landlock_ruleset.zig` is now historical: the current checked-in ruleset test file is syntactically complete, its dedicated ruleset helper replay still passes against `security/landlock/ruleset.zig`, and the broader shared replay has already been rerun successfully on `master`
- the remaining live ruleset blocker is the same one already recorded by the manifest-backed survey packet: `rb_replace_node()`, live object ownership transfer, hierarchy lifetime, and workqueue-backed teardown are still outside the current helper-only lane

The current manifest lane ownership carried by the release packet is:

- `fs/libfs.c` through `zigux/tests/phase13_libfs_manifest.json` lane `P13-L04`
- `lib/devres.c` through `zigux/tests/phase13_devres_manifest.json` lane `P13-L10`
- `security/landlock/ruleset.c` through `zigux/tests/phase13_landlock_ruleset_manifest.json` lane `P13-L12`
- `security/landlock/syscalls.c` through `zigux/tests/phase13_landlock_syscalls_manifest.json` lane `P13-L16`
- adjacent notifier-list reviewability evidence through `zigux/tests/phase13_notifier_list_manifest.json` lane `P13-L19`

Shared helper sequencing on top of those manifest-owner keys is now:

- `fs/libfs.c`: keep `P13-L01` narrowed to libfs survey-local or traceability-local drift now that `generic_check_addressable()` is already landed, and keep `P13-L03` verification-only unless a real packet-alignment failure or focused libfs replay regression appears
- `lib/devres.c`: keep helper expansion parked behind `P13-L06` until a concrete exported-helper gap appears, and keep `P13-L07` verification-only unless a focused devres replay fails or a helper-local regression surfaces
- `security/landlock/ruleset.c`: keep the remaining helper-only boundary work, if any, under `P13-L12` and do not reopen it from shared release notes unless the manifest-backed packet or shared replay drifts
- `security/landlock/syscalls.c`: keep `P13-L16` narrowed to packet drift or tiny validation-only cleanup and do not widen it from the shared release packet into new syscall helper scope
- shared release-discipline or docs-root follow-up should stay note-local and should not consume helper-local work already assigned to those narrower same-family lanes
- current note-local devres follow-up should only reopen if the already-landed scatterlist bookkeeping slice gets promoted into the manifest-backed packet or shared replay, or if another shared release-facing drift appears around that same helper-first boundary

The current shared replay inventory is:

- `phase13-libfs-tests`
- `phase13-devres-tests`
- `phase13-devres-dma-coherent-tests`
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

The adjacent notifier-list reviewability packet remains useful release evidence, but it is not counted as a fifth roadmap anchor:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/notifier_chain_view.zig`

## Evidence set

The current bounded release-evidence set is:

- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/check-phase13-libfs-packet.py`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-devres-inventory-contract.py`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `scripts/zigux/check-phase13-release-replay-exact-counts.py`
- `scripts/zigux/README.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_iounmap_reviewability.zig`
- `zigux/tests/phase13_devres_iomap_reviewability.zig`
- `zigux/tests/phase13_devres_wrapper_reviewability.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_reviewability.zig`
- `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/notifier_chain_view.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_notifier_list_manifest.json`

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
- live DMA-backed helpers, live scatterlist ownership, or detach-time scatter-gather cleanup beyond the current blocked boundary markers
- live Landlock enforcement, live tree-state ownership transfer, or broader syscall-enforcement parity
- notifier registration, callback execution, SRCU, blocking-notifier semantics, or a fifth roadmap anchor beyond the current read-only generic notifier foothold, dedicated exported C header, and adjacent reviewability packet

## Next bounded step

If this Phase 13 release-discipline lane reopens, keep the shared note aligned with the already-green shared replay, treat the manifest lane keys as packet-owner identifiers rather than the only live sequencing cues, let the narrower helper-family lanes consume their own next steps first, and only return here for another note-local or validator-local anti-overlap correction instead of reopening helper-local libfs, devres, or Landlock work from the shared release packet.
