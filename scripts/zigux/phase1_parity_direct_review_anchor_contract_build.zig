const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_parity_direct_review_anchor_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase1-parity-direct-review-anchor-contract-tests",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase1-parity-direct-review-anchor-contract",
        "Run the Phase 1 parity direct-review-anchor contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 1 parity direct-review-anchor contract tests");
    test_step.dependOn(&run_unit_tests.step);
}
