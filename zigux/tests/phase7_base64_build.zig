const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const base64_module = b.createModule(.{
        .root_source_file = b.path("../../lib/base64.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase7_base64.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("base64", base64_module);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase7-base64-test",
        "Run the Phase 7 base64 helper-local replay",
    );
    test_step.dependOn(&run_unit_tests.step);
}
