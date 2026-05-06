# Phase 13 libfs Slice

This bounded Phase 13 slice starts `fs/libfs.zig` with a pure helper-first foothold anchored to `fs/libfs.c`.

The current helper stays intentionally narrow:

- mirrors the `simple_statfs()` default summary shape by folding an encoded device id into the split `fsid`, carrying the filesystem magic, and fixing the `PAGE_SIZE` and `NAME_MAX` defaults used by the helper
- preserves the `always_delete_dentry()` policy that negative dentries in this helper family should be discarded immediately
- models the branch decisions inside `simple_lookup()` without claiming live dentry mutation, inode locking, Unicode tables, or VFS registration
- adds the first bounded buffer-copy trio around `simple_read_from_buffer()`, `simple_write_to_buffer()`, and `memory_read_from_buffer()` by keeping the work in pure offset, truncation, and short-copy accounting rather than pretending to own user-copy primitives or live file state
- keeps the landed pure seek-planning helper surface around the early `dcache_dir_lseek()` and `offset_dir_llseek()` policy surface so Zigux can validate `SEEK_SET` and `SEEK_CUR`, negative-offset rejection, max-position checks, and the point where a positive cursor walk would become necessary without modeling live dentries or file structs
- adds one tiny `dcache_readdir()`-adjacent emit planner that models the `dir_emit_dots()` handoff, the transition into positive entry scanning, emitted-entry position accounting, and the early stop case before any live cursor dentries or inode-backed state are touched
- adds the landed `dcache_dir_open()` setup helper surface by keeping the work in cursor allocation from `file->f_path.dentry`, `private_data` handoff, and the `-ENOMEM` fallback before any sibling traversal, lock ordering, or live cursor mutation is claimed
- adds the landed transaction acquire helper surface around `simple_transaction_get()` by keeping the work in page-bounded staging-buffer sizing, single-write-per-open gating, and empty-response start-state bookkeeping before any live publish, read, or release behavior is claimed
- adds the landed transaction publish helper surface around `simple_transaction_set()` by keeping the work in response-size validation, required private-data handoff, publish-barrier ordering, and published-size bookkeeping before any live readback or release behavior is claimed
- adds the landed transaction release helper surface around `simple_transaction_release()` by keeping the work in page-backed private-data cleanup, release bookkeeping, and the zero return path before any live file lifecycle, readback, or cursor-backed state is claimed
- adds the landed `generic_check_addressable()` planner by keeping the work in shift-overflow rejection, zero-block passthrough, minimum block-size validation, and explicit sector-addressability plus page-cache limit checks before any live superblock, page-cache, or inode ownership is claimed

This slice does not claim `d_add()` side effects, cursor-backed directory iteration, inode allocation, pseudo-fs mounting, or any other live VFS plumbing from the wider `fs/libfs.c` body.

The next honest bounded step in this same lane should stay smaller than deeper cursor traversal. A pure `simple_open()` private-data handoff planner is still the best next helper-first candidate, while the deeper `dcache_readdir()` cursor-resume packet around sibling traversal, reschedule-aware cursor movement, and lock-ordering preconditions should remain blocked until those boundaries are spelled out without pretending to own live VFS state.
