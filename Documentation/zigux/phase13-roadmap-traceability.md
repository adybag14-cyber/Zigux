# Phase 13 Roadmap Traceability

This note keeps the live Phase 13 helper packet tied back to the roadmap and the current shipped release surface on `master`.

## Roadmap anchor

Phase 13 stays in the shared subsystem-helper tranche.

The active shipped anchors on current `master` are:

  * `fs/libfs.c` through `fs/libfs.zig`
  * `lib/devres.c` through `lib/devres.zig`
  * `security/landlock/ruleset.c` through `security/landlock/ruleset.zig`
  * `security/landlock/syscalls.c` through `security/landlock/syscalls.zig`

The shared replay packet for those anchors is now the eight-test route wired by `zigux/tests/phase13_build.zig` and invoked through `make -C zigux phase13`.

That live replay route currently names:

  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_boundary_evidence.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_libfs_reviewability.zig`

## Libfs lane traceability

The Phase 13 `libfs` lane remains a helper-first review packet anchored to `fs/libfs.c`.

Current `master` keeps that anchor reviewable through:

  * `Documentation/zigux/phase13-libfs-slice.md`
  * `Documentation/zigux/phase13-libfs-survey.md`
  * `zigux/tests/phase13_libfs_manifest.json`
  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_libfs_addressability.zig`
  * `zigux/tests/phase13_libfs_reviewability.zig`

Inside that packet, the active shared replay keeps `zigux/tests/phase13_libfs.zig` and `zigux/tests/phase13_libfs_reviewability.zig` inside the same eight-test helper route while `zigux/tests/phase13_libfs_addressability.zig` stays shipped focused direct helper evidence rather than a ninth shared replay step.

That packet is truthful to the roadmap because it exposes only reviewable helper planning and explicit next-step posture. It currently covers the landed statfs, lookup, buffer-copy, seek-policy, directory-emit, `dcache_dir_open()` setup, `dcache_dir_close()` cursor-release, cursor-reposition bookkeeping, transaction acquire, publish, and release helpers, the `generic_check_addressable()` planner around shift overflow, zero-block passthrough, minimum block size, and explicit sector or page-index caps, the bounded `simple_open()` private-data handoff, and the exported `simple_dir_operations` wrapper without implying live file lifecycle, cursor dentry ownership, inode state, file-operations registration, or pseudo-filesystem mounting. Keep this packet parked unless a future same-lane step can stay equally small; the deeper `dcache_readdir()` cursor-resume packet still needs sibling-list traversal, reschedule-aware cursor movement, and lock-ordering boundaries called out before the helper-first boundary can move.

## Devres lane traceability

The Phase 13 `devres` lane remains a helper-first safety packet anchored to `lib/devres.c`.

Current `master` keeps that anchor reviewable through:

  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `zigux/tests/phase13_devres_manifest.json`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_boundary_evidence.zig`
  * `scripts/zigux/check-phase13-devres-packet.py`

Inside that packet, the active shared replay now keeps `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_boundary_evidence.zig` inside the eight-test helper route. The live `make -C zigux phase13-validate` route also reruns the shipped `scripts/zigux/check-phase13-devres-packet.py` beside the shared release validator, so the `devres` boundary note stays adjacent release evidence on current `master` without inflating the shared replay count beyond the build-backed route.

That packet is truthful to the roadmap because it exposes only reviewable helper planning and explicit blocker posture. It does not overclaim live MMIO mappings, live device-tree walking, DMA-backed helpers, scatterlist ownership, or live arch memtype mutation.

There is still no shipped `zigux/tests/phase13_devres_scatterlist.zig` direct-evidence shard on current `master`, so scatterlist remains blocker wording only rather than a replay surface.

## Landlock ruleset lane traceability

The Phase 13 `landlock ruleset` lane remains a helper-first security packet anchored to `security/landlock/ruleset.c`.

Current `master` keeps that anchor reviewable through:

  * `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  * `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `scripts/zigux/check-phase13-landlock-ruleset-packet.py`

Inside that packet, the active shared replay now keeps `zigux/tests/phase13_landlock_ruleset.zig` inside the same eight-test helper route while the dedicated packet checker stays adjacent lane evidence rather than an extra shared replay step. The live `make -C zigux phase13-validate` route now reruns `scripts/zigux/check-phase13-landlock-ruleset-packet.py` beside the shared release validator and the `devres` packet checker, so the roadmap note needs that checker named explicitly to keep the shipped helper boundary reviewable without overstating the replay count.

The shipped helper-owned boundary note `Documentation/zigux/phase13-landlock-ruleset-ownership.md` stays paired with that anchor too. It records why the current ruleset foothold is still helper-local planning around ownership and cleanup boundaries, and it keeps those owner cues explicit without turning the ownership note into a ninth shared replay step.

That packet is truthful to the roadmap because it keeps the current ruleset foothold bounded to in-memory helper planning around `landlock_create_ruleset()`, access-mask unioning, per-layer mask initialization, `landlock_unmask_layers()` bit clearing, `insert_rule()` merge and search planning, no-match tree-link planning, and matched-rule replacement planning. It does not overclaim live rb-tree mutation, object references, hierarchy ownership, deferred frees, or live Landlock policy enforcement.

The next honest same-lane step stays blocked where the live-tree state begins: old-rule cleanup after `rb_replace_node()`, object ownership, and hierarchy lifetime still need a narrower evidence path before this traceability note can claim more than the current helper-only packet.

## Landlock syscall lane traceability

The Phase 13 `landlock syscalls` lane remains a helper-first security packet anchored to `security/landlock/syscalls.c`.

Current `master` keeps that anchor reviewable through:

  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`

