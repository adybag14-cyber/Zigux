const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_phase2_bootstrap_workflow_routes_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-phase2-bootstrap-workflow-routes-contract",
        "Run the Phase 2 bootstrap workflow routes contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 2 bootstrap workflow routes contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
