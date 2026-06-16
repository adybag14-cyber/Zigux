const std = @import("std");
const diff = @import("artifact_diff.zig");

fn tmpPath(allocator: std.mem.Allocator, tmp_sub_path: []const u8, name: []const u8) ![]const u8 {
    return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/{s}", .{ tmp_sub_path, name });
}

test "json utf8 errors use stable side-prefixed sentinels" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "expected.json", .data = "{}\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "invalid-expected-utf8.json", .data = &[_]u8{ 0xff, '{', '\n' } });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "invalid-actual-utf8.json", .data = &[_]u8{ 0xff, '{', '\n' } });

    const expected_json = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "expected.json");
    defer std.testing.allocator.free(expected_json);
    const invalid_expected_utf8 = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "invalid-expected-utf8.json");
    defer std.testing.allocator.free(invalid_expected_utf8);
    const invalid_actual_utf8 = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "invalid-actual-utf8.json");
    defer std.testing.allocator.free(invalid_actual_utf8);

    const expected_side = try diff.compare(std.testing.io, std.testing.allocator, .json, invalid_expected_utf8, expected_json);
    defer diff.freeComparisonResult(std.testing.allocator, expected_side);
    try std.testing.expect(!expected_side.ok);
    try std.testing.expect(std.mem.startsWith(u8, expected_side.extra_lines[0], "EXPECTED_UTF8_ERROR="));
    try std.testing.expect(std.mem.endsWith(u8, expected_side.extra_lines[0], ":0: invalid start byte"));

    const actual_side = try diff.compare(std.testing.io, std.testing.allocator, .json, expected_json, invalid_actual_utf8);
    defer diff.freeComparisonResult(std.testing.allocator, actual_side);
    try std.testing.expect(!actual_side.ok);
    try std.testing.expect(std.mem.startsWith(u8, actual_side.extra_lines[0], "ACTUAL_UTF8_ERROR="));
}

test "expected-side utf8 failure keeps precedence when both sides are invalid" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "invalid-expected-utf8.json", .data = &[_]u8{ 0xff, '{', '\n' } });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "invalid-actual-utf8.json", .data = &[_]u8{ 0xff, '{', '\n' } });

    const invalid_expected_utf8 = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "invalid-expected-utf8.json");
    defer std.testing.allocator.free(invalid_expected_utf8);
    const invalid_actual_utf8 = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "invalid-actual-utf8.json");
    defer std.testing.allocator.free(invalid_actual_utf8);

    const both_invalid = try diff.compare(std.testing.io, std.testing.allocator, .json, invalid_expected_utf8, invalid_actual_utf8);
    defer diff.freeComparisonResult(std.testing.allocator, both_invalid);
    try std.testing.expect(!both_invalid.ok);
    try std.testing.expect(std.mem.startsWith(u8, both_invalid.extra_lines[0], "EXPECTED_UTF8_ERROR="));
}

test "self-test catalog retains json invalid case slots" {
    const cases = [_][]const u8{ "json_invalid_expected", "json_invalid_actual", "json_invalid_both" };
    for (cases) |case_name| {
        var found = false;
        for (diff.self_test_case_names) |name| {
            if (std.mem.eql(u8, name, case_name)) found = true;
        }
        try std.testing.expect(found);
    }
}