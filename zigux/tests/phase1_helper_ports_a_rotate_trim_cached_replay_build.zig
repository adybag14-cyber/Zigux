const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_module.addImport("cmdline", cmdline_module);
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_rotate_trim_cached_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap", bitmap_module);
    root_module.addImport("find_bit", find_bit_module);
    root_module.addImport("string", string_module);
    root_module.addImport("rbtree", rbtree_module);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-a-rotate-trim-cached-replay-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-helper-ports-a-rotate-trim-cached-replay",
        "Run the Lane 06 Phase 1 helper ports A rotate trim cached replay.",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 06 Phase 1 helper ports A rotate trim cached replay tests.",
    );
    test_step.dependOn(&run_tests.step);
}
