const std = @import("std");

pub fn build(b: *std.Build) void {
    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_alignment_policy_swap_contract.zig"),
            .target = b.graph.host,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-cross-alignment-policy-swap-contract",
        "Run the Lane 21 Phase 2 cross alignment policy swap contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 21 Phase 2 cross alignment policy swap contract tests.");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(test_step);
}
