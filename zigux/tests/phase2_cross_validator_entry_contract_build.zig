const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_validator_entry_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase2-cross-validator-entry-contract-tests",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase2-cross-validator-entry-contract",
        "Run the Phase 2 cross validator-entry contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run focused Phase 2 cross validator-entry contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
