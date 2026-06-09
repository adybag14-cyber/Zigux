const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_workflow_matrix_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-cross-workflow-matrix-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-cross-workflow-matrix-contract",
        "Run the Phase 2 cross workflow matrix contract from zigux/tests",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 2 cross workflow matrix contract test alias",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
