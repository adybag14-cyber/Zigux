const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const validator_pair_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_validator_pair_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const validator_pair_tests = b.addTest(.{
        .name = "phase2-closure-validator-pair-contract-tests",
        .root_module = validator_pair_module,
    });

    const run_validator_pair_tests = b.addRunArtifact(validator_pair_tests);

    const contract_step = b.step("phase2-closure-validator-pair-contract", "Run the Phase 2 closure validator-pair contract");
    contract_step.dependOn(&run_validator_pair_tests.step);

    b.default_step.dependOn(contract_step);
}
