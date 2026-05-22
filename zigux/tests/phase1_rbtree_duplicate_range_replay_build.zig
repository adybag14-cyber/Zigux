const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_duplicate_range_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("rbtree", rbtree_module);

    const replay = b.addTest(.{
        .name = "phase1-rbtree-duplicate-range-replay",
        .root_module = root_module,
    });

    const run_replay = b.addRunArtifact(replay);

    const replay_step = b.step(
        "phase1-rbtree-duplicate-range-replay",
        "Run the standalone Lane 07 rbtree duplicate-range replay",
    );
    replay_step.dependOn(&run_replay.step);
}
