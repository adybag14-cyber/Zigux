const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests_readme_path = b.option(
        []const u8,
        "tests-readme-path",
        "Path to the zigux/tests README packet to validate",
    ) orelse "zigux/tests/README.md";

    const contract_options = b.addOptions();
    contract_options.addOption([]const u8, "tests_readme_path", tests_readme_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_tests_readme_direct_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions(
        "phase1_tests_readme_direct_packet_contract_options",
        contract_options,
    );

    const tests = b.addTest(.{
        .name = "phase1-tests-readme-direct-packet-contract-test",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-tests-readme-direct-packet-contract",
        "Run the Phase 1 tests README direct packet contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 tests README direct packet contract");
    test_step.dependOn(&run_tests.step);
}
