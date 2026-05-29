const std = @import("std");

const tests_build = @embedFile("build.zig");
const tests_readme = @embedFile("README.md");
const host_tools_smoke = @embedFile("phase1_host_tools_smoke.zig");

const HelperImport = struct {
    import_name: []const u8,
    source_path: []const u8,
    smoke_decl: []const u8,
};

const helper_imports = [_]HelperImport{
    .{ .import_name = "argv_split", .source_path = "../../tools/lib/argv_split.zig", .smoke_decl = "const argv_split = @import(\"argv_split\");" },
    .{ .import_name = "cmdline", .source_path = "../../tools/lib/cmdline.zig", .smoke_decl = "const cmdline = @import(\"cmdline\");" },
    .{ .import_name = "find_bit", .source_path = "../../tools/lib/find_bit.zig", .smoke_decl = "pub const find_bit = @import(\"find_bit\");" },
    .{ .import_name = "bitmap", .source_path = "../../tools/lib/bitmap.zig", .smoke_decl = "const bitmap = @import(\"bitmap\");" },
    .{ .import_name = "ctype", .source_path = "../../tools/lib/ctype.zig", .smoke_decl = "const ctype = @import(\"ctype\");" },
    .{ .import_name = "hweight", .source_path = "../../tools/lib/hweight.zig", .smoke_decl = "const hweight = @import(\"hweight\");" },
    .{ .import_name = "list_sort", .source_path = "../../tools/lib/list_sort.zig", .smoke_decl = "const list_sort = @import(\"list_sort\");" },
    .{ .import_name = "rbtree", .source_path = "../../tools/lib/rbtree.zig", .smoke_decl = "const rbtree = @import(\"rbtree\");" },
    .{ .import_name = "string", .source_path = "../../tools/lib/string.zig", .smoke_decl = "const string = @import(\"string\");" },
    .{ .import_name = "slab", .source_path = "../../tools/lib/slab.zig", .smoke_decl = "const slab = @import(\"slab\");" },
    .{ .import_name = "str_error_r", .source_path = "../../tools/lib/str_error_r.zig", .smoke_decl = "const str_error_r = @import(\"str_error_r\");" },
    .{ .import_name = "vsprintf", .source_path = "../../tools/lib/vsprintf.zig", .smoke_decl = "const vsprintf = @import(\"vsprintf\");" },
    .{ .import_name = "zalloc", .source_path = "../../tools/lib/zalloc.zig", .smoke_decl = "const zalloc = @import(\"zalloc\");" },
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAny(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return;
    }
    return error.TestUnexpectedResult;
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.TestUnexpectedResult;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.TestUnexpectedResult;
    try std.testing.expect(earlier_index < later_index);
}

fn count(haystack: []const u8, needle: []const u8) usize {
    var total: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        total += 1;
        rest = rest[index + needle.len ..];
    }
    return total;
}

fn boundedSection(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.TestUnexpectedResult;
    const tail = haystack[start_index..];
    const end_index = std.mem.indexOf(u8, tail, end) orelse return error.TestUnexpectedResult;
    return tail[0..end_index];
}

test "phase1 host tools smoke route stays visible in build and README" {
    try expectContains(tests_build, "fn addPhase1HostToolsSmoke(");
    try expectContainsAny(tests_build, &.{
        ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")",
        ".root_source_file = b.path(\\\"phase1_host_tools_smoke.zig\\\")",
    });
    try expectContainsAny(tests_build, &.{
        ".name = \"phase1-host-tools-smoke\"",
        ".name = \\\"phase1-host-tools-smoke\\\"",
    });
    try expectContainsAny(tests_build, &.{
        "\"phase1-host-tools-smoke\",",
        "\\\"phase1-host-tools-smoke\\\",",
    });
    try expectContainsAny(tests_build, &.{
        "\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\",",
        "\\\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\\\",",
    });
    try expectContains(tests_build, "phase1_step.dependOn(&phase1_host_tools_smoke.step);");

    try expectContains(tests_readme, "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectBefore(tests_readme, "`zigux/tests/build.zig`", "`zigux/tests/phase1_host_tools_smoke.zig`");
    try expectBefore(tests_readme, "`zigux/tests/phase1_host_tools_smoke.zig`", "`.github/workflows/zigux-bootstrap.yml`");
}

test "phase1 host tools smoke keeps the helper import inventory wired" {
    const build_section = try boundedSection(tests_build, "fn addPhase1HostToolsSmoke(", "fn addPhase1StringDirectAnchor(");

    try expectContainsAny(build_section, &.{
        "bitmap_module.addImport(\"find_bit\", find_bit_module);",
        "bitmap_module.addImport(\\\"find_bit\\\", find_bit_module);",
    });
    for (helper_imports) |helper| {
        try expectContains(build_section, helper.source_path);
        try expectContains(build_section, helper.import_name);
        try expectContains(host_tools_smoke, helper.smoke_decl);
    }

    try std.testing.expectEqual(helper_imports.len, count(build_section, "root_module.addImport("));
}

test "phase1 host tools smoke keeps fixture guard and behavior tests explicit" {
    try expectContains(host_tools_smoke, "const phase1_find_bit_fixture_guard = @import(\"phase1_find_bit_fixture_guard.zig\");");
    try expectContains(host_tools_smoke, "_ = phase1_find_bit_fixture_guard;");
    try expectContains(host_tools_smoke, "test \"phase1 host-tools smoke imports the live helper modules\"");
    try expectContains(host_tools_smoke, "test \"phase1 host-tools smoke exercises live helper behavior\"");
    try expectContains(host_tools_smoke, "try std.testing.expect(@hasDecl(find_bit, \"findFirstBit\"));");
    try expectContains(host_tools_smoke, "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));");
}
