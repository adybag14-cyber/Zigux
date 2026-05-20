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

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_root = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_tail_iter_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root.addImport("bitmap", bitmap_module);
    replay_root.addImport("find_bit", find_bit_module);
    replay_root.addImport("string", string_module);
    replay_root.addImport("rbtree", rbtree_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-helper-ports-a-tail-iter-replay-tests",
        .root_module = replay_root,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-helper-ports-a-tail-iter-replay",
        "Run the Phase 1 helper ports A tail/iterator replay",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 helper ports A tail/iterator replay");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}
