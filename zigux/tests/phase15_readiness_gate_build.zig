const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const readiness_gate_module = b.createModule(.{
        .root_source_file = b.path("phase15_readiness_gate.zig"),
        .target = target,
        .optimize = optimize,
    });

    const readiness_gate_tests = b.addTest(.{
        .name = "phase15-readiness-gate-tests",
        .root_module = readiness_gate_module,
    });
    const run_readiness_gate_tests = b.addRunArtifact(readiness_gate_tests);
    run_readiness_gate_tests.setCwd(b.path("../.."));

    const readiness_gate_step = b.step("phase15-readiness-gate", "Run the focused Phase 15 readiness-gate test");
    readiness_gate_step.dependOn(&run_readiness_gate_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 readiness-gate test");
    test_step.dependOn(&run_readiness_gate_tests.step);
}
