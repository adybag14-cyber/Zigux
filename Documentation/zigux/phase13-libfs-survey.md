# Phase 13 libfs Survey

This document records the bounded Phase 13 survey and reviewability lane around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-reviewability-packet`
- scope: the landed `fs/libfs.zig` helper packet, its dedicated Phase 13 tests, the shared Phase 13 build wiring, the focused `generic_check_addressable()` helper proof, and the lane notes that compare the current helper-surface footing against the roadmap
- product boundary:
  - `fs/libfs.zig`
  - `zigux/tests/phase13_libfs.zig`
  - `zigux/tests/phase13_libfs_addressability.zig`
  - `zigux/tests/phase13_libfs_reviewability.zig`
  - `zigux/tests/phase13_libfs_manifest.json`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-libfs-slice.md`
  - `Documentation/zigux/phase13-libfs-survey.md`
  - `Documentation/zigux/phase13-roadmap-traceability.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `fs/libfs.c` as a shared subsystem-helper anchor.

That matters because `fs/libfs.c` is still a large helper surface that spans simple metadata helpers, dcache cursor traversal, offset bookkeeping, recursive removal, pseudo-filesystem setup, inode and rename helpers, simple buffer I/O, attribute plumbing, and several shared utility routines.

The live Zigux tree is no longer survey-only here. It already carries a meaningful `fs/libfs.zig` helper packet, so the highest-value verification work in this lane is to keep that real helper footing reviewable and compile-checkable instead of continuing to describe it with older starter scaffolding.

## Survey findings

- `fs/libfs.c` remains broad enough to cross several VFS boundaries at once: dentries, directory iteration, inode bookkeeping, pseudo-filesystem mounting, and generic buffer-copy helpers.
- the live repo now has a landed `fs/libfs.zig` helper packet plus `zigux/tests/phase13_libfs.zig`, and `zigux/tests/phase13_build.zig` compiles that dedicated libfs helper test path.
- the current helper packet stays intentionally bounded around `simple_statfs()` defaults, the `always_delete_dentry()` policy, the branch decisions inside `simple_lookup()`, the pure buffer-copy helper trio, the early `dcache_dir_lseek()` and `offset_dir_llseek()` seek-policy surface, one tiny `dcache_readdir()`-adjacent emit planner, the pure `dcache_dir_open()` cursor-setup planner, the pure `dcache_dir_close()` cursor-release planner, the pure post-scan cursor-reposition planner around hashed-cursor detach plus before-target versus behind-target reinsertion, the pure `simple_transaction_get()` acquire planner, the pure `simple_transaction_set()` publish planner, the pure `simple_transaction_release()` lifetime planner, the pure `generic_check_addressable()` planner around shift overflow, zero-block passthrough, minimum block size, and explicit sector or page-index caps, the pure `simple_open()` planner around the `inode->i_private` to `file->private_data` handoff, and the exported `simple_dir_operations` wrapper plan that keeps the `dcache_dir_open()`, `dcache_dir_close()`, `dcache_dir_lseek()`, `generic_read_dir()`, `dcache_readdir()`, and `noop_fsync()` handler bundle explicit.
- the focused `zigux/tests/phase13_libfs_addressability.zig` file keeps the `generic_check_addressable()` planner directly exercised without widening the broader Phase 13 build route in this run.
- the reviewability gate and manifest now tie the current helper packet, tests, focused addressability proof, build wire, slice note, survey note, and roadmap traceability note together so future runs can verify the exact Phase 13 lane state before widening helper coverage.
- the focused `zigux/tests/phase13_libfs_addressability.zig` shard remains dedicated helper-local evidence rather than a ninth shared replay step, so future packet updates should keep naming it explicitly without inflating the shared eight-test `phase13_build.zig` route.
- directory cursor helpers such as the now-landed `dcache_dir_open()`, `dcache_dir_close()`, and cursor-reposition planner still stay below the deeper cursor-backed `dcache_readdir()` traversal, which remains riskier because it depends on cursor dentries, sibling lists, lock ordering, and reschedule-aware traversal.

## Recorded gaps

The current lane state is:

- landed `phase13-build-gate`
- landed `phase13-make-target`
- landed `phase13-libfs-starter`
- landed `phase13-libfs-tests`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-slice-note`
- landed `phase13-libfs-survey-note`
- landed `phase13-libfs-offset-seek-helper`
- landed `phase13-libfs-directory-emit-helper`
- landed `phase13-libfs-dcache-dir-open-helper`
- landed `phase13-libfs-dcache-dir-close-helper`
- landed `phase13-libfs-cursor-reposition-helper`
- landed `phase13-libfs-transaction-buffer-helper`
- landed `phase13-libfs-transaction-publish-helper`
- landed `phase13-libfs-transaction-release-helper`
- landed `phase13-libfs-addressability-helper`
- landed `phase13-libfs-simple-open-helper`
- landed `phase13-libfs-simple-dir-operations-wrapper`
- blocked `phase13-libfs-dcache-cursor-helpers`

This keeps the lane explicit without overstating progress: Zigux now has a real `fs/libfs.zig` helper packet plus a reviewability checkpoint, one focused capacity-checking helper, the bounded `dcache_dir_open()` and `dcache_dir_close()` cursor pair, the bounded cursor-reposition planner, the bounded `simple_open()` private-data handoff, and the exported `simple_dir_operations` wrapper plan, but it still does not claim live dcache parity, pseudo-filesystem mounting, inode lifecycle work, rename-state behavior, or cursor-backed directory traversal.

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

3. run the focused addressability proof when the helper changes outside the shared replay packet
- `zig test --dep libfs -Mroot=zigux/tests/phase13_libfs_addressability.zig -Mlibfs=fs/libfs.zig`

## Next bounded step

Keep this lane parked unless a future pass can identify another equally small helper-first step that stays below live cursor traversal. The deeper `dcache_readdir()` cursor resume and reschedule preconditions should remain blocked until they can name sibling-list resume context, cursor repositioning under reschedule pressure, and lock-ordering boundaries without widening past the now-landed open or close cursor pair plus reposition helper into live cursor dentries, inode state, or pseudo-filesystem work.
