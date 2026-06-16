const std = @import("std");
const diff = @import("artifact_diff.zig");

const missing_case_names = [_][]const u8{
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
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

test "missing path output keeps stable expected and actual existence markers" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "present.txt", .data = "ok\n" });

    const present = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "present.txt");
    defer std.testing.allocator.free(present);
    const missing = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "missing.txt");
    defer std.testing.allocator.free(missing);
    const other_missing = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "other-missing.txt");
    defer std.testing.allocator.free(other_missing);

    const missing_expected = (try diff.pathProblemLines(std.testing.io, std.testing.allocator, missing, present)).?;
    defer diff.freeComparisonResult(std.testing.allocator, missing_expected);
    try std.testing.expectEqualStrings("EXPECTED_EXISTS=False", missing_expected.extra_lines[0]);
    try std.testing.expectEqualStrings("ACTUAL_EXISTS=True", missing_expected.extra_lines[1]);

    const missing_actual = (try diff.pathProblemLines(std.testing.io, std.testing.allocator, present, missing)).?;
    defer diff.freeComparisonResult(std.testing.allocator, missing_actual);
    try std.testing.expectEqualStrings("EXPECTED_EXISTS=True", missing_actual.extra_lines[0]);
    try std.testing.expectEqualStrings("ACTUAL_EXISTS=False", missing_actual.extra_lines[1]);

    const missing_both = (try diff.pathProblemLines(std.testing.io, std.testing.allocator, missing, other_missing)).?;
    defer diff.freeComparisonResult(std.testing.allocator, missing_both);
    try std.testing.expectEqualStrings("EXPECTED_EXISTS=False", missing_both.extra_lines[0]);
    try std.testing.expectEqualStrings("ACTUAL_EXISTS=False", missing_both.extra_lines[1]);
}

test "missing path self-test cases cover text json and digest modes" {
    for (missing_case_names) |case_name| {
        try std.testing.expect(catalogContains(case_name));
    }
    try std.testing.expect(catalogContains("bytes_missing_expected"));
    try std.testing.expect(catalogContains("bytes_missing_actual"));
    try std.testing.expect(catalogContains("bytes_missing_both"));
}

test "missing path guard runs before mode-specific artifact reads" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const missing = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "missing.txt");
    defer std.testing.allocator.free(missing);
    const other_missing = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "other-missing.txt");
    defer std.testing.allocator.free(other_missing);

    const text_missing = try diff.compare(std.testing.io, std.testing.allocator, .text, missing, other_missing);
    defer diff.freeComparisonResult(std.testing.allocator, text_missing);
    try std.testing.expect(!text_missing.ok);
    try std.testing.expectEqualStrings("EXPECTED_EXISTS=False", text_missing.extra_lines[0]);

    const json_missing = try diff.compare(std.testing.io, std.testing.allocator, .json, missing, other_missing);
    defer diff.freeComparisonResult(std.testing.allocator, json_missing);
    try std.testing.expect(!json_missing.ok);

    const bytes_missing = try diff.compare(std.testing.io, std.testing.allocator, .bytes, missing, other_missing);
    defer diff.freeComparisonResult(std.testing.allocator, bytes_missing);
    try std.testing.expect(!bytes_missing.ok);
}