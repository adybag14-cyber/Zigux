const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_argv_split_ownership_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("argv_split", argv_split_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-argv-split-ownership-replay-tests",
        .root_module = replay_module,
    });

    const replay_step = b.step(
        "phase1-argv-split-ownership-replay",
        "Run the Lane 07 argv_split ownership replay tests.",
    );
    replay_step.dependOn(&b.addRunArtifact(replay_tests).step);
    b.default_step.dependOn(replay_step);
}
