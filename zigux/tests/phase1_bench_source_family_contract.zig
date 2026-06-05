const std = @import("std");

const bench_source_path = "zigux/tests/phase1_bench.zig";

const bitmap_source_markers = [_][]const u8{
    "const iterations_bitmap_weight: u64 = 20000;",
    "const iterations_bitmap_window: u64 = 20000;",
    "fn bitmapWeightBench() struct { checksum: u64 } {",
    "fn bitmapWindowBench() struct { checksum: u64 } {",
    "checksum +%= @intCast(bitmap.weight(&map, nbits));",
    "checksum +%= @intCast(bitmap.weightedOr(&dst, &lhs, &rhs, nbits));",
    "checksum +%= @intCast(bitmap.weightedXor(&dst, &lhs, &rhs, nbits));",
    "const bitmap_weight_result = bitmapWeightBench();",
    "const bitmap_window_result = bitmapWindowBench();",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS={d}\\\\n\", .{iterations_bitmap_weight});",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS={d}\\\\n\", .{iterations_bitmap_window});",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={d}\\\\n\", .{bitmap_weight_result.checksum});",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={d}\\\\n\", .{bitmap_window_result.checksum});",
};

const string_source_markers = [_][]const u8{
    "const iterations_string: u64 = 40000;",
    "fn stringBench() !struct { checksum: u64 } {",
    "const enabled = try string.strtobool(if (even) \"on\" else \"0\");",
    "var trim_buf = [_]u8{ ' ', '\\t', 'h', 'i', ' ', '\\n' };",
    "const trimmed = string.trimSpaces(&trim_buf);",
    "const parsed = string.memparse(if (even) \"64K rest\" else \"-17 tail\");",
    "string.memchrInv(\"aaaaXaaa\", 'a')",
    "string.memchrInv(\"bbbb\", 'b');",
    "const string_result = try stringBench();",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_STRING_ITERATIONS={d}\\\\n\", .{iterations_string});",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_STRING_CHECKSUM={d}\\\\n\", .{string_result.checksum});",
};

const hweight_source_markers = [_][]const u8{
    "const iterations_hweight: u64 = 100000;",
    "fn hweightBench() struct { checksum: u64 } {",
    "checksum +%= hweight.swHweight8(0xf0);",
    "checksum +%= hweight.swHweight16(0xf0f0);",
    "checksum +%= hweight.swHweight32(0xf0f0_f0f0);",
    "checksum +%= hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0);",
    "checksum +%= @intCast(hweight.hweightLong(0xf0f0));",
    "const hweight_result = hweightBench();",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_HWEIGHT_ITERATIONS={d}\\\\n\", .{iterations_hweight});",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_HWEIGHT_CHECKSUM={d}\\\\n\", .{hweight_result.checksum});",
};

const list_sort_source_markers = [_][]const u8{
    "const iterations_list_sort: u64 = 1000;",
    "fn listSortBench() struct { checksum: u64 } {",
    "const cmp = struct {",
    "fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {",
    "list_sort.listAddTail(&entry.node, &head);",
    "list_sort.listSort(null, &head, cmp);",
    "checksum +%= @intCast(entry.ordinal);",
    "const list_sort_result = listSortBench();",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_LIST_SORT_ITERATIONS={d}\\\\n\", .{iterations_list_sort});",
    "try stdout_writer.interface.print(\"PHASE1_BENCH_LIST_SORT_CHECKSUM={d}\\\\n\", .{list_sort_result.checksum});",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle);
    try std.testing.expect(first != null);
    const after_first = haystack[first.? + needle.len ..];
    try std.testing.expect(std.mem.indexOf(u8, after_first, needle) == null);
}

fn requireMarkerSet(source: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try requireContains(source, marker);
    }
}

test "phase1 bitmap bench source keeps helper operations and output keys" {
    const allocator = std.testing.allocator;
    const source = try readRepoFile(allocator, bench_source_path);
    defer allocator.free(source);

    try requireMarkerSet(source, &bitmap_source_markers);
    try requireContainsOnce(source, "fn bitmapWeightBench() struct { checksum: u64 } {");
    try requireContainsOnce(source, "fn bitmapWindowBench() struct { checksum: u64 } {");
    try requireContainsOnce(source, "const bitmap_weight_result = bitmapWeightBench();");
    try requireContainsOnce(source, "const bitmap_window_result = bitmapWindowBench();");
}

test "phase1 string bench source keeps parsing and scan operations" {
    const allocator = std.testing.allocator;
    const source = try readRepoFile(allocator, bench_source_path);
    defer allocator.free(source);

    try requireMarkerSet(source, &string_source_markers);
    try requireContainsOnce(source, "fn stringBench() !struct { checksum: u64 } {");
    try requireContainsOnce(source, "const string_result = try stringBench();");
    try requireContainsOnce(source, "PHASE1_BENCH_STRING_CHECKSUM={d}\\\\n");
}

test "phase1 hweight bench source keeps width coverage and output keys" {
    const allocator = std.testing.allocator;
    const source = try readRepoFile(allocator, bench_source_path);
    defer allocator.free(source);

    try requireMarkerSet(source, &hweight_source_markers);
    try requireContainsOnce(source, "fn hweightBench() struct { checksum: u64 } {");
    try requireContainsOnce(source, "const hweight_result = hweightBench();");
    try requireContainsOnce(source, "PHASE1_BENCH_HWEIGHT_CHECKSUM={d}\\\\n");
}

test "phase1 list_sort bench source keeps stable duplicate-order surface" {
    const allocator = std.testing.allocator;
    const source = try readRepoFile(allocator, bench_source_path);
    defer allocator.free(source);

    try requireMarkerSet(source, &list_sort_source_markers);
    try requireContainsOnce(source, "fn listSortBench() struct { checksum: u64 } {");
    try requireContainsOnce(source, "const list_sort_result = listSortBench();");
    try requireContainsOnce(source, "PHASE1_BENCH_LIST_SORT_CHECKSUM={d}\\\\n");
}
