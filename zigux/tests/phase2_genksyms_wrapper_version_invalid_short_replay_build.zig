const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const genksyms_wrapper_module = b.createModule(.{
        .root_source_file = b.path("../../scripts/zigux/genksyms.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_wrapper_version_invalid_short_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("genksyms_wrapper", genksyms_wrapper_module);

    const tests = b.addTest(.{
        .name = "phase2-genksyms-wrapper-version-invalid-short-replay-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("test", "Run the Phase 2 genksyms wrapper version-before-invalid-short replay");
    test_step.dependOn(&run_tests.step);
}
