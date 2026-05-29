const std = @import("std");

const Status = enum {
    verified,
    missing_allowed,
    fail,
};

fn passValue(status: Status) []const u8 {
    return switch (status) {
        .verified, .missing_allowed => "pass",
        .fail => "fail",
    };
}

fn statusValue(status: Status) []const u8 {
    return switch (status) {
        .verified => "verified",
        .missing_allowed => "missing_allowed",
        .fail => "fail",
    };
}

fn formatLine(buf: []u8, comptime key: []const u8, value: []const u8) ![]const u8 {
    return std.fmt.bufPrint(buf, "LANE05_ARCHIVE_PARTS_PACKET_{s}={s}", .{ key, value });
}

fn emitsShardDetails(status: Status) bool {
    return status == .verified;
}

test "missing packet remains an explicit allowed bootstrap frontier" {
    var pass_buf: [64]u8 = undefined;
    var status_buf: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "LANE05_ARCHIVE_PARTS_PACKET=pass",
        try std.fmt.bufPrint(&pass_buf, "LANE05_ARCHIVE_PARTS_PACKET={s}", .{passValue(.missing_allowed)}),
    );
    try std.testing.expectEqualStrings(
        "LANE05_ARCHIVE_PARTS_PACKET_STATUS=missing_allowed",
        try formatLine(&status_buf, "STATUS", statusValue(.missing_allowed)),
    );
    try std.testing.expect(!emitsShardDetails(.missing_allowed));
}

test "verified packet output carries shard geometry after policy metadata" {
    var pass_buf: [64]u8 = undefined;
    var status_buf: [96]u8 = undefined;
    var chunk_buf: [96]u8 = undefined;
    var count_buf: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "LANE05_ARCHIVE_PARTS_PACKET=pass",
        try std.fmt.bufPrint(&pass_buf, "LANE05_ARCHIVE_PARTS_PACKET={s}", .{passValue(.verified)}),
    );
    try std.testing.expectEqualStrings(
        "LANE05_ARCHIVE_PARTS_PACKET_STATUS=verified",
        try formatLine(&status_buf, "STATUS", statusValue(.verified)),
    );
    try std.testing.expectEqualStrings(
        "LANE05_ARCHIVE_PARTS_PACKET_CHUNK_BYTES=786432",
        try std.fmt.bufPrint(&chunk_buf, "LANE05_ARCHIVE_PARTS_PACKET_CHUNK_BYTES={d}", .{786_432}),
    );
    try std.testing.expectEqualStrings(
        "LANE05_ARCHIVE_PARTS_PACKET_PART_COUNT=74",
        try std.fmt.bufPrint(&count_buf, "LANE05_ARCHIVE_PARTS_PACKET_PART_COUNT={d}", .{74}),
    );
    try std.testing.expect(emitsShardDetails(.verified));
}

test "failure status is never reported as a passing packet" {
    var pass_buf: [64]u8 = undefined;
    var status_buf: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "LANE05_ARCHIVE_PARTS_PACKET=fail",
        try std.fmt.bufPrint(&pass_buf, "LANE05_ARCHIVE_PARTS_PACKET={s}", .{passValue(.fail)}),
    );
    try std.testing.expectEqualStrings(
        "LANE05_ARCHIVE_PARTS_PACKET_STATUS=fail",
        try formatLine(&status_buf, "STATUS", statusValue(.fail)),
    );
    try std.testing.expect(!emitsShardDetails(.fail));
}

test "status vocabulary stays narrow for workflow parsers" {
    const allowed = [_]Status{ .verified, .missing_allowed, .fail };

    for (allowed) |status| {
        const value = statusValue(status);
        try std.testing.expect(
            std.mem.eql(u8, value, "verified") or
                std.mem.eql(u8, value, "missing_allowed") or
                std.mem.eql(u8, value, "fail"),
        );
        try std.testing.expect(!std.mem.containsAtLeast(u8, value, 1, " "));
        try std.testing.expect(!std.mem.containsAtLeast(u8, value, 1, "-"));
    }
}
