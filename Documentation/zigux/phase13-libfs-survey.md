# Phase 13 libfs Survey

This document records the bounded Phase 13 survey and reviewability lane around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-reviewability`
- `PHASE13_SURVEYED_COMMIT=ba74bb197b16b020ec02b876efdd154663c6a146`
- scope: the landed `fs/libfs.zig` helper slice, its dedicated Phase 13 tests, the shared Phase 13 build wiring, and the lane notes that compare the current wrapper footing against the roadmap
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

The live Zigux tree is no longer survey-only here. It already carries a small `fs/libfs.zig` helper slice, so the highest-value verification work in this lane is to keep that real helper footing reviewable and compile-checkable instead of continuing to describe a missing wrapper.

## Survey findings

- `fs/libfs.c` remains broad enough to cross several VFS boundaries at once: dentries, directory iteration, inode bookkeeping, pseudo-filesystem mounting, and generic buffer-copy helpers.
- the live repo now has a landed `fs/libfs.zig` helper slice plus `zigux/tests/phase13_libfs.zig`, and both the explicit standalone `zig test` entrypoints with `libfs` module wiring plus `zigux/tests/phase13_build.zig` compile that helper and reviewability path.
- the current survey packet is pinned to inspected `master` head `ba74bb197b16b020ec02b876efdd154663c6a146` so future lane runs can detect note and manifest drift before widening helper coverage.
- the current helper slice stays intentionally narrow around `simple_statfs()` defaults, the `always_delete_dentry()` policy, the branch decisions inside `simple_lookup()`, the pure buffer-copy helper trio, the early `dcache_dir_lseek()` and `offset_dir_llseek()` seek-policy surface, one tiny `dcache_readdir()`-adjacent emit planner, one bounded `dcache_dir_open()` / `dcache_readdir()` cursor-precondition planner, one bounded `dcache_dir_close()` release planner, a bounded `simple_transaction_get()` / `simple_transaction_set()` staging-buffer planner, and a pure `simple_transaction_read()` / `simple_transaction_release()` follow-up that only models private-data presence checks, read delegation intent, and release bookkeeping.
- the reviewability gate and manifest tie the current helper slice, tests, build wire, slice note, and survey note together so future runs can verify the exact Phase 13 lane state before widening helper coverage.
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
- landed `phase13-libfs-transaction-read-release-followup`
- landed `phase13-libfs-dcache-cursor-preconditions`
- landed `phase13-libfs-dcache-cursor-reposition-bookkeeping`
- landed `phase13-libfs-dcache-dir-close-release-bookkeeping`
- blocked `phase13-libfs-dcache-cursor-helpers`
- blocked `phase13-libfs-inode-and-pseudofs-lifecycle`

This keeps the lane explicit without overstating progress: Zigux now has a real `fs/libfs.zig` helper slice plus a reviewability checkpoint, a bounded cursor-precondition planner, a bounded post-scan cursor-reposition planner, a bounded close-path release planner, a bounded transaction-buffer planner, and a pure transaction read/release follow-up, but it still does not claim live dcache parity, mutable file-private transaction state, pseudo-filesystem mounting, inode lifecycle work, rename-state behavior, or cursor-backed directory traversal.

## Non-goals

This slice does not claim:

- live `d_add()` or dcache mutation side effects
- dcache cursor or directory-iteration wrappers
- pseudo-filesystem mount or superblock helpers
- rename, unlink, rmdir, or setattr lifecycle helpers
- file-attribute, writeback, or fsync wrapper parity
- VFS object ownership, locking, or mount-state behavior

## Gates

1. run the focused standalone libfs checks
- `zig test fs/libfs.zig`
- `zig test --dep libfs -Mroot=zigux/tests/phase13_libfs.zig -Mlibfs=fs/libfs.zig`
- `zig test --dep libfs -Mroot=zigux/tests/phase13_libfs_reviewability.zig -Mlibfs=fs/libfs.zig`

2. run the dedicated Phase 13 build
- `zig build test --build-file zigux/tests/phase13_build.zig --summary all`

3. run the convenience target
- `make -C zigux phase13`

## Latest verification snapshot

- inspected head: `ba74bb197b16b020ec02b876efdd154663c6a146`
- `zig test fs/libfs.zig`: passed (`0` embedded tests; parse and compile check only)
- `zig test --dep libfs -Mroot=zigux/tests/phase13_libfs.zig -Mlibfs=fs/libfs.zig`: passed (`22/22` tests)
- `zig test --dep libfs -Mroot=zigux/tests/phase13_libfs_reviewability.zig -Mlibfs=fs/libfs.zig`: passed (`1/1` tests)
- `zig build test --build-file zigux/tests/phase13_build.zig --summary all`: blocked on unrelated `zigux/tests/phase13_landlock_syscalls.zig` syntax corruption at line 236; the libfs, devres, Landlock ruleset, and notifier-list legs still compiled and ran inside that shared build before the separate landlock-syscalls failure stopped the tranche

## Next bounded step

Keep the Phase 13 libfs lane helper-first and leave the remaining cursor-backed helpers plus inode and pseudo-filesystem lifecycle paths blocked on live VFS state unless a future run can isolate another equally small non-live boundary.
