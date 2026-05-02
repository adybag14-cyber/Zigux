# Phase 13 libfs Survey

This document records the bounded Phase 13 survey and reviewability lane around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-reviewability`
- `PHASE13_SURVEYED_COMMIT=949994db4046ec70abf044d1b2ea874fde9bc4a6`
- scope: the landed `fs/libfs.zig` helper slice, its dedicated Phase 13 tests, the shared Phase 13 build wiring, and the lane notes that compare the current wrapper footing against the roadmap

## Survey findings

- `fs/libfs.c` remains broad enough to cross several VFS boundaries at once: dentries, directory iteration, inode bookkeeping, pseudo-filesystem mounting, and generic buffer-copy helpers.
- the live repo now has a landed `fs/libfs.zig` helper slice plus `zigux/tests/phase13_libfs.zig`, and both the explicit standalone `zig test` entrypoints with `libfs` module wiring plus `zigux/tests/phase13_build.zig` compile that helper and reviewability path.
- the current survey packet is pinned to inspected `master` head `949994db4046ec70abf044d1b2ea874fde9bc4a6` so future lane runs can detect note and manifest drift before widening helper coverage.
- the current helper slice stays intentionally narrow around `simple_statfs()` defaults, the `always_delete_dentry()` policy, the branch decisions inside `simple_lookup()`, the pure buffer-copy helper trio, the early `dcache_dir_lseek()` and `offset_dir_llseek()` seek-policy surface, one tiny `offset_readdir()` control-flow planner, one tiny `dcache_readdir()`-adjacent emit planner, one bounded `dcache_dir_open()` / `dcache_readdir()` cursor-precondition planner, one bounded `dcache_dir_close()` release planner, a bounded `simple_transaction_get()` / `simple_transaction_set()` staging-buffer planner, a pure `simple_transaction_read()` / `simple_transaction_release()` follow-up, and a pure `simple_open()` private-data handoff planner.

## Recorded gaps

The current lane state is:

- landed `phase13-libfs-helper-starter`
- landed `phase13-libfs-test-gate`
- landed `phase13-build-gate`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-slice-note`
- landed `phase13-libfs-survey-note`
- landed `phase13-libfs-offset-seek-helper`
- landed `phase13-libfs-offset-readdir-helper`
- landed `phase13-libfs-directory-emit-helper`
- landed `phase13-libfs-transaction-buffer-helper`
- landed `phase13-libfs-transaction-read-release-followup`
- landed `phase13-libfs-dcache-cursor-preconditions`
- landed `phase13-libfs-dcache-cursor-reposition-bookkeeping`
- landed `phase13-libfs-dcache-dir-close-release-bookkeeping`
- landed `phase13-libfs-simple-open-private-data-planning`
- blocked `phase13-libfs-dcache-cursor-helpers`
- blocked `phase13-libfs-inode-and-pseudofs-lifecycle`

This keeps the lane explicit without overstating progress: Zigux now has a real `fs/libfs.zig` helper slice plus a reviewability checkpoint, a tiny `offset_readdir()` control-flow planner, a bounded cursor-precondition planner, a bounded post-scan cursor-reposition planner, a bounded close-path release planner, a bounded transaction-buffer planner, a pure transaction read/release follow-up, and a pure simple-open private-data planner, but it still does not claim live dcache parity, mutable file-private transaction state, pseudo-filesystem mounting, inode lifecycle work, rename-state behavior, or cursor-backed directory traversal.
