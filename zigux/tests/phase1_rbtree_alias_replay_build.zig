const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_root = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_alias_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root.addImport("rbtree", rbtree_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-rbtree-alias-replay-tests",
        .root_module = replay_root,
    });

    const run_replay = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-rbtree-alias-replay",
        "Run the Phase 1 rbtree Linux-style alias replay.",
    );
    replay_step.dependOn(&run_replay.step);
}
