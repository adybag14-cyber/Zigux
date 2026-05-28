const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const genksyms_module = b.createModule(.{
        .root_source_file = b.path("../../scripts/zigux/genksyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_wrapper_version_missing_long_reference_argument_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("genksyms", genksyms_module);

    const replay_tests = b.addTest(.{
        .name = "phase2-genksyms-wrapper-version-missing-long-reference-replay-tests",
        .root_module = root_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const test_step = b.step("test", "Run focused Phase 2 genksyms wrapper version missing long reference replay tests.");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}
