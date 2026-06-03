const std = @import("std");

const policy = @embedFile("zig-toolchain-policy.json");

const expected_channel = "0.17.0-dev.758+748e7c5e3";
const expected_archive_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, policy, needle) != null);
}

fn expectNotContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, policy, needle) == null);
}

fn countOccurrences(needle: []const u8) usize {
    var count: usize = 0;
    var cursor: []const u8 = policy;
    while (std.mem.indexOf(u8, cursor, needle)) |index| {
        count += 1;
        cursor = cursor[index + needle.len ..];
    }
    return count;
}

test "toolchain policy keeps channel and minimum version in exact lockstep" {
    try expectContains("\"phase\": \"Phase 2\"");
    try expectContains("\"channel_minimum_lockstep\": true");
    try expectContains("\"channel\": \"" ++ expected_channel ++ "\"");
    try expectContains("\"minimum_version\": \"" ++ expected_channel ++ "\"");
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(expected_channel));

    try expectNotContains("0.17.0-dev.87+9b177a7d2");
}

test "toolchain policy keeps the trusted archive target closed and pinned" {
    try expectContains("\"archive_sha256\": {");
    try expectContains("\"archive_target_scope\": [");
    try expectContains("\"x86_64-linux\": \"" ++ expected_archive_sha256 ++ "\"");
    try expectContains("\"x86_64-linux\"");
    try std.testing.expectEqual(@as(usize, 2), countOccurrences("\"x86_64-linux\""));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(expected_archive_sha256));
}

test "toolchain policy keeps the Phase 2 required route roster review visible" {
    const routes = [_][]const u8{
        "\"phase2-toolchain\"",
        "\"phase2-tools\"",
        "\"phase2-kconfig\"",
        "\"phase2-cross\"",
        "\"phase2-genksyms\"",
        "\"phase2-fixdep\"",
        "\"phase2-validate\"",
    };

    var previous_index: usize = 0;
    for (routes, 0..) |marker, route_index| {
        const found_index = std.mem.indexOf(u8, policy, marker) orelse return error.MissingRoute;
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(marker));
        if (route_index > 0) {
            try std.testing.expect(found_index > previous_index);
        }
        previous_index = found_index;
    }

    try std.testing.expectEqual(@as(usize, routes.len), countOccurrences("phase2-"));
}
