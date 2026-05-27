const std = @import("std");
const cursor = @import("libfs_dcache_cursor");

test "dcache dir open planner keeps cursor private and skips sibling mutation claims" {
    const fresh = cursor.planDcacheDirOpen(true, false);
    try std.testing.expectEqualStrings("fs/libfs.c", fresh.anchor);
    try std.testing.expectEqual(cursor.DcacheDirOpenStatus.ok, fresh.status);
    try std.testing.expect(fresh.installs_private_cursor);
    try std.testing.expect(!fresh.may_reuse_existing_cursor);
    try std.testing.expect(fresh.keeps_cursor_private);
    try std.testing.expect(!fresh.claims_lock_ordering);
    try std.testing.expect(!fresh.mutates_dcache_siblings);

    const reused = cursor.planDcacheDirOpen(true, true);
    try std.testing.expectEqual(cursor.DcacheDirOpenStatus.ok, reused.status);
    try std.testing.expect(!reused.installs_private_cursor);
    try std.testing.expect(reused.may_reuse_existing_cursor);

    const blocked = cursor.planDcacheDirOpen(false, false);
    try std.testing.expectEqual(cursor.DcacheDirOpenStatus.missing_shared_inode, blocked.status);
    try std.testing.expect(!blocked.installs_private_cursor);
}

test "dcache readdir planner stays on preconditions and end-of-directory gating" {
    const missing = cursor.planDcacheReaddir(cursor.dir_offset_first, true, false);
    try std.testing.expectEqual(cursor.DcacheReaddirStatus.missing_private_cursor, missing.status);
    try std.testing.expectEqual(@as(?cursor.DcacheReaddirMode, null), missing.mode);
    try std.testing.expect(missing.keeps_current_pos);

    const blocked = cursor.planDcacheReaddir(cursor.dir_offset_first + 1, false, true);
    try std.testing.expectEqual(cursor.DcacheReaddirStatus.ok, blocked.status);
    try std.testing.expectEqual(cursor.DcacheReaddirMode.blocked_on_emit_dots, blocked.mode.?);
    try std.testing.expect(blocked.requires_dir_emit_dots);
    try std.testing.expect(!blocked.enters_cursor_scan);
    try std.testing.expect(blocked.keeps_current_pos);

    const active = cursor.planDcacheReaddir(cursor.dir_offset_first + 1, true, true);
    try std.testing.expectEqual(cursor.DcacheReaddirStatus.ok, active.status);
    try std.testing.expectEqual(cursor.DcacheReaddirMode.ready_to_scan, active.mode.?);
    try std.testing.expect(active.enters_cursor_scan);
    try std.testing.expect(!active.keeps_current_pos);
    try std.testing.expect(!active.claims_sibling_traversal);

    const terminal = cursor.planDcacheReaddir(cursor.dir_offset_end_of_directory, true, true);
    try std.testing.expectEqual(cursor.DcacheReaddirMode.ready_at_end_of_directory, terminal.mode.?);
    try std.testing.expect(!terminal.enters_cursor_scan);
    try std.testing.expect(terminal.keeps_current_pos);
    try std.testing.expect(terminal.points_at_end_of_directory);

    const invalid = cursor.planDcacheReaddir(-1, true, true);
    try std.testing.expectEqual(cursor.DcacheReaddirStatus.negative_position, invalid.status);
    try std.testing.expectEqual(@as(?cursor.DcacheReaddirMode, null), invalid.mode);
}
