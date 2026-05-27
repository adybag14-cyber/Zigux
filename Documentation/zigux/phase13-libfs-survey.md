# Phase 13 libfs Survey

This document records the bounded Phase 13 survey lane around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-filesystem-boundary-survey`
- reviewed against live `master` `master-readback-2026-05-27`
- scope: the shipped helper-first libfs packet plus the landed dcache cursor precondition side packet, keeping helper-local planner evidence explicit while the older shared Phase 13 build route and live filesystem mutation remain out of scope
- product boundary:
  - `fs/libfs.zig`
  - `fs/libfs_dcache_cursor.zig`
  - `zigux/tests/phase13_libfs.zig`
  - `zigux/tests/phase13_libfs_reviewability.zig`
  - `zigux/tests/phase13_libfs_dcache_cursor.zig`
  - `zigux/tests/phase13_libfs_manifest.json`
  - `zigux/tests/phase13_libfs_dcache_cursor_manifest.json`
  - `Documentation/zigux/phase13-libfs-survey.md`
  - `Documentation/zigux/phase13-libfs-slice.md`
  - `Documentation/zigux/phase13-libfs-dcache-cursor-planner.md`
  - `scripts/zigux/check-phase13-libfs-packet.py`
  - `scripts/zigux/check-phase13-libfs-dcache-cursor-packet.py`

## Why this slice exists

The Phase 13 roadmap explicitly names `fs/libfs.c` as a shared subsystem-helper anchor.

That still matters because `fs/libfs.c` contains small VFS-adjacent helpers that can easily be overstated as live filesystem behavior. Current `master` already ships a bounded helper-first libfs packet, and this run closes the next helper-local step by making `dcache_dir_open()` and `dcache_readdir()` cursor preconditions reviewable without implying live cursor dentries or sibling traversal.

## Survey findings

- current `master` exposes `fs/libfs.zig`, `fs/libfs_dcache_cursor.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_dcache_cursor.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_libfs_dcache_cursor_manifest.json`, `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-libfs-dcache-cursor-planner.md`, `scripts/zigux/check-phase13-libfs-packet.py`, and `scripts/zigux/check-phase13-libfs-dcache-cursor-packet.py`
- the current helper packet already lands bounded lookup shaping, `simple_transaction_get()` / `simple_transaction_set()` / `simple_transaction_release()` planning, `generic_check_addressable()` planning, `simple_offset_add()` / `simple_offset_remove()` planning, `offset_readdir()` planning, and offset-based rename plus rename-exchange planning without claiming live dcache or inode ownership
- the new side packet lands `dcache_dir_open()` and `dcache_readdir()` cursor preconditions through a helper-first planner, a focused replay, a dedicated manifest, and a packet checker without claiming sibling traversal, lock ordering, or live rename relocation
- the older shared `zigux/tests/phase13_build.zig` replay route is still absent on current `master`, so the shipped packet remains focused rather than shared-build-backed

## Recorded gaps

The current lane state is:

- helper-local governance for this family remains tracked under `P13-L01`, while the separate verification-only replay lane remains parked under `P13-L03`
- landed `phase13-libfs-helper-starter`
- landed `phase13-libfs-offset-add-planner`
- landed `phase13-libfs-offset-remove-planner`
- landed `phase13-libfs-offset-rename-planner`
- landed `phase13-libfs-transaction-acquire-helper`
- landed `phase13-libfs-transaction-release-helper`
- landed `phase13-libfs-transaction-publish-helper`
- landed `phase13-libfs-addressability-helper`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-survey-note`
- landed `phase13-libfs-dcache-cursor-precondition-planner`
- blocked `phase13-build-gate`
- blocked `phase13-libfs-live-dcache-mutation`
- blocked `phase13-libfs-live-inode-state`
- blocked `phase13-libfs-live-cursor-traversal`

This keeps the lane explicit without understating shipped progress: current `master` exposes the direct helper, focused replay, reviewability gate, packet checker, and the new cursor-precondition side packet, while the shared Phase 13 build route plus live filesystem mutation remain out of scope.

## Non-goals

This slice does not claim:

- live dcache entry insertion or removal side effects
- live inode lifetime or inode locking behavior
- page-cache-backed filesystem state
- live directory-map mutation, maple-tree mutation, or rename application
- broader superblock or filesystem registration behavior
- live cursor sibling traversal or private cursor relocation
- shared release-surface ownership for unrelated Phase 13 helpers

## Next bounded step

If the libfs family reopens, prefer one helper-local follow-through: add the smallest `dcache_dir_close()` cursor release planner that can be expressed without claiming live cursor unlinking, sibling mutation, or lock ordering. Keep verification-only replay work on `P13-L03`.
