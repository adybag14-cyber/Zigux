const std = @import("std");
const policy = @import("toolchain_policy.zig");

test "version evaluation keeps exact present too old and not pinned states" {
    const present = try policy.evaluateToolchainVersion(
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(policy.ToolchainStatus.present, present.status);
    try std.testing.expect(present.note == null);

    const too_old = try policy.evaluateToolchainVersion(
        "0.16.0",
        "0.17.0-dev.877+a3ae499dc",
        null,
    );
    try std.testing.expectEqual(policy.ToolchainStatus.too_old, too_old.status);
    try std.testing.expect(too_old.note == null);

    const not_pinned = try policy.evaluateToolchainVersion(
        "0.17.0-dev.877+stalehash",
        "0.17.0-dev.877+a3ae499dc",
        "0.17.0-dev.877+a3ae499dc",
    );
    try std.testing.expectEqual(policy.ToolchainStatus.not_pinned, not_pinned.status);
    try std.testing.expect(not_pinned.note != null);
    try std.testing.expectEqualStrings("0.17.0-dev.877+a3ae499dc", not_pinned.note.?);
}

test "version ordering treats dev builds below release at same semver" {
    const dev = try policy.parseZigVersion("0.17.0-dev.1+abc");
    const release = try policy.parseZigVersion("0.17.0");
    try std.testing.expect(dev.lessThan(release));
}

test "policy archive filename matches pinned channel contract" {
    var buffer: [96]u8 = undefined;
    const filename = try policy.policyArchiveFilename(
        "x86_64-linux",
        "0.17.0-dev.877+a3ae499dc",
        &buffer,
    );
    try std.testing.expectEqualStrings(
        "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz",
        filename,
    );
}

test "self-test catalog covers evaluation branches" {
    const cases = [_]struct { version: []const u8, min: []const u8, expected: policy.ToolchainStatus }{
        .{ .version = "0.17.0-dev.877+a3ae499dc", .min = "0.17.0-dev.877+a3ae499dc", .expected = .present },
        .{ .version = "0.15.2", .min = "0.17.0-dev.877+a3ae499dc", .expected = .too_old },
    };
    for (cases) |case| {
        const result = try policy.evaluateToolchainVersion(case.version, case.min, null);
        try std.testing.expectEqual(case.expected, result.status);
    }
    try std.testing.expectEqual(@as(usize, 2), cases.len);
}