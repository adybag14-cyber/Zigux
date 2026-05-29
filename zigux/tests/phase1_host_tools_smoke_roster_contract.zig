const std = @import("std");

const build_zig = @embedFile("build.zig");

const Helper = struct {
    import_name: []const u8,
    module_name: []const u8,
    path: []const u8,
};

const phase1_helpers = [_]Helper{
    .{ .import_name = "argv_split", .module_name = "argv_split_module", .path = "../../tools/lib/argv_split.zig" },
    .{ .import_name = "cmdline", .module_name = "cmdline_module", .path = "../../tools/lib/cmdline.zig" },
    .{ .import_name = "find_bit", .module_name = "find_bit_module", .path = "../../tools/lib/find_bit.zig" },
    .{ .import_name = "bitmap", .module_name = "bitmap_module", .path = "../../tools/lib/bitmap.zig" },
    .{ .import_name = "ctype", .module_name = "ctype_module", .path = "../../tools/lib/ctype.zig" },
    .{ .import_name = "hweight", .module_name = "hweight_module", .path = "../../tools/lib/hweight.zig" },
    .{ .import_name = "list_sort", .module_name = "list_sort_module", .path = "../../tools/lib/list_sort.zig" },
    .{ .import_name = "rbtree", .module_name = "rbtree_module", .path = "../../tools/lib/rbtree.zig" },
    .{ .import_name = "string", .module_name = "string_module", .path = "../../tools/lib/string.zig" },
    .{ .import_name = "slab", .module_name = "slab_module", .path = "../../tools/lib/slab.zig" },
    .{ .import_name = "str_error_r", .module_name = "str_error_r_module", .path = "../../tools/lib/str_error_r.zig" },
    .{ .import_name = "vsprintf", .module_name = "vsprintf_module", .path = "../../tools/lib/vsprintf.zig" },
    .{ .import_name = "zalloc", .module_name = "zalloc_module", .path = "../../tools/lib/zalloc.zig" },
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn phase1SmokeSection() ![]const u8 {
    const start = std.mem.indexOf(u8, build_zig, "fn addPhase1HostToolsSmoke(") orelse return error.MissingPhase1SmokeStart;
    const end = std.mem.indexOfPos(u8, build_zig, start, "fn addPhase1StringDirectAnchor(") orelse return error.MissingPhase1SmokeEnd;
    try std.testing.expect(start < end);
    return build_zig[start..end];
}

test "phase1 host-tools smoke keeps every helper path and root import" {
    const section = try phase1SmokeSection();

    try expectContains(section, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")");
    for (phase1_helpers) |helper| {
        var path_marker: [160]u8 = undefined;
        const path_needles = try std.fmt.bufPrint(
            &path_marker,
            ".root_source_file = b.path(\"{s}\")",
            .{helper.path},
        );
        try expectContains(section, path_needles);

        var import_marker: [120]u8 = undefined;
        const import_needles = try std.fmt.bufPrint(
            &import_marker,
            "root_module.addImport(\"{s}\", {s})",
            .{ helper.import_name, helper.module_name },
        );
        try expectContains(section, import_needles);
        try expectBefore(section, path_needles, import_needles);
    }
}

test "bitmap remains wired through the shared find_bit helper module" {
    const section = try phase1SmokeSection();

    try expectContains(section, "bitmap_module.addImport(\"find_bit\", find_bit_module)");
    try expectBefore(
        section,
        "bitmap_module.addImport(\"find_bit\", find_bit_module)",
        "root_module.addImport(\"bitmap\", bitmap_module)",
    );
}

test "shared smoke and test steps still depend on phase1 host-tools smoke" {
    try expectContains(build_zig, "const phase1_step = b.step(\n        \"phase1-host-tools-smoke\"");
    try expectContains(build_zig, "Run the shared Phase 1 host-tools smoke anchor from zigux/tests");
    try expectContains(build_zig, "phase1_step.dependOn(&phase1_host_tools_smoke.step)");
    try expectContains(build_zig, "smoke_step.dependOn(&phase1_host_tools_smoke.step)");
    try expectContains(build_zig, "test_step.dependOn(&phase1_host_tools_smoke.step)");
    try expectBefore(build_zig, "const phase1_step = b.step(", "const smoke_step = b.step(");
    try expectBefore(build_zig, "const smoke_step = b.step(", "const test_step = b.step(");
}
