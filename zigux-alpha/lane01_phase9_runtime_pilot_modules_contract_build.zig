const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane01_phase9_runtime_pilot_modules_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane01-phase9-runtime-pilot-modules-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane01-phase9-runtime-pilot-modules-contract",
        "Run the Lane 01 Phase 9 runtime pilot modules roadmap contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 9 runtime pilot modules roadmap contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(contract_step);
}
