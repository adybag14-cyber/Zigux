const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_hweight_split_fold_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root_module.addImport("hweight", hweight_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-hweight-split-fold-replay-tests",
        .root_module = replay_root_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    run_replay_tests.setCwd(b.path("../.."));

    const replay_step = b.step(
        "phase1-hweight-split-fold-replay",
        "Run the Phase 1 hweight split-fold replay",
    );
    replay_step.dependOn(&run_replay_tests.step);
}
