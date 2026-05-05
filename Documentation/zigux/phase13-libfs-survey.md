# Phase 13 libfs Survey

This document records the bounded Phase 13 survey and reviewability lane around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-starter`
- scope: the landed `fs/libfs.zig` helper starter, its dedicated Phase 13 test, the shared Phase 13 build wiring, and the lane notes that compare the current helper-surface footing against the roadmap
- product boundary:
  - `fs/libfs.zig`
  - `zigux/tests/phase13_libfs.zig`
  - `zigux/tests/phase13_libfs_reviewability.zig`
  - `zigux/tests/phase13_libfs_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-libfs-slice.md`
  - `Documentation/zigux/phase13-libfs-survey.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `fs/libfs.c` as a shared subsystem-helper anchor.

That matters because `fs/libfs.c` is still a large helper surface that spans simple metadata helpers, dcache cursor traversal, offset bookkeeping, recursive removal, pseudo-filesystem setup, inode and rename helpers, simple buffer I/O, attribute plumbing, and several shared utility routines.

The live Zigux tree is no longer survey-only here. It already carries a small `fs/libfs.zig` starter, so the highest-value verification work in this lane is to keep that real helper footing reviewable and compile-checkable instead of continuing to describe it with older wrapper scaffolding.

## Survey findings

- `fs/libfs.c` remains broad enough to cross several VFS boundaries at once: dentries, directory iteration, inode bookkeeping, pseudo-filesystem mounting, and generic buffer-copy helpers.
- the live repo now has a landed `fs/libfs.zig` starter plus `zigux/tests/phase13_libfs.zig`, and `zigux/tests/phase13_build.zig` compiles that dedicated libfs helper test path.
- the current starter stays intentionally narrow around `simple_statfs()` defaults, the `always_delete_dentry()` policy, the branch decisions inside `simple_lookup()`, the pure buffer-copy helper trio, the early `dcache_dir_lseek()` and `offset_dir_llseek()` seek-policy surface, one tiny `dcache_readdir()`-adjacent emit planner, the pure `simple_transaction_get()` acquire planner, and the pure `simple_transaction_set()` publish planner.
- the reviewability gate and manifest tie the starter, tests, build wire, slice note, and survey note together so future runs can verify the exact Phase 13 lane state before widening helper coverage.
- directory cursor helpers such as `dcache_dir_open()` and the deeper cursor-backed `dcache_readdir()` traversal remain riskier because they depend on cursor dentries, sibling lists, lock ordering, and reschedule-aware traversal.

## Recorded gaps

The current lane state is:

- landed `phase13-libfs-helper-starter`
- landed `phase13-libfs-test-gate`
- landed `phase13-build-gate`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-slice-note`
- landed `phase13-libfs-survey-note`
- landed `phase13-libfs-offset-seek-helper`
- landed `phase13-libfs-directory-emit-helper`
- landed `phase13-libfs-transaction-buffer-helper`
- landed `phase13-libfs-transaction-publish-helper`
- ready-next `phase13-libfs-transaction-release-helper`
- blocked `phase13-libfs-dcache-cursor-helpers`
- blocked `phase13-libfs-inode-and-pseudofs-lifecycle`

This keeps the lane explicit without overstating progress: Zigux now has a real `fs/libfs.zig` helper foothold plus a reviewability checkpoint, but it still does not claim live dcache parity, pseudo-filesystem mounting, inode lifecycle work, rename-state behavior, or cursor-backed directory traversal.

## Non-goals

This slice does not claim:

- live `d_add()` or dcache mutation side effects
- dcache cursor or directory-iteration helper surfaces
- pseudo-filesystem mount or superblock helpers
- rename, unlink, rmdir, or setattr lifecycle helpers
- file-attribute, writeback, or fsync helper-surface parity
- VFS object ownership, locking, or mount-state behavior

## Gates

1. run the dedicated Phase 13 build
- `zig build test --build-file zigux/tests/phase13_build.zig`

2. run the convenience target
- `make -C zigux phase13`

## Next bounded step

Stay in the Phase 13 libfs lane and add one tiny `fs/libfs.zig` transaction release helper next, limited to reviewable `simple_transaction_release()` private-data lifetime and release bookkeeping before any live readback, cursor dentry, inode, or pseudo-filesystem work.
