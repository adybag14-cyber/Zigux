# Phase 13 libfs Slice

This bounded Phase 13 slice starts `fs/libfs.zig` with a pure helper-first foothold anchored to `fs/libfs.c`.

The starter stays intentionally narrow:

- mirrors the `simple_statfs()` default summary shape by folding an encoded device id into the split `fsid`, carrying the filesystem magic, and fixing the `PAGE_SIZE` and `NAME_MAX` defaults used by the helper
- preserves the `always_delete_dentry()` policy that negative dentries in this helper family should be discarded immediately
- models the branch decisions inside `simple_lookup()` without claiming live dentry mutation, inode locking, Unicode tables, or VFS registration

This slice does not claim `d_add()` side effects, cursor-backed directory iteration, offset bookkeeping, inode allocation, pseudo-fs mounting, or any other live VFS plumbing from the wider `fs/libfs.c` body.

The next honest bounded step in this same lane is to add one small pure helper around the early directory-reading surface, such as a reviewable `dcache_readdir()` planning helper or a cursor-free offset-policy wrapper, before attempting any live dentries or inode-backed state.
