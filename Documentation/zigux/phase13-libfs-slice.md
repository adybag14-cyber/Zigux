# Phase 13 libfs Slice

This bounded Phase 13 slice keeps `fs/libfs.c` attached to a shipped helper-first libfs packet while keeping live filesystem behavior out of scope.

Current repo reality on `master` is broader than the stale reminder text claimed:
  * `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, and `scripts/zigux/check-phase13-libfs-packet.py` are current repo evidence
  * the helper packet already covers lookup shaping, `simple_transaction_get()` / `simple_transaction_set()` / `simple_transaction_release()` planning, `generic_check_addressable()` planning, `simple_offset_add()` / `simple_offset_remove()` planning, `offset_readdir()` planning, and offset-based rename plus rename-exchange planning
  * the adjacent `dcache_dir_open()` / `dcache_readdir()` cursor-precondition packet is now landed through `fs/libfs_dcache_cursor.zig`, `zigux/tests/phase13_libfs_dcache_cursor.zig`, `zigux/tests/phase13_libfs_dcache_cursor_manifest.json`, `Documentation/zigux/phase13-libfs-dcache-cursor-planner.md`, and `scripts/zigux/check-phase13-libfs-dcache-cursor-packet.py`
  * the older shared `zigux/tests/phase13_build.zig` route is still missing on current `master`, so the libfs packet remains focused rather than shared-build-backed

This slice therefore stays honest about the boundary: current `master` does prove a live helper-first libfs foothold and its focused replay routes, but it does not prove shared Phase 13 build wiring or any deeper live VFS ownership.

This slice does not claim `d_add()` side effects, cursor-backed sibling traversal, live directory-map mutation, inode allocation or lifetime ownership, pseudo-fs mounting, page-cache-backed filesystem state, or any other live VFS plumbing from the wider `fs/libfs.c` body.

The next honest bounded step in this same helper family is the smallest `dcache_dir_close()` cursor release planner that stays reviewable without claiming live cursor unlinking, sibling mutation, or lock ordering.
