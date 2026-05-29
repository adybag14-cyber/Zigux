const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_shared_smoke_gate_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-shared-smoke-gate-contract-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const gate_step = b.step(
        "phase1-shared-smoke-gate-contract",
        "Validate the shared tests-root Phase 1 host-tools smoke gate contract",
    );
    gate_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 shared smoke gate contract",
    );
    test_step.dependOn(&run_tests.step);
}
