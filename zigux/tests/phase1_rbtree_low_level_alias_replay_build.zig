const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_low_level_alias_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root_module.addImport("rbtree", rbtree_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-rbtree-low-level-alias-replay-tests",
        .root_module = replay_root_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const test_step = b.step(
        "phase1-rbtree-low-level-alias-replay",
        "Run the Phase 1 rbtree low-level alias replay.",
    );
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}
