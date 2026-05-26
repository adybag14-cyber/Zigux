const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_argv_split_ascii_whitespace_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("argv_split", argv_split_module);

    const tests = b.addTest(.{
        .name = "phase1-argv-split-ascii-whitespace-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase1-argv-split-ascii-whitespace-replay",
        "Run the Phase 1 argv_split ASCII whitespace replay",
    );
    replay_step.dependOn(&run_tests.step);
}
