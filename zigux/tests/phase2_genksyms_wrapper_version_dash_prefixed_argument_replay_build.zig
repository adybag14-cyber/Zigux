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
        .root_source_file = b.path("phase2_genksyms_wrapper_version_dash_prefixed_argument_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("genksyms", genksyms_module);

    const tests = b.addTest(.{
        .name = "phase2-genksyms-wrapper-version-dash-prefixed-argument-replay-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase2-genksyms-wrapper-version-dash-prefixed-argument-replay",
        "Run the Phase 2 genksyms wrapper version dash-prefixed argument replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run focused Phase 2 genksyms wrapper replay tests");
    test_step.dependOn(&run_tests.step);
}
