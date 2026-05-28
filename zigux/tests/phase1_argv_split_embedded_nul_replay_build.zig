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
        .root_source_file = b.path("phase1_argv_split_embedded_nul_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("argv_split", argv_split_module);

    const tests = b.addTest(.{
        .name = "phase1-argv-split-embedded-nul-replay-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-argv-split-embedded-nul-replay",
        "Run the focused Phase 1 argv_split embedded-NUL replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the focused Phase 1 argv_split embedded-NUL replay",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
