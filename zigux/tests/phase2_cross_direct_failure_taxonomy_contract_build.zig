const std = @import("std");

pub fn build(b: *std.Build) void {
    const test_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_direct_failure_taxonomy_contract.zig"),
        .target = b.graph.host,
    });
    const tests = b.addTest(.{ .root_module = test_module });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-cross-direct-failure-taxonomy-contract",
        "Run the Phase 2 direct cross checker failure taxonomy contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 direct cross checker failure taxonomy contract.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(contract_step);
}