That packet is truthful to the roadmap because it records only bounded helper planning and the current shipped syscall-helper surface. The shipped helper surface now keeps ABI shape reporting, `landlock_create_ruleset()` query and mask validation, `landlock_restrict_self()` logging translation including the special `ruleset_fd == -1` mute-subdomains-only case, `landlock_add_rule()` dispatch, `get_ruleset_from_fd()` mode checks, `get_path_from_fd()` path-source validation, the focused `zigux/tests/phase13_landlock_syscalls_reviewability.zig` direct-evidence shard, the current `add_rule_path_beneath()` handoff reviewable, and the bounded `fop_ruleset_release()` release-side handoff reviewable without implying anonymous inode creation, live file-operations wiring, path-backed rule import, credential mutation, or live syscall enforcement.

The shipped helper-owned boundary note `Documentation/zigux/phase13-landlock-syscalls-governance.md` stays paired with that anchor too. It keeps the current FD, path, and release-side governance cues explicit for contributors and reviewers without turning that helper-owned policy note into a ninth shared replay step.

Together, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` are the current syscall-owned truthfulness trio for this helper packet. Keeping that trio explicit in the roadmap note matches the newer contributor and tests-root guidance on `master` without borrowing the unrelated ruleset checker as shorthand for syscall evidence.

Keep this packet parked unless a future same-lane step can add another equally bounded planner without widening into live file-operations wiring, FD ownership, credential work, or domain state.

## Adjacent release evidence

The broader shipped Phase 13 release surface also includes adjacent evidence that stays outside the shared replay count:

  * `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
  * `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
  * `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  * `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  * `zigux/tests/phase13_libfs_addressability.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * `scripts/zigux/validate-phase13-release.py`
  * `scripts/zigux/check-phase13-devres-packet.py`
  * `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
  * `scripts/zigux/check-phase13-notifier-packet.py`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
  * `zigux/tests/phase13_notifier_list_manifest.json`
  * `zigux/tests/phase13_notifier_list_reviewability.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `zigux/helpers/list_view.zig`
  * `zigux/helpers/hlist_view.zig`
  * `include/zigux/abi.h`
  * `include/zigux/notifier_abi.h`
  * `zigux/helpers/notifier_chain_view.zig`
  * `zigux/Makefile`

The direct `zigux/tests/phase13_libfs_addressability.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` shards stay in that adjacent release-evidence set for the same reason already recorded in their helper-lane sections and the release-notes packet: they are shipped focused direct evidence on current `master`, but they do not expand the shared replay beyond the eight build-backed tests.

`Documentation/zigux/phase13-shared-helper-lane-sequencing.md` stays in that same adjacent evidence set as the owner-map note for the active `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls` helper families. It keeps the shared validator-first route and adjacent notifier evidence from collapsing into one ownerless packet, but it does not add a ninth replay step or change which helper lane owns which backlog.

The contributor workflow guide, contributor-surface sync note, compact tests-root companion, and shared review checklist stay in that same adjacent evidence set too. They keep the broader contributor-facing Phase 13 packet honest beside the validator-first route, but they do not promote those reminder surfaces into extra replay steps or move ownership away from the helper-family lanes.

The shipped validator-first route also stays in that adjacent evidence set: `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, and `zigux/Makefile` keep the four-anchor traceability packet, the dedicated `devres` and `landlock/ruleset` checker proofs, and the adjacent notifier evidence fail-closed on current `master` without promoting those validation surfaces into a ninth shared replay step.

The shipped `scripts/zigux/check-phase13-notifier-packet.py` route stays in that same adjacent evidence set: it fail-closes the notifier survey, manifest, reviewability replay, shipped `list_view` plus `hlist_view` helper footholds, the exported list and hlist ABI carrier structs in `include/zigux/abi.h`, the notifier ABI header, and the notifier-chain helper footholds without promoting that adjacent packet into a ninth shared replay step.

The helper-owned Landlock boundary notes stay in that adjacent release packet because they document the shipped ownership and governance blockers that still prevent a closure claim without inflating the eight-test shared replay count.

These files keep the shipped release surface reviewable, but they do not change the fact that the active shared replay remains the eight-test helper packet.

## Current decision

The honest current roadmap read is:

  * Phase 13 is active, not closed
  * the shared replay packet is real and build-backed
  * `libfs` remains bounded to helper-first filesystem planning with one focused addressability shard still outside the shared replay count
  * `devres` remains bounded to helper-first MMIO-adjacent planning
  * `landlock ruleset` remains bounded to helper-first ruleset planning with live-tree state still explicitly blocked
  * `landlock syscalls` remains bounded to helper-first syscall planning with the release-side handoff now explicitly shipped and the packet otherwise parked
  * `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` remains the owner-map companion for the active helper tranche rather than a replay-count expansion
  * the current shipped Phase 13 packet still has no dedicated `Documentation/zigux/phase13-closure.md`, so `Documentation/zigux/phase13-release-notes-survey.md` plus this traceability note carry the active tranche posture for the existing work
  * release-facing docs must keep the shared replay count and the adjacent-evidence split exact so contributors do not mistake missing docs or implied replay expansion for product progress
