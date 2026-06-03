const std = @import("std");

const build_zig = @embedFile("build.zig");

const HelperImport = struct {
    import_name: []const u8,
    module_name: []const u8,
    source_path: []const u8,
};

const phase1_helpers = [_]HelperImport{
    .{ .import_name = "argv_split", .module_name = "argv_split_module", .source_path = "../../tools/lib/argv_split.zig" },
    .{ .import_name = "cmdline", .module_name = "cmdline_module", .source_path = "../../tools/lib/cmdline.zig" },
    .{ .import_name = "find_bit", .module_name = "find_bit_module", .source_path = "../../tools/lib/find_bit.zig" },
    .{ .import_name = "bitmap", .module_name = "bitmap_module", .source_path = "../../tools/lib/bitmap.zig" },
    .{ .import_name = "ctype", .module_name = "ctype_module", .source_path = "../../tools/lib/ctype.zig" },
    .{ .import_name = "hweight", .module_name = "hweight_module", .source_path = "../../tools/lib/hweight.zig" },
    .{ .import_name = "list_sort", .module_name = "list_sort_module", .source_path = "../../tools/lib/list_sort.zig" },
    .{ .import_name = "rbtree", .module_name = "rbtree_module", .source_path = "../../tools/lib/rbtree.zig" },
    .{ .import_name = "string", .module_name = "string_module", .source_path = "../../tools/lib/string.zig" },
    .{ .import_name = "slab", .module_name = "slab_module", .source_path = "../../tools/lib/slab.zig" },
    .{ .import_name = "str_error_r", .module_name = "str_error_r_module", .source_path = "../../tools/lib/str_error_r.zig" },
    .{ .import_name = "vsprintf", .module_name = "vsprintf_module", .source_path = "../../tools/lib/vsprintf.zig" },
    .{ .import_name = "zalloc", .module_name = "zalloc_module", .source_path = "../../tools/lib/zalloc.zig" },
};

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, build_zig, needle) != null);
}

fn expectNotContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, build_zig, needle) == null);
}

fn expectFormattedContains(comptime fmt: []const u8, args: anytype) !void {
    const needle = try std.fmt.allocPrint(std.testing.allocator, fmt, args);
    defer std.testing.allocator.free(needle);
    try expectContains(needle);
}

test "phase1 host-tools smoke wires every helper source into a module" {
    try expectContains("fn addPhase1HostToolsSmoke(");
    try expectContains(".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")");
    try expectContains(".name = \"phase1-host-tools-smoke\"");

    for (phase1_helpers) |helper| {
        try expectFormattedContains("const {s} = b.createModule", .{helper.module_name});
        try expectFormattedContains(".root_source_file = b.path(\"{s}\")", .{helper.source_path});
    }
}

test "phase1 host-tools smoke root imports the complete helper roster" {
    for (phase1_helpers) |helper| {
        try expectFormattedContains("root_module.addImport(\"{s}\", {s});", .{
            helper.import_name,
            helper.module_name,
        });
    }
}

test "phase1 host-tools smoke preserves helper-local dependency imports" {
    try expectContains("bitmap_module.addImport(\"find_bit\", find_bit_module);");
    try expectContains("string_module.addImport(\"cmdline\", cmdline_module);");
}

test "phase1 host-tools smoke remains the default phase1 route" {
    try expectContains("const phase1_step = b.step(");
    try expectContains("\"phase1-host-tools-smoke\"");
    try expectContains("phase1_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectContains("smoke_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectContains("test_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectNotContains("smoke_step.dependOn(&phase1_string_direct_anchor.step);");
    try expectNotContains("test_step.dependOn(&phase1_string_direct_anchor.step);");
}
