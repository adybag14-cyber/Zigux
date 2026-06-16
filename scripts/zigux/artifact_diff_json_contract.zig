const std = @import("std");
const diff = @import("artifact_diff.zig");

const json_case_names = [_][]const u8{
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
};

fn tmpPath(allocator: std.mem.Allocator, tmp_sub_path: []const u8, name: []const u8) ![]const u8 {
    return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/{s}", .{ tmp_sub_path, name });
}

fn catalogContains(case_name: []const u8) bool {
    for (diff.self_test_case_names) |name| {
        if (std.mem.eql(u8, name, case_name)) return true;
    }
    return false;
}

test "artifact diff keeps json self-test catalog explicit" {
    for (json_case_names) |name| {
        try std.testing.expect(catalogContains(name));
    }
}

test "artifact diff preserves json canonicalization and error reporting surface" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "expected.json", .data = "{\"alpha\": 1, \"beta\": [2, 3]}\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "actual.json", .data = "{\n \"beta\": [2, 3],\n \"alpha\": 1\n}\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "invalid-expected.json", .data = "{\"alpha\": 1,\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "invalid-actual.json", .data = "{\"alpha\": 1,\n" });

    const expected_json = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "expected.json");
    defer std.testing.allocator.free(expected_json);
    const actual_json = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "actual.json");
    defer std.testing.allocator.free(actual_json);
    const invalid_expected = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "invalid-expected.json");
    defer std.testing.allocator.free(invalid_expected);
    const invalid_actual = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "invalid-actual.json");
    defer std.testing.allocator.free(invalid_actual);

    const json_pass = try diff.compare(std.testing.io, std.testing.allocator, .json, expected_json, actual_json);
    defer diff.freeComparisonResult(std.testing.allocator, json_pass);
    try std.testing.expect(json_pass.ok);

    const json_mismatch = try diff.compare(std.testing.io, std.testing.allocator, .json, expected_json, invalid_actual);
    defer diff.freeComparisonResult(std.testing.allocator, json_mismatch);
    try std.testing.expect(!json_mismatch.ok);

    const expected_error = try diff.compare(std.testing.io, std.testing.allocator, .json, invalid_expected, actual_json);
    defer diff.freeComparisonResult(std.testing.allocator, expected_error);
    try std.testing.expect(!expected_error.ok);
    try std.testing.expect(std.mem.startsWith(u8, expected_error.extra_lines[0], "EXPECTED_JSON_ERROR="));

    const actual_error = try diff.compare(std.testing.io, std.testing.allocator, .json, expected_json, invalid_actual);
    defer diff.freeComparisonResult(std.testing.allocator, actual_error);
    try std.testing.expect(!actual_error.ok);
    try std.testing.expect(std.mem.startsWith(u8, actual_error.extra_lines[0], "ACTUAL_JSON_ERROR="));
}

test "artifact diff json mode stays separate from text and byte digest modes" {
    try std.testing.expectEqual(diff.Mode.text, diff.Mode.parse("text").?);
    try std.testing.expectEqual(diff.Mode.json, diff.Mode.parse("json").?);
    try std.testing.expectEqual(diff.Mode.bytes, diff.Mode.parse("bytes").?);
    try std.testing.expectEqual(diff.Mode.bytes, diff.Mode.parse("sha256").?);
}