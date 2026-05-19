# Phase 13 libfs Slice

This bounded Phase 13 slice keeps `fs/libfs.zig` as a pure helper-first foothold anchored to `fs/libfs.c`.

The current helper stays intentionally narrow:
  * mirrors the `simple_statfs()` default summary shape by folding an encoded device id into the split `fsid`, carrying the filesystem magic, and fixing the `PAGE_SIZE` and `NAME_MAX` defaults used by the helper
  * preserves the `always_delete_dentry()` policy that negative dentries in this helper family should be discarded immediately
  * models the branch decisions inside `simple_lookup()` without claiming live dentry mutation, inode locking, Unicode tables, or VFS registration
  * keeps the bounded buffer-copy trio around `simple_read_from_buffer()`, `simple_write_to_buffer()`, and `memory_read_from_buffer()` in pure offset, truncation, and short-copy accounting rather than pretending to own user-copy primitives or live file state
  * keeps the landed pure seek-planning wrappers around the early `dcache_dir_lseek()` and `offset_dir_llseek()` policy surface so Zigux can validate `SEEK_SET` and `SEEK_CUR`, negative-offset rejection, max-position checks, and the point where a positive cursor walk would become necessary without modeling live dentries or file structs
  * keeps the `dcache_readdir()`-adjacent emit planner that models the `dir_emit_dots()` handoff, the transition into positive entry scanning, emitted-entry position accounting, and the early stop case before any live cursor dentries or inode-backed state are touched
  * adds helper-only offset-map planners around `simple_offset_add()`, `simple_offset_remove()`, and offset-based rename plus rename-exchange handling, keeping managed-slot classification, busy-to-ENOSPC remapping, erase bookkeeping, and reserved-slot behavior explicit without claiming live directory-map mutation
  * adds helper-only transaction acquire, release, and publish planners around `simple_transaction_get()`, `simple_transaction_release()`, and `simple_transaction_set()`, keeping page-backed private-data staging, cleanup, and publish bookkeeping explicit without claiming readback or pseudo-filesystem lifecycle ownership
  * adds helper-only `generic_check_addressable()` planning, keeping sector and page-index window checks plus the zero-block short-circuit explicit without claiming live inode, buffer-head, or page-cache ownership
This slice does not claim `d_add()` side effects, cursor-backed directory iteration, live directory-map mutation, inode allocation or lifetime ownership, pseudo-fs mounting, page-cache-backed filesystem state, or any other live VFS plumbing from the wider `fs/libfs.c` body.

The next honest bounded step in this same helper family is to stay helper-first and add one equally small offset-map lifecycle helper such as destroy planning, while keeping live dcache, inode, and wider filesystem ownership out of scope.
