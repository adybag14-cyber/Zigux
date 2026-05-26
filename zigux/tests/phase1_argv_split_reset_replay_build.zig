const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_argv_split_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root_module.addImport("argv_split", argv_split_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-argv-split-reset-replay-tests",
        .root_module = replay_root_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-argv-split-reset-replay",
        "Run the Phase 1 argv_split reset replay",
    );
    replay_step.dependOn(&run_replay_tests.step);
}
