const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane01_phase4_validation_rollback_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane01-phase4-validation-rollback-contract",
        .root_module = contract_module,
    });

    const run_contract = b.addRunArtifact(contract_tests);
    const contract_step = b.step("lane01-phase4-validation-rollback-contract", "Run the Lane 01 Phase 4 validation rollback roadmap contract");
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 4 validation rollback roadmap contract");
    test_step.dependOn(&run_contract.step);
}
