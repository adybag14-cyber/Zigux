const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_root_module = b.createModule(.{
        .root_source_file = b.path("lane01_phase7_runtime_leaf_libraries_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "lane01-phase7-runtime-leaf-libraries-contract-tests",
        .root_module = contract_root_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane01-phase7-runtime-leaf-libraries-contract",
        "Validate the Lane 01 Phase 7 runtime leaf libraries roadmap packet",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 7 runtime leaf libraries contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
