const std = @import("std");

const build_source = @embedFile("phase1_bench_build.zig");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, build_source, needle) != null);
}

fn expectOccurs(needle: []const u8, expected: usize) !void {
    var cursor: usize = 0;
    var count: usize = 0;
    while (std.mem.indexOf(u8, build_source[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectOrdered(markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const offset = std.mem.indexOf(u8, build_source[cursor..], marker) orelse return error.MissingBuildMarker;
        cursor += offset + marker.len;
    }
}

test "phase1 bench build gate keeps the current helper module packet" {
    const helper_paths = [_][]const u8{
        ".root_source_file = b.path(\"phase1_bench.zig\")",
        ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\")",
        ".root_source_file = b.path(\"../../tools/lib/bitmap.zig\")",
        ".root_source_file = b.path(\"../../tools/lib/string.zig\")",
        ".root_source_file = b.path(\"../../tools/lib/hweight.zig\")",
        ".root_source_file = b.path(\"../../tools/lib/list_sort.zig\")",
        ".root_source_file = b.path(\"../../tools/lib/rbtree.zig\")",
    };
    for (helper_paths) |path_marker| {
        try expectContains(path_marker);
    }

    const imports = [_][]const u8{
        "bitmap_module.addImport(\"find_bit\", find_bit_module);",
        "root_module.addImport(\"bitmap\", bitmap_module);",
        "root_module.addImport(\"find_bit\", find_bit_module);",
        "root_module.addImport(\"hweight\", hweight_module);",
        "root_module.addImport(\"list_sort\", list_sort_module);",
        "root_module.addImport(\"rbtree\", rbtree_module);",
        "root_module.addImport(\"string\", string_module);",
    };
    for (imports) |import_marker| {
        try expectContains(import_marker);
    }
}

test "phase1 bench build gate keeps bench, test, and default step wiring" {
    try expectContains(".name = \"phase1-bench\"");
    try expectContains("const run_bench = b.addRunArtifact(exe);");
    try expectOccurs("b.step(", 2);
    try expectOccurs("&run_bench.step", 2);

    try expectOrdered(&[_][]const u8{
        "const run_bench = b.addRunArtifact(exe);",
        "const bench_step = b.step(",
        "\"bench\"",
        "bench_step.dependOn(&run_bench.step);",
        "const test_step = b.step(",
        "\"test\"",
        "test_step.dependOn(&run_bench.step);",
        "b.default_step.dependOn(test_step);",
    });
}
