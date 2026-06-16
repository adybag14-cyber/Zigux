const std = @import("std");
const diff = @import("artifact_diff.zig");

const self_test_cases = diff.self_test_case_names;

test "artifact diff CLI mode parsing remains stable" {
    try std.testing.expectEqual(diff.Mode.text, diff.Mode.parse("text").?);
    try std.testing.expectEqual(diff.Mode.json, diff.Mode.parse("json").?);
    try std.testing.expectEqual(diff.Mode.bytes, diff.Mode.parse("bytes").?);
    try std.testing.expectEqual(diff.Mode.bytes, diff.Mode.parse("sha256").?);
    try std.testing.expect(diff.Mode.parse("yaml") == null);
}

test "artifact diff mode dispatch keeps text json bytes and legacy sha256" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "a.txt", .data = "x\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "b.txt", .data = "x\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "a.json", .data = "{}\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "b.json", .data = "{}\n" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "a.bin", .data = "blob" });
    try tmp.dir.writeFile(std.testing.io, .{ .sub_path = "b.bin", .data = "blob" });

    const a_txt = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/a.txt", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(a_txt);
    const b_txt = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/b.txt", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(b_txt);
    const a_json = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/a.json", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(a_json);
    const b_json = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/b.json", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(b_json);
    const a_bin = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/a.bin", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(a_bin);
    const b_bin = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/b.bin", .{tmp.sub_path[0..]});
    defer std.testing.allocator.free(b_bin);

    const text_pass = try diff.compare(std.testing.io, std.testing.allocator, .text, a_txt, b_txt);
    defer diff.freeComparisonResult(std.testing.allocator, text_pass);
    try std.testing.expect(text_pass.ok);

    const json_pass = try diff.compare(std.testing.io, std.testing.allocator, .json, a_json, b_json);
    defer diff.freeComparisonResult(std.testing.allocator, json_pass);
    try std.testing.expect(json_pass.ok);

    const bytes_pass = try diff.compare(std.testing.io, std.testing.allocator, .bytes, a_bin, b_bin);
    defer diff.freeComparisonResult(std.testing.allocator, bytes_pass);
    try std.testing.expect(bytes_pass.ok);

    const bytes_alias = try diff.compare(std.testing.io, std.testing.allocator, .bytes, a_bin, a_bin);
    defer diff.freeComparisonResult(std.testing.allocator, bytes_alias);
    try std.testing.expect(bytes_alias.ok);
}

test "artifact diff self-test catalog covers parser and digest failure gates" {
    for (self_test_cases, 0..) |case, index| {
        for (self_test_cases[0..index]) |previous| {
            try std.testing.expect(!std.mem.eql(u8, case, previous));
        }
    }
    try std.testing.expectEqual(@as(usize, 23), self_test_cases.len);

    const digest = try diff.sha256Hex(std.testing.allocator, "zigux-artifact-diff");
    defer std.testing.allocator.free(digest);
    try std.testing.expectEqualStrings("0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576", digest);

    const drift_digest = try diff.sha256Hex(std.testing.allocator, "zigux-artifact-DRIFT");
    defer std.testing.allocator.free(drift_digest);
    try std.testing.expectEqualStrings("bfc83f8f1f4369ce3cfabfdff0699ae3bf7a15b89f1702b690e56c6f35f1ee94", drift_digest);
}