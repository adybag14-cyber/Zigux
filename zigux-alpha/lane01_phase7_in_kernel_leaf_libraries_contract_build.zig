const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "lane01-phase7-in-kernel-leaf-libraries-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_phase7_in_kernel_leaf_libraries_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane01-phase7-in-kernel-leaf-libraries-contract",
        "Run the Lane 01 Phase 7 in-kernel leaf-libraries roadmap contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Lane 01 Phase 7 in-kernel leaf-libraries contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
