# Phase 13 libfs Slice

This bounded Phase 13 slice starts `fs/libfs.zig` with a pure helper-first foothold anchored to `fs/libfs.c`.

The current helper stays intentionally narrow:

- mirrors the `simple_statfs()` default summary shape by folding an encoded device id into the split `fsid`, carrying the filesystem magic, and fixing the `PAGE_SIZE` and `NAME_MAX` defaults used by the helper
- preserves the `always_delete_dentry()` policy that negative dentries in this helper family should be discarded immediately
- models the branch decisions inside `simple_lookup()` without claiming live dentry mutation, inode locking, Unicode tables, or VFS registration
- adds the first bounded buffer-copy trio around `simple_read_from_buffer()`, `simple_write_to_buffer()`, and `memory_read_from_buffer()` by keeping the work in pure offset, truncation, and short-copy accounting rather than pretending to own user-copy primitives or live file state
- keeps the landed pure seek-planning wrappers around the early `dcache_dir_lseek()` and `offset_dir_llseek()` policy surface so Zigux can validate `SEEK_SET` and `SEEK_CUR`, negative-offset rejection, max-position checks, and the point where a positive cursor walk would become necessary without modeling live dentries or file structs
- adds one tiny `dcache_readdir()`-adjacent emit planner that models the `dir_emit_dots()` handoff, the transition into positive entry scanning, emitted-entry position accounting, and the early stop case before any live cursor dentries or inode-backed state are touched
- adds one bounded `dcache_dir_open()` / `dcache_readdir()` cursor-precondition planner that keeps the work in cursor-allocation failure, `dir_emit_dots()` gating, first-child-versus-cursor resume selection, and missing-private-data blocking before any sibling-list mutation, lock ordering, or live cursor dentries are claimed
- adds one bounded shared cursor-reposition planner that models the post-scan `hlist_del_init()` detach plus the `hlist_add_before()` / `hlist_add_behind()` reinsertion choices used by `dcache_readdir()` and `dcache_dir_lseek()` without claiming live sibling-list mutation, lock ordering, or cursor dentry ownership
- adds one bounded `simple_transaction_get()` / `simple_transaction_set()` staging-buffer planner that models request-size limits, one-write-per-open reservation, copy-fault retention, and publish-size bookkeeping without claiming live page allocation, file-private storage mutation, or pseudo-filesystem state
- adds one bounded `simple_transaction_read()` / `simple_transaction_release()` follow-up that keeps the work in pure private-data presence checks, read-delegation intent, and release bookkeeping before any live dentries, inode-backed state, or pseudo-filesystem lifecycle is touched

This slice does not claim `d_add()` side effects, cursor-backed directory iteration, inode allocation, pseudo-fs mounting, simple-transaction state, or any other live VFS plumbing from the wider `fs/libfs.c` body.

The next honest bounded step in this same lane is to keep the libfs cursor work parked at this pure boundary until a later phase can justify any deeper reschedule-aware traversal, live sibling-list mutation, lock ordering, or cursor dentry ownership modeling.
