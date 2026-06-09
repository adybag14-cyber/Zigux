const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_parity_review_anchor_fields_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "phase1-parity-review-anchor-fields-contract-tests",
        .root_module = contract_module,
    });
    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-parity-review-anchor-fields-contract",
        "Run the Phase 1 parity review-anchor fields source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 parity review-anchor fields source contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
