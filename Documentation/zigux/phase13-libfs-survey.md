# Phase 13 libfs Survey

This document records the bounded Phase 13 survey lane around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 13 build wiring, and a lane note that compares the live repo state against the roadmap for `fs/libfs.zig`
- product boundary:
  - `zigux/tests/phase13_libfs_manifest.json`
  - `zigux/tests/phase13_libfs_survey.zig`
  - `zigux/tests/phase13_build.zig`
  - `Documentation/zigux/phase13-libfs-survey.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `fs/libfs.c` as a shared subsystem-helper anchor.

That matters because the live repo currently has no `fs/libfs.zig` file at all, even though `fs/libfs.c` is a 2,314-line helper surface that spans simple metadata helpers, dcache cursor traversal, offset bookkeeping, recursive removal, pseudo-filesystem setup, inode and rename helpers, simple buffer I/O, attribute plumbing, and several shared utility routines.

The highest-value honest step in this lane is therefore to make the gap reviewable and compile-checkable before any wrapper lands, rather than pretending the file family already has a starter or widening immediately into VFS stateful behavior.

## Survey findings

- `fs/libfs.c` is present on `master` and is large enough to cross several VFS boundaries at once: dentries, directory iteration, inode bookkeeping, pseudo-filesystem mounting, and generic buffer-copy helpers.
- the live repo now has a dedicated `zigux/tests/phase13_build.zig` gate and `make -C zigux phase13` entry point, but it still has zero `fs/*.zig` files and no `fs/libfs.zig` wrapper starter.
- the lowest-risk helper-first foothold inside `libfs.c` is not the dcache or pseudo-fs logic. It is the trio of buffer-copy helpers `simple_read_from_buffer()`, `simple_write_to_buffer()`, and `memory_read_from_buffer()`, which expose clear bounds, offset, and short-copy behavior without needing live dentries, inode locks, or mount state.
- directory cursor helpers such as `dcache_dir_open()`, `dcache_dir_lseek()`, and `dcache_readdir()` remain substantially riskier because they depend on cursor dentries, sibling lists, lock ordering, and reschedule-aware traversal.
- pseudo-filesystem and inode-lifecycle helpers such as `simple_fill_super()`, `pseudo_fs_get_tree()`, `simple_pin_fs()`, and the rename or setattr families are still too broad for the first Phase 13 wrapper slice.

## Recorded gaps

The survey manifest now records:

- the landed `phase13-build-gate`
- the landed `phase13-make-target`
- the landed `phase13-libfs-survey-gate`
- the landed `phase13-libfs-survey-note`
- the ready-next `phase13-libfs-buffer-helper-starter`
- the blocked `phase13-libfs-dcache-cursor-helpers`
- the blocked `phase13-libfs-inode-and-pseudofs-lifecycle`

This keeps the lane explicit without overstating progress: Zigux now has a real Phase 13 libfs survey checkpoint, but it still does not claim any `fs/libfs.zig` implementation, dcache wrapper parity, pseudo-filesystem mounting, inode lifecycle, or rename-state behavior.

## Non-goals

This survey slice does not claim:

- a landed `fs/libfs.zig` file
- dcache cursor or directory-iteration helpers
- pseudo-filesystem mount or superblock helpers
- rename, unlink, rmdir, or setattr lifecycle helpers
- file-attribute, writeback, or fsync wrapper parity
- VFS object ownership, locking, or mount-state behavior

## Gates

1. run the dedicated Phase 13 build
- `zig build test --build-file zigux/tests/phase13_build.zig`

2. run the convenience target
- `make -C zigux phase13`

## Next bounded step

Stay in the Phase 13 libfs lane and add one tiny `fs/libfs.zig` buffer-helper starter next, limited to `simple_read_from_buffer()`, `simple_write_to_buffer()`, and `memory_read_from_buffer()` semantics plus lane-local tests for offset validation, truncation to available space, and short-copy accounting before any dcache, pseudo-fs, or inode-lifecycle work.