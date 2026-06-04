const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_root_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_kconfig_bridge_count_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "phase2-closure-kconfig-bridge-count-contract-tests",
        .root_module = contract_root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase2-closure-kconfig-bridge-count-contract",
        "Run the Phase 2 closure kconfig bridge count contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_contract_tests.step);
}
