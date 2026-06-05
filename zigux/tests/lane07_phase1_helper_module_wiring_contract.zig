const std = @import("std");
const contract_options = @import("contract_options");

const default_tests_build_path = "zigux/tests/build.zig";

fn testsBuildPath() []const u8 {
    if (@hasDecl(contract_options, "tests_build_path")) {
        return contract_options.tests_build_path;
    }
    return default_tests_build_path;
}

fn readTestsBuild(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        testsBuildPath(),
        allocator,
        .limited(512 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative| {
        count += 1;
        offset += relative + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_pos = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_pos = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_pos < later_pos);
}

test "phase1 helper module sources stay wired through the shared tests build root" {
    const source = try readTestsBuild(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const helper_sources = [_][]const u8{
        ".root_source_file = b.path(\"../../tools/lib/argv_split.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/cmdline.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/bitmap.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/ctype.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/hweight.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/list_sort.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/rbtree.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/string.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/slab.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/str_error_r.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/vsprintf.zig\"),",
        ".root_source_file = b.path(\"../../tools/lib/zalloc.zig\"),",
    };

    for (helper_sources) |marker| {
        try requireOnce(source, marker);
    }
    try requireOnce(source, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),");
}

test "phase1 nested helper dependencies stay explicit before root smoke imports" {
    const source = try readTestsBuild(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const find_bit_source = ".root_source_file = b.path(\"../../tools/lib/find_bit.zig\"),";
    const bitmap_source = ".root_source_file = b.path(\"../../tools/lib/bitmap.zig\"),";
    const cmdline_source = ".root_source_file = b.path(\"../../tools/lib/cmdline.zig\"),";
    const string_source = ".root_source_file = b.path(\"../../tools/lib/string.zig\"),";
    const bitmap_dep = "bitmap_module.addImport(\"find_bit\", find_bit_module);";
    const string_dep = "string_module.addImport(\"cmdline\", cmdline_module);";
    const root_bitmap = "root_module.addImport(\"bitmap\", bitmap_module);";
    const root_string = "root_module.addImport(\"string\", string_module);";

    try requireOnce(source, bitmap_dep);
    try requireOnce(source, string_dep);
    try requireBefore(source, find_bit_source, bitmap_dep);
    try requireBefore(source, bitmap_source, bitmap_dep);
    try requireBefore(source, bitmap_dep, root_bitmap);
    try requireBefore(source, cmdline_source, string_dep);
    try requireBefore(source, string_source, string_dep);
    try requireBefore(source, string_dep, root_string);

    try requireAbsent(source, "bitmap_module.addImport(\"cmdline\"");
    try requireAbsent(source, "string_module.addImport(\"find_bit\"");
}

test "phase1 root smoke import roster stays exact and ordered" {
    const source = try readTestsBuild(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const root_imports = [_][]const u8{
        "root_module.addImport(\"argv_split\", argv_split_module);",
        "root_module.addImport(\"cmdline\", cmdline_module);",
        "root_module.addImport(\"find_bit\", find_bit_module);",
        "root_module.addImport(\"bitmap\", bitmap_module);",
        "root_module.addImport(\"ctype\", ctype_module);",
        "root_module.addImport(\"hweight\", hweight_module);",
        "root_module.addImport(\"list_sort\", list_sort_module);",
        "root_module.addImport(\"rbtree\", rbtree_module);",
        "root_module.addImport(\"string\", string_module);",
        "root_module.addImport(\"slab\", slab_module);",
        "root_module.addImport(\"str_error_r\", str_error_r_module);",
        "root_module.addImport(\"vsprintf\", vsprintf_module);",
        "root_module.addImport(\"zalloc\", zalloc_module);",
    };

    for (root_imports) |marker| {
        try requireOnce(source, marker);
    }
    for (root_imports[0 .. root_imports.len - 1], root_imports[1..]) |earlier, later| {
        try requireBefore(source, earlier, later);
    }

    try requireAbsent(source, "root_module.addImport(\"phase1_find_bit_fixture_guard\"");
    try requireAbsent(source, "root_module.addImport(\"tools/lib/");
}
