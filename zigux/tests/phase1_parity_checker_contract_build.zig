const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_parity_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-parity-checker-contract",
        "Run the Phase 1 parity-checker contract witness",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 parity-checker contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
