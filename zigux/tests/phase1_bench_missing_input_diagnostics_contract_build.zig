const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench_missing_input_diagnostics_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase1-bench-missing-input-diagnostics-contract-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step("phase1-bench-missing-input-diagnostics-contract", "Run the Phase 1 bench missing input diagnostics contract.");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 bench missing input diagnostics contract tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
