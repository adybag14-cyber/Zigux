const std = @import("std");

pub const CursorReleaseReason = enum {
    missing_private_cursor,
    waiting_for_end_of_directory,
    waiting_for_cursor_consumption,
    ready_for_teardown,
};

pub const DcacheCursorReleasePacketDescriptor = struct {
    provides_dcache_dir_close_planning: bool = true,
    keeps_helper_first_boundary: bool = true,
    claims_live_cursor_unlink: bool = false,
    claims_lock_ordering: bool = false,
};

pub const DcacheCursorReleasePlan = struct {
    descriptor: DcacheCursorReleasePacketDescriptor = .{},
    requires_private_cursor: bool,
    releases_private_cursor: bool,
    ready_at_end_of_directory: bool,
    cursor_consumed: bool,
    reason: CursorReleaseReason,
};

pub fn planDcacheDirClose(
    has_private_cursor: bool,
    ready_at_end_of_directory: bool,
    cursor_consumed: bool,
) DcacheCursorReleasePlan {
    if (!has_private_cursor) {
        return .{
            .requires_private_cursor = true,
            .releases_private_cursor = false,
            .ready_at_end_of_directory = ready_at_end_of_directory,
            .cursor_consumed = cursor_consumed,
            .reason = .missing_private_cursor,
        };
    }

    if (!ready_at_end_of_directory) {
        return .{
            .requires_private_cursor = true,
            .releases_private_cursor = false,
            .ready_at_end_of_directory = false,
            .cursor_consumed = cursor_consumed,
            .reason = .waiting_for_end_of_directory,
        };
    }

    if (!cursor_consumed) {
        return .{
            .requires_private_cursor = true,
            .releases_private_cursor = false,
            .ready_at_end_of_directory = true,
            .cursor_consumed = false,
            .reason = .waiting_for_cursor_consumption,
        };
    }

    return .{
        .requires_private_cursor = true,
        .releases_private_cursor = true,
        .ready_at_end_of_directory = true,
        .cursor_consumed = true,
        .reason = .ready_for_teardown,
    };
}

test "dcache_dir_close planner stays reviewable and helper-first" {
    const missing_private_cursor = planDcacheDirClose(false, false, false);
    try std.testing.expectEqual(CursorReleaseReason.missing_private_cursor, missing_private_cursor.reason);
    try std.testing.expect(!missing_private_cursor.releases_private_cursor);
    try std.testing.expect(!missing_private_cursor.descriptor.claims_live_cursor_unlink);
    try std.testing.expect(!missing_private_cursor.descriptor.claims_lock_ordering);

    const waiting_for_end = planDcacheDirClose(true, false, false);
    try std.testing.expectEqual(CursorReleaseReason.waiting_for_end_of_directory, waiting_for_end.reason);
    try std.testing.expect(!waiting_for_end.releases_private_cursor);

    const waiting_for_consumption = planDcacheDirClose(true, true, false);
    try std.testing.expectEqual(CursorReleaseReason.waiting_for_cursor_consumption, waiting_for_consumption.reason);
    try std.testing.expect(!waiting_for_consumption.releases_private_cursor);

    const ready_for_teardown = planDcacheDirClose(true, true, true);
    try std.testing.expectEqual(CursorReleaseReason.ready_for_teardown, ready_for_teardown.reason);
    try std.testing.expect(ready_for_teardown.releases_private_cursor);
}
