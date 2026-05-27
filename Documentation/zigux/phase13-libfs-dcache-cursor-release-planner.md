# Phase 13 libfs dcache cursor release planner

This bounded Phase 13 packet keeps `fs/libfs.c` attached to a helper-first `dcache_dir_close()` cursor-release slice.

Current repo reality for this packet is intentionally narrow:

- `fs/libfs_dcache_cursor_release.zig` keeps the close-path packet helper-first and planning-only
- `zigux/tests/phase13_libfs_dcache_cursor_release.zig` replays the release preconditions without claiming live cursor unlinking
- `zigux/tests/phase13_libfs_dcache_cursor_release_manifest.json` records the landed helper packet, the still-missing shared Phase 13 build route, and the blocked unlink and lock-ordering boundaries
- `scripts/zigux/check-phase13-libfs-dcache-cursor-release-packet.py` keeps the helper, replay, manifest, and doc note aligned

This packet does not claim sibling traversal, cursor dentry mutation, live cursor unlinking, lock ordering, or broader VFS lifetime ownership.

The next honest bounded step in this same family is a fresh packet-local reread across the libfs survey, slice, and manifest before widening into any deeper teardown semantics.
