# Phase 13 Roadmap Traceability

This note keeps the live Phase 13 helper packet tied back to the roadmap and the current shipped release surface on `master`.

## Roadmap anchor

Phase 13 stays in the shared subsystem-helper tranche.

The active shipped anchors on current `master` are:

  * `fs/libfs.c` through `fs/libfs.zig`
  * `lib/devres.c` through `lib/devres.zig`
  * `security/landlock/ruleset.c` through `security/landlock/ruleset.zig`
  * `security/landlock/syscalls.c` through `security/landlock/syscalls.zig`

The shared replay packet for those anchors is now the seven-test route wired by `zigux/tests/phase13_build.zig` and invoked through `make -C zigux phase13`.

That live replay route currently names:

  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
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
  * `zigux/tests/phase13_libfs_reviewability.zig`

That packet is truthful to the roadmap because it exposes only reviewable helper planning and explicit next-step posture. It currently covers the landed statfs, lookup, buffer-copy, seek-policy, directory-emit, and transaction acquire, publish, and release helpers, while leaving the next bounded libfs follow-up on the blocked `dcache_dir_open()` and deeper `dcache_readdir()` cursor-precondition packet before any live file lifecycle, cursor dentry ownership, inode state, or pseudo-filesystem mounting is claimed.

## Devres lane traceability

The Phase 13 `devres` lane remains a helper-first safety packet anchored to `lib/devres.c`.

Current `master` keeps that anchor reviewable through:

  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `zigux/tests/phase13_devres_manifest.json`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `scripts/zigux/check-phase13-devres-packet.py`

Inside that packet, the active shared replay now keeps `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_dma_coherent.zig` inside the seven-test helper route. The shipped `scripts/zigux/check-phase13-devres-packet.py` remains adjacent `devres` release evidence on current `master`, so it stays reviewable without inflating the shared replay count beyond the build-backed route.

That packet is truthful to the roadmap because it exposes only reviewable helper planning and explicit blocker posture. It does not overclaim live MMIO mappings, live device-tree walking, DMA-backed helpers, scatterlist ownership, or live arch memtype mutation.

## Landlock syscall lane traceability

The Phase 13 `landlock syscalls` lane remains a helper-first security packet anchored to `security/landlock/syscalls.c`.

Current `master` keeps that anchor reviewable through:

  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`

That packet is truthful to the roadmap because it records only bounded helper planning and the next explicit release-side follow-up. The shipped helper surface now keeps ABI shape reporting, `landlock_create_ruleset()` query and mask validation, `landlock_restrict_self()` logging translation including the special `ruleset_fd == -1` mute-subdomains-only case, `landlock_add_rule()` dispatch, `get_ruleset_from_fd()` mode checks, `get_path_from_fd()` path-source validation, the focused `zigux/tests/phase13_landlock_syscalls_reviewability.zig` direct-evidence shard, and the current `add_rule_path_beneath()` handoff reviewable without implying anonymous inode creation, live file-operations wiring, path-backed rule import, credential mutation, or live syscall enforcement.

The next honest same-lane step is still the tiny `fop_ruleset_release()` planner recorded in the survey manifest so the retained ruleset in `private_data`, the matching `landlock_put_ruleset()` release, and the zero return contract become explicit before any broader file-operations or FD-ownership claims are attempted.

## Adjacent release evidence

The broader shipped Phase 13 release surface also includes adjacent evidence that stays outside the shared replay count:

  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
  * `zigux/tests/phase13_notifier_list_manifest.json`
  * `zigux/tests/phase13_notifier_list_reviewability.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `include/zigux/notifier_abi.h`
  * `zigux/helpers/notifier_chain_view.zig`

These files keep the shipped release surface reviewable, but they do not change the fact that the active shared replay remains the seven-test helper packet.

## Current decision

The honest current roadmap read is:

  * Phase 13 is active, not closed
  * the shared replay packet is real and build-backed
  * `libfs` remains bounded to helper-first filesystem planning
  * `devres` remains bounded to helper-first MMIO-adjacent planning
  * `landlock syscalls` remains bounded to helper-first syscall planning with the release-side handoff still explicitly queued next
  * release-facing docs must keep the shared replay count and the adjacent-evidence split exact so contributors do not mistake missing docs or implied replay expansion for product progress
