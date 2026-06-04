const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const status_contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_status_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const status_contract_tests = b.addTest(.{
        .name = "phase2-closure-status-contract-tests",
        .root_module = status_contract_module,
    });
    const run_status_contract_tests = b.addRunArtifact(status_contract_tests);
    run_status_contract_tests.setCwd(b.path("../.."));

    const status_contract_step = b.step(
        "phase2-closure-status-contract",
        "Run the Phase 2 closure status contract",
    );
    status_contract_step.dependOn(&run_status_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 2 closure status contract tests");
    test_step.dependOn(&run_status_contract_tests.step);
}
