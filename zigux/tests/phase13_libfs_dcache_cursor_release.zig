const std = @import("std");
const release = @import("libfs_dcache_cursor_release");

fn describeReason(reason: release.CursorReleaseReason) []const u8 {
    return switch (reason) {
        .missing_private_cursor => "missing_private_cursor",
        .waiting_for_end_of_directory => "waiting_for_end_of_directory",
        .waiting_for_cursor_consumption => "waiting_for_cursor_consumption",
        .ready_for_teardown => "ready_for_teardown",
    };
}

test "dcache dir close planner keeps cursor teardown reviewable" {
    const missing_private_cursor = release.planDcacheDirClose(false, false, false);
    try std.testing.expectEqualStrings(
        "missing_private_cursor",
        describeReason(missing_private_cursor.reason),
    );
    try std.testing.expect(!missing_private_cursor.releases_private_cursor);

    const waiting_for_end_of_directory = release.planDcacheDirClose(true, false, true);
    try std.testing.expectEqualStrings(
        "waiting_for_end_of_directory",
        describeReason(waiting_for_end_of_directory.reason),
    );
    try std.testing.expect(!waiting_for_end_of_directory.releases_private_cursor);

    const waiting_for_cursor_consumption = release.planDcacheDirClose(true, true, false);
    try std.testing.expectEqualStrings(
        "waiting_for_cursor_consumption",
        describeReason(waiting_for_cursor_consumption.reason),
    );
    try std.testing.expect(!waiting_for_cursor_consumption.releases_private_cursor);

    const ready_for_teardown = release.planDcacheDirClose(true, true, true);
    try std.testing.expectEqualStrings(
        "ready_for_teardown",
        describeReason(ready_for_teardown.reason),
    );
    try std.testing.expect(ready_for_teardown.releases_private_cursor);
}
