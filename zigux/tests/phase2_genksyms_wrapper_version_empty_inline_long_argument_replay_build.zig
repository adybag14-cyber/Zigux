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
        .root_source_file = b.path("phase2_genksyms_wrapper_version_empty_inline_long_argument_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("genksyms", genksyms_module);

    const tests = b.addTest(.{
        .name = "phase2-genksyms-wrapper-version-empty-inline-long-argument-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "phase2-genksyms-wrapper-version-empty-inline-long-argument-replay",
        "Run the focused Phase 2 genksyms wrapper version empty inline long-argument replay",
    );
    test_step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run the focused Phase 2 genksyms wrapper replay");
    default_step.dependOn(&run_tests.step);
    b.default_step.dependOn(default_step);
}
