const std = @import("std");

const BuildContract = struct {
    helper_imports: []const []const u8,
    root_step: []const u8,
    root_test_name: []const u8,
    step_description: []const u8,
};

const phase1_helpers_build_contract = BuildContract{
    .helper_imports = &.{
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
    },
    .root_step = "phase1-helpers",
    .root_test_name = "phase1-helpers",
    .step_description = "Run the focused Phase 1 helper replay anchor from zigux/tests",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOne(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

test "phase 1 helpers build root keeps focused replay route" {
    const build_zig = try readRepoFile("zigux/tests/phase1_helpers_build.zig", 20 * 1024);
    defer std.testing.allocator.free(build_zig);

    try expectContains(build_zig, ".root_source_file = b.path(\"phase1_helpers.zig\")");
    try expectContains(build_zig, ".name = \"phase1-helpers\"");
    try expectContains(build_zig, "b.step(\n        \"phase1-helpers\"");
    try expectContains(build_zig, phase1_helpers_build_contract.step_description);
    try expectOne(build_zig, "const phase1_helpers = b.step(");
    try expectOne(build_zig, "phase1_helpers.dependOn(&run_tests.step);");
}

test "phase 1 helpers build root imports every parity helper" {
    const build_zig = try readRepoFile("zigux/tests/phase1_helpers_build.zig", 20 * 1024);
    defer std.testing.allocator.free(build_zig);

    for (phase1_helpers_build_contract.helper_imports) |import_name| {
        var module_line_buffer: [160]u8 = undefined;
        const module_line = try std.fmt.bufPrint(
            &module_line_buffer,
            "root_module.addImport(\"{s}\", {s}_module);",
            .{ import_name, import_name },
        );
        try expectOne(build_zig, module_line);

        var path_line_buffer: [160]u8 = undefined;
        const path_line = try std.fmt.bufPrint(
            &path_line_buffer,
            ".root_source_file = b.path(\"../../tools/lib/{s}.zig\")",
            .{import_name},
        );
        try expectContains(build_zig, path_line);
    }

    try expectOne(build_zig, "bitmap_module.addImport(\"find_bit\", find_bit_module);");
}

test "phase 1 parity checker knows the focused replay build file" {
    const checker = try readRepoFile("scripts/zigux/check-phase1-parity.py", 64 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "REPLAY_BUILD_REL = Path(\"zigux/tests/phase1_helpers_build.zig\")");
    try expectContains(checker, "EXPECTED_REPLAY_BUILD_MARKERS = (");
    try expectContains(checker, ".root_source_file = b.path(\"phase1_helpers.zig\"),");
    try expectContains(checker, ".name = \"phase1-helpers\",");
    try expectContains(checker, phase1_helpers_build_contract.step_description);
}
