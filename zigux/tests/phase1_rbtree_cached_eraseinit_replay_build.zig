const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_cached_eraseinit_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("rbtree", rbtree_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-rbtree-cached-eraseinit-replay",
        .root_module = replay_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    const test_step = b.step("phase1-rbtree-cached-eraseinit-replay", "Run focused Phase 1 rbtree cached eraseInit replay");
    test_step.dependOn(&run_replay_tests.step);
}
