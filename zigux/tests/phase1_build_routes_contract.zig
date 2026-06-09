const std = @import("std");

const build_file_path = "zigux/tests/build.zig";
const helper_build_file_path = "zigux/tests/phase1_helpers_build.zig";
const tests_readme_path = "zigux/tests/README.md";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(text: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, marker) != null);
}

fn expectNotContains(text: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, marker) == null);
}

fn expectInOrder(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, text, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, text, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "shared tests build keeps Phase 1 smoke and direct-anchor routes live" {
    const build_file = try readFile(std.testing.allocator, build_file_path);
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, "fn addPhase1HostToolsSmoke(");
    try expectContains(build_file, "fn addPhase1StringDirectAnchor(");
    try expectContains(build_file, "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);");
    try expectContains(build_file, "const phase1_string_direct_anchor = addPhase1StringDirectAnchor(b, target, optimize);");
    try expectContains(build_file, "b.step(\n        \"phase1-host-tools-smoke\",");
    try expectContains(build_file, "phase1_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectContains(build_file, "b.step(\n        \"phase1-string-direct-anchor\",");
    try expectContains(build_file, "phase1_string_direct_anchor_step.dependOn(&phase1_string_direct_anchor.step);");
    try expectNotContains(build_file, "b.step(\n        \"phase1\",");
    try expectInOrder(
        build_file,
        "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);",
        "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
    );
}

test "shared Phase 1 smoke route wires all current host helper modules" {
    const build_file = try readFile(std.testing.allocator, build_file_path);
    defer std.testing.allocator.free(build_file);

    const helpers = [_][]const u8{
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

    for (helpers) |helper| {
        const source_marker = try std.fmt.allocPrint(
            std.testing.allocator,
            ".root_source_file = b.path(\"../../tools/lib/{s}.zig\"),",
            .{helper},
        );
        defer std.testing.allocator.free(source_marker);
        try expectContains(build_file, source_marker);

        const import_marker = try std.fmt.allocPrint(
            std.testing.allocator,
            "root_module.addImport(\"{s}\", {s}_module);",
            .{ helper, helper },
        );
        defer std.testing.allocator.free(import_marker);
        try expectContains(build_file, import_marker);
    }

    try expectContains(build_file, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
    try expectContains(build_file, "string_module.addImport(\"cmdline\", cmdline_module);");
    try expectContains(build_file, ".name = \"phase1-host-tools-smoke\",");
}

test "focused helper replay and workflow markers stay aligned with tests README" {
    const helper_build_file = try readFile(std.testing.allocator, helper_build_file_path);
    defer std.testing.allocator.free(helper_build_file);
    const tests_readme = try readFile(std.testing.allocator, tests_readme_path);
    defer std.testing.allocator.free(tests_readme);
    const workflow = try readFile(std.testing.allocator, workflow_path);
    defer std.testing.allocator.free(workflow);

    try expectContains(helper_build_file, ".root_source_file = b.path(\"phase1_helpers.zig\"),");
    try expectContains(helper_build_file, ".name = \"phase1-helpers\",");
    try expectContains(helper_build_file, "b.step(\n        \"phase1-helpers\",");
    try expectContains(helper_build_file, "phase1_helpers.dependOn(&run_tests.step);");

    try expectContains(tests_readme, "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(tests_readme, "`zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`");
    try expectContains(workflow, "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
    try expectInOrder(
        workflow,
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    );
}
