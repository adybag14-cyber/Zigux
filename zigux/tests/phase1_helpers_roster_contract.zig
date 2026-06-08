const std = @import("std");

const helper_names = [_][]const u8{
    "argv_split",
    "cmdline",
    "bitmap",
    "ctype",
    "find_bit",
    "hweight",
    "list_sort",
    "rbtree",
    "slab",
    "str_error_r",
    "string",
    "vsprintf",
    "zalloc",
};

const helper_paths = [_][]const u8{
    "../../tools/lib/argv_split.zig",
    "../../tools/lib/cmdline.zig",
    "../../tools/lib/bitmap.zig",
    "../../tools/lib/ctype.zig",
    "../../tools/lib/find_bit.zig",
    "../../tools/lib/hweight.zig",
    "../../tools/lib/list_sort.zig",
    "../../tools/lib/rbtree.zig",
    "../../tools/lib/slab.zig",
    "../../tools/lib/str_error_r.zig",
    "../../tools/lib/string.zig",
    "../../tools/lib/vsprintf.zig",
    "../../tools/lib/zalloc.zig",
};

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
    const rest = haystack[first + needle.len ..];
    try std.testing.expect(std.mem.indexOf(u8, rest, needle) == null);
}

fn quotedImportName(name: []const u8) ![64]u8 {
    var buffer: [64]u8 = undefined;
    const rendered = try std.fmt.bufPrint(&buffer, "const {s} = @import(\"{s}\");", .{ name, name });
    var out: [64]u8 = undefined;
    @memcpy(out[0..rendered.len], rendered);
    out[rendered.len] = 0;
    return out;
}

test "phase1 helper replay imports the committed helper roster exactly once" {
    const source = try readRepoFile("zigux/tests/phase1_helpers.zig");
    defer std.testing.allocator.free(source);

    for (helper_names) |name| {
        const marker_storage = try quotedImportName(name);
        const marker = std.mem.sliceTo(&marker_storage, 0);
        try expectExactlyOnce(source, marker);
    }
    try expectExactlyOnce(source, "@embedFile(\"fixtures/phase1_helpers.json\")");
    try expectContains(source, "test \"phase 1 helper ports match committed parity fixture\"");
    try expectContains(source, ".ignore_unknown_fields = true");
}

test "phase1 helper fixture keeps one top-level packet per helper" {
    const fixture = try readRepoFile("zigux/tests/fixtures/phase1_helpers.json");
    defer std.testing.allocator.free(fixture);

    for (helper_names) |name| {
        var key_buffer: [64]u8 = undefined;
        const key = try std.fmt.bufPrint(&key_buffer, "\"{s}\"", .{name});
        try expectContains(fixture, key);
    }
    try expectContains(fixture, "\"inclusive_boundary_next\"");
    try expectContains(fixture, "\"tail_clamped_last\"");
    try expectContains(fixture, "\"next_match_terminal_null\"");
    try expectContains(fixture, "\"replace_char_cstr_bytes\"");
}

test "phase1 helper build wrapper wires the same helper roster" {
    const build_file = try readRepoFile("zigux/tests/phase1_helpers_build.zig");
    defer std.testing.allocator.free(build_file);

    for (helper_names, helper_paths) |name, path| {
        var source_marker_buffer: [96]u8 = undefined;
        const source_marker = try std.fmt.bufPrint(
            &source_marker_buffer,
            ".root_source_file = b.path(\"{s}\"),",
            .{path},
        );
        try expectContains(build_file, source_marker);

        var import_marker_buffer: [96]u8 = undefined;
        const import_marker = try std.fmt.bufPrint(
            &import_marker_buffer,
            "root_module.addImport(\"{s}\", {s}_module);",
            .{ name, name },
        );
        try expectContains(build_file, import_marker);
    }

    try expectContains(build_file, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
    try expectContains(build_file, ".name = \"phase1-helpers\",");
    try expectContains(build_file, "\"Run the focused Phase 1 helper replay anchor from zigux/tests\"");
}
