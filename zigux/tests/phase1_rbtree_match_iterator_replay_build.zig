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
        .root_source_file = b.path("phase1_rbtree_match_iterator_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("rbtree", rbtree_module);

    const tests = b.addTest(.{
        .name = "phase1-rbtree-match-iterator-replay-tests",
        .root_module = replay_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const replay_step = b.step(
        "phase1-rbtree-match-iterator-replay",
        "Run the Phase 1 rbtree match iterator replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 rbtree match iterator replay");
    test_step.dependOn(&run_tests.step);
}
