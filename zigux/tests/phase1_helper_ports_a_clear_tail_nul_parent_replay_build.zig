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

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_clear_tail_nul_parent_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("bitmap", bitmap_module);
    replay_module.addImport("find_bit", find_bit_module);
    replay_module.addImport("string", string_module);
    replay_module.addImport("rbtree", rbtree_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-helper-ports-a-clear-tail-nul-parent-replay-tests",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    run_replay_tests.setCwd(b.path("../.."));

    const replay_step = b.step(
        "phase1-helper-ports-a-clear-tail-nul-parent-replay",
        "Run the Phase 1 helper ports A clear-tail/NUL/parent replay",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 1 helper ports A clear-tail/NUL/parent replay");
    test_step.dependOn(&run_replay_tests.step);
}
