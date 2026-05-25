# Phase 13 libfs Slice

This bounded Phase 13 slice keeps `fs/libfs.c` attached to a helper-first libfs target without pretending that the direct helper packet is currently shipped on `master`.

Current repo reality is narrower than the older reminder text claimed:
  * `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, and `zigux/tests/phase13_libfs_manifest.json` are still directly readable on current `master`
  * the current public repository tree does not expose a top-level `fs/` directory, so `fs/libfs.zig` is not directly readable on current `master`
  * exact current-`master` GitHub readback also returns missing for `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_build.zig`
  * because those direct packet paths are absent, the earlier helper-by-helper bullets for statfs shaping, delete-dentry policy, lookup shaping, buffer-copy helpers, directory seek planning, emit planning, offset-map planners, transaction planners, and addressability planning should be treated as intended helper-family scope only, not as shipped current-head evidence

This slice therefore stays honest about the boundary: current `master` still carries the libfs reminder packet, but it does not presently prove a live `fs/libfs.zig` helper foothold or its coupled replay routes.

This slice does not claim `d_add()` side effects, cursor-backed directory iteration, live directory-map mutation, inode allocation or lifetime ownership, pseudo-fs mounting, page-cache-backed filesystem state, or any other live VFS plumbing from the wider `fs/libfs.c` body. It also does not claim that the missing direct helper and replay paths have silently moved elsewhere in the current public tree.

The next honest bounded step in this same helper family is to keep stale shipped-path claims out of the reminder packet until one future same-lane follow-through rematerializes a direct `fs/libfs.zig` helper plus directly coupled replay evidence on current `master`.
