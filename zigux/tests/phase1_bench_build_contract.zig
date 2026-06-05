const std = @import("std");

const bench_build = @embedFile("phase1_bench_build.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |idx| {
        count += 1;
        rest = rest[idx + needle.len ..];
    }
    try std.testing.expectEqual(expected, count);
}

test "Phase 1 bench build shard exposes executable bench and test routes" {
    try expectContains(bench_build, ".root_source_file = b.path(\"phase1_bench.zig\")");
    try expectContains(bench_build, ".name = \"phase1-bench\"");
    try expectContains(bench_build, "const run_bench = b.addRunArtifact(exe);");
    try expectContains(bench_build, "b.step(\n        \"bench\"");
    try expectContains(bench_build, "b.step(\n        \"test\"");
    try expectContains(bench_build, "bench_step.dependOn(&run_bench.step);");
    try expectContains(bench_build, "test_step.dependOn(&run_bench.step);");
    try expectContains(bench_build, "b.default_step.dependOn(test_step);");
    try expectCount(bench_build, "b.addRunArtifact(exe)", 1);
}

test "Phase 1 bench build shard keeps helper module graph closed" {
    const helper_modules = [_]struct {
        field: []const u8,
        path: []const u8,
    }{
        .{ .field = "find_bit_module", .path = "../../tools/lib/find_bit.zig" },
        .{ .field = "bitmap_module", .path = "../../tools/lib/bitmap.zig" },
        .{ .field = "string_module", .path = "../../tools/lib/string.zig" },
        .{ .field = "cmdline_module", .path = "../../tools/lib/cmdline.zig" },
        .{ .field = "hweight_module", .path = "../../tools/lib/hweight.zig" },
        .{ .field = "list_sort_module", .path = "../../tools/lib/list_sort.zig" },
        .{ .field = "rbtree_module", .path = "../../tools/lib/rbtree.zig" },
    };

    for (helper_modules) |module| {
        try expectContains(bench_build, module.field);
        try expectContains(bench_build, module.path);
    }

    try expectContains(bench_build, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
    try expectContains(bench_build, "string_module.addImport(\"cmdline\", cmdline_module);");
    try expectContains(bench_build, "root_module.addImport(\"bitmap\", bitmap_module);");
    try expectContains(bench_build, "root_module.addImport(\"find_bit\", find_bit_module);");
    try expectContains(bench_build, "root_module.addImport(\"hweight\", hweight_module);");
    try expectContains(bench_build, "root_module.addImport(\"list_sort\", list_sort_module);");
    try expectContains(bench_build, "root_module.addImport(\"rbtree\", rbtree_module);");
    try expectContains(bench_build, "root_module.addImport(\"string\", string_module);");
}

test "Phase 1 bench build shard stays scoped away from shared tests root" {
    try std.testing.expect(std.mem.indexOf(u8, bench_build, "addTest") == null);
    try std.testing.expect(std.mem.indexOf(u8, bench_build, "phase1-host-tools-smoke") == null);
    try std.testing.expect(std.mem.indexOf(u8, bench_build, "zigux/tests/build.zig") == null);
    try std.testing.expect(std.mem.indexOf(u8, bench_build, "check-phase1-bench.py") == null);
}
