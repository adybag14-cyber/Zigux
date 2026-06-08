const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_self_test_case_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-closure-self-test-case-contract",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-closure-self-test-case-contract",
        "Run the Phase 1 closure validator self-test case contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Phase 1 closure validator self-test case contract tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
