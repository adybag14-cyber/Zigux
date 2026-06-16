const std = @import("std");
const diff = @import("artifact_diff.zig");

fn tmpPath(allocator: std.mem.Allocator, tmp_sub_path: []const u8, name: []const u8) ![]const u8 {
    return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/{s}", .{ tmp_sub_path, name });
}

fn catalogContains(case_name: []const u8) bool {
    for (diff.self_test_case_names) |name| {
        if (std.mem.eql(u8, name, case_name)) return true;
    }
    return false;
}

test "artifact diff exposes bytes digest mode and legacy sha256 compatibility" {
    try std.testing.expectEqual(diff.Mode.bytes, diff.Mode.parse("sha256").?);
    try std.testing.expectEqualStrings("bytes", diff.Mode.bytes.name());
    try std.testing.expect(catalogContains("legacy_sha256_alias"));
}

test "artifact diff byte comparison emits stable digest markers" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "blob-a.bin", .data = "zigux-artifact-diff" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "blob-b.bin", .data = "zigux-artifact-diff" });

    const blob_a = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "blob-a.bin");
    defer std.testing.allocator.free(blob_a);
    const blob_b = try tmpPath(std.testing.allocator, tmp.sub_path[0..], "blob-b.bin");
    defer std.testing.allocator.free(blob_b);

    const pass = try diff.compare(std.testing.io, std.testing.allocator, .bytes, blob_a, blob_b);
    defer diff.freeComparisonResult(std.testing.allocator, pass);
    try std.testing.expect(pass.ok);
    try std.testing.expectEqual(@as(usize, 1), pass.extra_lines.len);
    try std.testing.expect(std.mem.startsWith(u8, pass.extra_lines[0], "SHA256="));

    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "blob-b.bin", .data = "zigux-artifact-DRIFT" });
    const drift = try diff.compare(std.testing.io, std.testing.allocator, .bytes, blob_a, blob_b);
    defer diff.freeComparisonResult(std.testing.allocator, drift);
    try std.testing.expect(!drift.ok);
    try std.testing.expectEqual(@as(usize, 2), drift.extra_lines.len);
    try std.testing.expect(std.mem.startsWith(u8, drift.extra_lines[0], "EXPECTED_SHA256="));
    try std.testing.expect(std.mem.startsWith(u8, drift.extra_lines[1], "ACTUAL_SHA256="));
}

test "artifact diff self-test catalog covers pass drift and missing byte cases" {
    const cases = [_][]const u8{
        "bytes_pass",
        "bytes_drift",
        "bytes_missing_expected",
        "bytes_missing_actual",
        "bytes_missing_both",
    };
    for (cases) |case_name| {
        try std.testing.expect(catalogContains(case_name));
    }

    const digest = try diff.sha256Hex(std.testing.allocator, "zigux-artifact-diff");
    defer std.testing.allocator.free(digest);
    try std.testing.expectEqualStrings("0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576", digest);
}