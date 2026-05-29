const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_tests_readme_workflow_gates_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-tests-readme-workflow-gates-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase1-tests-readme-workflow-gates-contract",
        "Run the Phase 1 tests README workflow gate contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 tests README workflow gate contract.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
