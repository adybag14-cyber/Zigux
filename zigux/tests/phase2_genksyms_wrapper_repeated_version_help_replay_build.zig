const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_wrapper_repeated_version_help_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const genksyms_module = b.createModule(.{
        .root_source_file = b.path("../../scripts/zigux/genksyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("genksyms", genksyms_module);

    const tests = b.addTest(.{
        .name = "phase2-genksyms-wrapper-repeated-version-help-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "test",
        "Run the focused Phase 2 genksyms wrapper repeated-version help replay.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
