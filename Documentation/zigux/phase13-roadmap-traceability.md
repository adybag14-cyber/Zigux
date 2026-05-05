# Phase 13 Roadmap Traceability

This note keeps the live Phase 13 helper packet tied back to the roadmap and the current shipped release surface on `master`.

## Roadmap anchor

Phase 13 stays in the shared subsystem-helper tranche.

The active shipped anchors on current `master` are:

- `fs/libfs.c` through `fs/libfs.zig`
- `lib/devres.c` through `lib/devres.zig`
- `security/landlock/ruleset.c` through `security/landlock/ruleset.zig`
- `security/landlock/syscalls.c` through `security/landlock/syscalls.zig`

The shared replay packet for those anchors is now the seven-test route wired by `zigux/tests/phase13_build.zig` and invoked through `make -C zigux phase13`.

## Libfs lane traceability

The Phase 13 `libfs` lane remains a helper-first review packet anchored to `fs/libfs.c`.

Current `master` keeps that anchor reviewable through:

- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`

That packet is truthful to the roadmap because it exposes only reviewable helper planning and explicit next-step posture. It currently covers the landed statfs, lookup, buffer-copy, seek-policy, directory-emit, and transaction acquire or publish helpers, while leaving the next bounded libfs follow-up on the tiny `simple_transaction_release()` lifetime planner before any live file lifecycle, cursor dentry ownership, inode state, or pseudo-filesystem mounting is claimed.

## Devres lane traceability

The Phase 13 `devres` lane remains a helper-first safety packet anchored to `lib/devres.c`.

Current `master` keeps that anchor reviewable through:

- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `scripts/zigux/check-phase13-devres-packet.py`

That packet is truthful to the roadmap because it exposes only reviewable helper planning and explicit blocker posture. It does not overclaim live MMIO mappings, live device-tree walking, DMA-backed helpers, scatterlist ownership, or live arch memtype mutation.

## Adjacent release evidence

The broader shipped Phase 13 release surface also includes adjacent evidence that stays outside the shared replay count:

- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/notifier_chain_view.zig`

These files keep the shipped release surface reviewable, but they do not change the fact that the active shared replay remains the seven-test helper packet.

## Current decision

The honest current roadmap read is:

- Phase 13 is active, not closed
- the shared replay packet is real and build-backed
- `libfs` remains bounded to helper-first filesystem planning
- `devres` remains bounded to helper-first MMIO-adjacent planning
- release-facing docs must keep the shared replay count and the adjacent-evidence split exact so contributors do not mistake missing docs or implied replay expansion for product progress
