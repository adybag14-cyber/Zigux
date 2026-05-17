const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const base64_module = b.createModule(.{
        .root_source_file = b.path("../../lib/base64.zig"),
        .target = target,
        .optimize = optimize,
    });
    const base64_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_base64.zig"),
        .target = target,
        .optimize = optimize,
    });
    base64_root_module.addImport("base64", base64_module);

    const base64_tests = b.addTest(.{
        .name = "phase6-base64-tests",
        .root_module = base64_root_module,
    });
    const run_base64_tests = b.addRunArtifact(base64_tests);
    run_base64_tests.skip_foreign_checks = true;

    const test_step = b.step("test", "Run Phase 6 base64 helper tests");
    test_step.dependOn(&run_base64_tests.step);
}
