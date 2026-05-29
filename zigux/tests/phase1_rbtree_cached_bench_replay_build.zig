const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_cached_bench_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    root_module.addImport("rbtree", rbtree_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-rbtree-cached-bench-replay",
        .root_module = root_module,
    });
    const run_replay = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-rbtree-cached-bench-replay",
        "Run the focused Phase 1 rbtree cached bench replay from zigux/tests",
    );
    replay_step.dependOn(&run_replay.step);

    const test_step = b.step(
        "test",
        "Run the focused Phase 1 rbtree cached bench replay from zigux/tests",
    );
    test_step.dependOn(&run_replay.step);

    b.default_step.dependOn(test_step);
}
