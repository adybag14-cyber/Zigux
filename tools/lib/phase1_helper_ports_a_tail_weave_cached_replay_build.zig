const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_path = b.option([]const u8, "bitmap-path", "Path to bitmap.zig") orelse "bitmap.zig";
    const find_bit_path = b.option([]const u8, "find-bit-path", "Path to find_bit.zig") orelse "find_bit.zig";
    const string_path = b.option([]const u8, "string-path", "Path to string.zig") orelse "string.zig";
    const rbtree_path = b.option([]const u8, "rbtree-path", "Path to rbtree.zig") orelse "rbtree.zig";

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path(find_bit_path),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path(bitmap_path),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);
    const string_module = b.createModule(.{
        .root_source_file = b.path(string_path),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path(rbtree_path),
        .target = target,
        .optimize = optimize,
    });

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_tail_weave_cached_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("bitmap", bitmap_module);
    test_module.addImport("find_bit", find_bit_module);
    test_module.addImport("string", string_module);
    test_module.addImport("rbtree", rbtree_module);

    const unit_tests = b.addTest(.{
        .root_module = test_module,
    });
    const run_tests = b.addRunArtifact(unit_tests);

    const route = b.step("phase1-helper-ports-a-tail-weave-cached-replay", "Run the Lane 06 tail weave cached helper replay");
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 06 tail weave cached helper replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
