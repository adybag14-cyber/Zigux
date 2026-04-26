# Phase 13 libfs Slice

This bounded Phase 13 slice starts `fs/libfs.zig` with a pure helper-first foothold anchored to `fs/libfs.c`.

The current helper stays intentionally narrow:

- mirrors the `simple_statfs()` default summary shape by folding an encoded device id into the split `fsid`, carrying the filesystem magic, and fixing the `PAGE_SIZE` and `NAME_MAX` defaults used by the helper
- preserves the `always_delete_dentry()` policy that negative dentries in this helper family should be discarded immediately
- models the branch decisions inside `simple_lookup()` without claiming live dentry mutation, inode locking, Unicode tables, or VFS registration
- adds the first bounded buffer-copy trio around `simple_read_from_buffer()`, `simple_write_to_buffer()`, and `memory_read_from_buffer()` by keeping the work in pure offset, truncation, and short-copy accounting rather than pretending to own user-copy primitives or live file state
- adds a pure seek-planning wrapper around the early `dcache_dir_lseek()` and `offset_dir_llseek()` policy surface so Zigux can validate `SEEK_SET` or `SEEK_CUR`, negative-offset rejection, max-position checks, and the point where a cursor walk would become necessary without modeling live dentries or file structs

This slice does not claim `d_add()` side effects, cursor-backed directory iteration, inode allocation, pseudo-fs mounting, simple-transaction state, or any other live VFS plumbing from the wider `fs/libfs.c` body.

The next honest bounded step in this same lane is to stay helper-first and add one small directory-emit or transaction-buffer wrapper that still avoids live dentries, inode-backed state, and pseudo-filesystem lifecycle work.
