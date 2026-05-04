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
- adds one bounded post-scan cursor-reposition planner for the `dcache_dir_lseek()` and `dcache_readdir()` tails so Zigux can validate when the private cursor is merely unhashed versus re-anchored before or behind a found positive dentry, and the exported helper descriptor now advertises that landed planning surface instead of leaving it hidden behind older starter scaffolding, without claiming live sibling-list mutation, lock ordering, or cursor dentry ownership
- adds one bounded `dcache_dir_close()` release planner that models the unconditional `dput(file->private_data)` call, the zero-error close outcome, and the fact that a missing private cursor remains a tolerated no-op instead of widening into live refcount mutation or directory teardown
- adds one bounded `simple_transaction_get()` / `simple_transaction_set()` staging-buffer planner that models request-size limits, one-write-per-open reservation, copy-fault retention, and publish-size bookkeeping without claiming live page allocation, file-private storage mutation, or pseudo-filesystem state
- adds one bounded `simple_transaction_read()` / `simple_transaction_release()` follow-up that keeps the work in pure private-data presence checks, read-delegation intent, and release bookkeeping before any live dentries, inode-backed state, or pseudo-filesystem lifecycle is touched
- adds one bounded `simple_open()` planner that keeps the inode-private-data borrow explicit by modeling when `inode->i_private` is copied into `file->private_data` and when the open path remains a pure zero-error no-op, without claiming live inode mutation, file allocation, or broader open/close lifecycle ownership
- adds one pure `generic_check_addressable()` addressability planner that keeps block-size validation, last-block accounting, and sector or page addressability limits explicit without claiming live superblock, page-cache, or inode ownership

This slice does not claim `d_add()` side effects, cursor-backed directory iteration, inode allocation, pseudo-fs mounting, simple-transaction state, or any other live VFS plumbing from the wider `fs/libfs.c` body.

The current helper packet now covers the landed addressability boundary too.
The next honest same-lane work, if any, is review-local only: keep notes and packet governance aligned while the remaining cursor-backed helpers plus inode and pseudo-filesystem lifecycle stay blocked on live VFS state.
