const std = @import("std");
const build_root = @import("build_root_options").build_root;

const helper_imports = [_][]const u8{
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

fn expectRouteAfterSmokeFactory(haystack: []const u8) !void {
    const factory = "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);";
    const route = "const phase1_step = b.step(\n        \"phase1-host-tools-smoke\",";
    const factory_index = std.mem.indexOf(u8, haystack, factory) orelse return error.MissingSmokeFactory;
    const route_index = std.mem.indexOf(u8, haystack, route) orelse return error.MissingSmokeRoute;
    try std.testing.expect(route_index > factory_index);
}

fn expectAggregateDependency(haystack: []const u8, step_name: []const u8) !void {
    const step_header = try std.fmt.allocPrint(std.testing.allocator, "const {s}_step = b.step(", .{step_name});
    defer std.testing.allocator.free(step_header);
    const step_index = std.mem.indexOf(u8, haystack, step_header) orelse return error.MissingAggregateStep;
    const rest = haystack[step_index..];
    const dependency = ".dependOn(&phase1_host_tools_smoke.step);";
    try expectContains(rest, dependency);
}

fn expectHelperModuleWiring(haystack: []const u8, name: []const u8) !void {
    const module_decl = try std.fmt.allocPrint(std.testing.allocator, "const {s}_module = b.createModule", .{name});
    defer std.testing.allocator.free(module_decl);
    const source_path = try std.fmt.allocPrint(std.testing.allocator, ".root_source_file = b.path(\"../../tools/lib/{s}.zig\")", .{name});
    defer std.testing.allocator.free(source_path);
    const import_decl = try std.fmt.allocPrint(std.testing.allocator, "root_module.addImport(\"{s}\", {s}_module);", .{ name, name });
    defer std.testing.allocator.free(import_decl);

    try expectContains(haystack, module_decl);
    try expectContains(haystack, source_path);
    try expectContains(haystack, import_decl);
}

fn expectPhase1BuildRootContract(haystack: []const u8) !void {
    try expectContains(haystack, "fn addPhase1HostToolsSmoke(");
    try expectContains(haystack, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")");
    try expectContains(haystack, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
    try expectContains(haystack, "string_module.addImport(\"cmdline\", cmdline_module);");

    for (helper_imports) |name| {
        try expectHelperModuleWiring(haystack, name);
    }

    try expectRouteAfterSmokeFactory(haystack);
    try expectContains(haystack, "Run the shared Phase 1 host-tools smoke anchor from zigux/tests");
    try expectAggregateDependency(haystack, "smoke");
    try expectAggregateDependency(haystack, "test");
}

const sample_current_build_root =
    \\fn addPhase1HostToolsSmoke(b: *std.Build) void {
    \\    const root_module = b.createModule(.{
    \\        .root_source_file = b.path("phase1_host_tools_smoke.zig"),
    \\    });
    \\    const argv_split_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/argv_split.zig") });
    \\    const cmdline_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/cmdline.zig") });
    \\    const find_bit_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/find_bit.zig") });
    \\    const bitmap_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/bitmap.zig") });
    \\    const ctype_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/ctype.zig") });
    \\    const hweight_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/hweight.zig") });
    \\    const list_sort_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/list_sort.zig") });
    \\    const rbtree_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/rbtree.zig") });
    \\    const string_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/string.zig") });
    \\    const slab_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/slab.zig") });
    \\    const str_error_r_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/str_error_r.zig") });
    \\    const vsprintf_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/vsprintf.zig") });
    \\    const zalloc_module = b.createModule(.{ .root_source_file = b.path("../../tools/lib/zalloc.zig") });
    \\    bitmap_module.addImport("find_bit", find_bit_module);
    \\    string_module.addImport("cmdline", cmdline_module);
    \\    root_module.addImport("argv_split", argv_split_module);
    \\    root_module.addImport("cmdline", cmdline_module);
    \\    root_module.addImport("find_bit", find_bit_module);
    \\    root_module.addImport("bitmap", bitmap_module);
    \\    root_module.addImport("ctype", ctype_module);
    \\    root_module.addImport("hweight", hweight_module);
    \\    root_module.addImport("list_sort", list_sort_module);
    \\    root_module.addImport("rbtree", rbtree_module);
    \\    root_module.addImport("string", string_module);
    \\    root_module.addImport("slab", slab_module);
    \\    root_module.addImport("str_error_r", str_error_r_module);
    \\    root_module.addImport("vsprintf", vsprintf_module);
    \\    root_module.addImport("zalloc", zalloc_module);
    \\}
    \\pub fn build(b: *std.Build) void {
    \\    const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);
    \\    const phase1_step = b.step(
    \\        "phase1-host-tools-smoke",
    \\        "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",
    \\    );
    \\    phase1_step.dependOn(&phase1_host_tools_smoke.step);
    \\    const smoke_step = b.step("smoke", "Run the currently live shared survey anchors from zigux/tests");
    \\    smoke_step.dependOn(&phase1_host_tools_smoke.step);
    \\    const test_step = b.step("test", "Run the shared Zigux tests-root survey smoke");
    \\    test_step.dependOn(&phase1_host_tools_smoke.step);
    \\}
;

test "sample build root satisfies the phase 1 smoke harness contract" {
    try expectPhase1BuildRootContract(sample_current_build_root);
}

test "repository build root keeps the phase 1 smoke harness wired" {
    try expectPhase1BuildRootContract(build_root);
}
