const std = @import("std");

pub fn build(b: *std.Build) void {
    const test_step = b.step("test", "Run the Phase 2 cross workflow concurrency contract");
    const contract_step = b.step("phase2-cross-workflow-concurrency-contract", "Run the Phase 2 cross workflow concurrency contract");

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_workflow_concurrency_contract.zig"),
            .target = b.graph.host,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    test_step.dependOn(&run_tests.step);
    contract_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
