const std = @import("std");
const diff = @import("artifact_diff.zig");

const text_case_names = [_][]const u8{
    "text_pass",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
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

test "artifact diff keeps text self-test catalog explicit" {
    for (text_case_names) |name| {
        try std.testing.expect(catalogContains(name));
    }
}

test "artifact diff text mode remains exact and separate from json and byte digest modes" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "expected.txt", .data = "alpha\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "actual.txt", .data = "alpha\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "expected.json", .data = "{}\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "blob.bin", .data = "bytes" });

    const expected_txt = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "expected.txt");
    defer std.testing.allocator.free(expected_txt);
    const actual_txt = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "actual.txt");
    defer std.testing.allocator.free(actual_txt);
    const expected_json = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "expected.json");
    defer std.testing.allocator.free(expected_json);
    const blob = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "blob.bin");
    defer std.testing.allocator.free(blob);

    const text_pass = try diff.compare(std.testing.io, std.testing.allocator, .text, expected_txt, actual_txt);
    defer diff.freeComparisonResult(std.testing.allocator, text_pass);
    try std.testing.expect(text_pass.ok);
    try std.testing.expectEqual(@as(usize, 0), text_pass.extra_lines.len);

    const json_pass = try diff.compare(std.testing.io, std.testing.allocator, .json, expected_json, expected_json);
    defer diff.freeComparisonResult(std.testing.allocator, json_pass);
    try std.testing.expect(json_pass.ok);

    const bytes_pass = try diff.compare(std.testing.io, std.testing.allocator, .bytes, blob, blob);
    defer diff.freeComparisonResult(std.testing.allocator, bytes_pass);
    try std.testing.expect(bytes_pass.ok);
    try std.testing.expect(std.mem.startsWith(u8, bytes_pass.extra_lines[0], "SHA256="));
}

test "artifact diff text results report identity without digest noise" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "a.txt", .data = "same\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "b.txt", .data = "same\n" });

    const a = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "a.txt");
    defer std.testing.allocator.free(a);
    const b = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "b.txt");
    defer std.testing.allocator.free(b);

    const result = try diff.compare(std.testing.io, std.testing.allocator, .text, a, b);
    defer diff.freeComparisonResult(std.testing.allocator, result);
    try std.testing.expect(result.ok);
    try std.testing.expectEqual(@as(usize, 0), result.extra_lines.len);
    try std.testing.expectEqual(diff.Mode.text, diff.Mode.parse("text").?);
}

test "artifact diff text mode shares stable missing-file reporting" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "actual.txt", .data = "present\n" });

    const missing = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "missing.txt");
    defer std.testing.allocator.free(missing);
    const actual_txt = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "actual.txt");
    defer std.testing.allocator.free(actual_txt);
    const other_missing = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "other-missing.txt");
    defer std.testing.allocator.free(other_missing);

    const missing_expected = try diff.compare(std.testing.io, std.testing.allocator, .text, missing, actual_txt);
    defer diff.freeComparisonResult(std.testing.allocator, missing_expected);
    try std.testing.expectEqualStrings("EXPECTED_EXISTS=False", missing_expected.extra_lines[0]);
    try std.testing.expectEqualStrings("ACTUAL_EXISTS=True", missing_expected.extra_lines[1]);

    const missing_actual = try diff.compare(std.testing.io, std.testing.allocator, .text, actual_txt, missing);
    defer diff.freeComparisonResult(std.testing.allocator, missing_actual);
    try std.testing.expectEqualStrings("EXPECTED_EXISTS=True", missing_actual.extra_lines[0]);
    try std.testing.expectEqualStrings("ACTUAL_EXISTS=False", missing_actual.extra_lines[1]);

    const missing_both = try diff.compare(std.testing.io, std.testing.allocator, .text, missing, other_missing);
    defer diff.freeComparisonResult(std.testing.allocator, missing_both);
    try std.testing.expectEqualStrings("EXPECTED_EXISTS=False", missing_both.extra_lines[0]);
    try std.testing.expectEqualStrings("ACTUAL_EXISTS=False", missing_both.extra_lines[1]);
}