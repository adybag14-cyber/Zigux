# Phase 13 libfs dcache cursor planner

This bounded Phase 13 packet keeps `fs/libfs.c` attached to a helper-first `dcache_dir_open()` and `dcache_readdir()` precondition slice.

Current repo reality for this packet is intentionally narrow:

- `fs/libfs_dcache_cursor.zig` keeps the cursor packet helper-first and planning-only
- `zigux/tests/phase13_libfs_dcache_cursor.zig` replays the open and readdir precondition surface without claiming live cursor dentries
- `zigux/tests/phase13_libfs_dcache_cursor_manifest.json` records the landed helper packet, the still-missing shared Phase 13 build route, and the blocked live cursor traversal boundary
- `scripts/zigux/check-phase13-libfs-dcache-cursor-packet.py` keeps the helper, replay, manifest, and doc note aligned
- the neighboring `dcache_dir_close()` cursor-release side packet is now landed through `fs/libfs_dcache_cursor_release.zig`, `zigux/tests/phase13_libfs_dcache_cursor_release.zig`, `zigux/tests/phase13_libfs_dcache_cursor_release_manifest.json`, `Documentation/zigux/phase13-libfs-dcache-cursor-release-planner.md`, and `scripts/zigux/check-phase13-libfs-dcache-cursor-release-packet.py`

This packet does not claim sibling traversal, cursor dentry mutation, lock ordering, live rename relocation, or broader VFS lifetime ownership.

The next honest bounded step in this same family is a fresh packet-local reread across the cursor-precondition note, the cursor-release note, and the libfs survey before widening into deeper teardown semantics.
