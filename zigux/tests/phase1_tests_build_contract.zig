const std = @import("std");

const build_zig = @embedFile("build.zig");

const phase1_helper_modules = [_][]const u8{
    "argv_split",
    "cmdline",
    "find_bit",
    "bitmap",
    "ctype",
    "hweight",
    "list_sort",
    "rbtree",
    "string",
    "slab",
    "str_error_r",
    "vsprintf",
    "zalloc",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |found| {
        count += 1;
        offset = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "phase 1 shared tests build keeps host-tools smoke root wired" {
    try expectContains(build_zig, "fn addPhase1HostToolsSmoke(");
    try expectContains(build_zig, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")");
    try expectContains(build_zig, ".name = \"phase1-host-tools-smoke\"");
    try expectContains(build_zig, "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);");

    try expectContains(build_zig, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
    inline for (phase1_helper_modules) |module_name| {
        try expectContains(build_zig, ".root_source_file = b.path(\"../../tools/lib/" ++ module_name ++ ".zig\")");
        try expectContains(build_zig, "root_module.addImport(\"" ++ module_name ++ "\", " ++ module_name ++ "_module);");
    }
}

test "phase 1 shared tests build exposes focused phase1 steps" {
    try expectContains(build_zig, "const phase1_step = b.step(");
    try expectContains(build_zig, "\"phase1-host-tools-smoke\",");
    try expectContains(build_zig, "\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\",");
    try expectContains(build_zig, "phase1_step.dependOn(&phase1_host_tools_smoke.step);");

    try expectContains(build_zig, "const phase1_string_direct_anchor_step = b.step(");
    try expectContains(build_zig, "\"phase1-string-direct-anchor\",");
    try expectContains(build_zig, "\"Run the shared Phase 1 string strlcat direct-anchor packet from zigux/tests\",");
    try expectContains(build_zig, "phase1_string_direct_anchor_step.dependOn(&phase1_string_direct_anchor.step);");
}

test "phase 1 shared tests build remains part of aggregate smoke and test steps" {
    try expectContains(build_zig, "const smoke_step = b.step(");
    try expectContains(build_zig, "const test_step = b.step(");
    try expectCount(build_zig, ".dependOn(&phase1_host_tools_smoke.step);", 3);
    try expectContains(build_zig, "smoke_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectContains(build_zig, "test_step.dependOn(&phase1_host_tools_smoke.step);");
}
