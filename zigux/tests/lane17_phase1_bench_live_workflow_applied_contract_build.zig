const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const applied_contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_live_workflow_applied_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_applied_contract_tests = b.addRunArtifact(applied_contract_tests);

    const contract_step = b.step(
        "lane17-phase1-bench-live-workflow-applied-contract",
        "Run the Lane 17 Phase 1 bench live workflow applied-state contract.",
    );
    contract_step.dependOn(&run_applied_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 bench live workflow applied-state contract.");
    test_step.dependOn(contract_step);

    b.default_step.dependOn(test_step);
}
