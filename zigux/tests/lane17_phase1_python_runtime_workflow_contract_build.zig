const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_python_runtime_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane17-phase1-python-runtime-workflow-contract",
        "Run the Lane 17 Phase 1 Python runtime workflow contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 Python runtime workflow contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
