const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const smoke_path = b.option(
        []const u8,
        "smoke-path",
        "Path to the Phase 1 host-tools smoke source",
    ) orelse "phase1_host_tools_smoke.zig";
    const tests_build_path = b.option(
        []const u8,
        "tests-build-path",
        "Path to the shared zigux/tests build root",
    ) orelse "build.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "smoke_path", smoke_path);
    options.addOption([]const u8, "tests_build_path", tests_build_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke_test_block_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const contract_tests = b.addTest(.{
        .name = "phase1-host-tools-smoke-test-block-contract",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-host-tools-smoke-test-block-contract",
        "Verify the Phase 1 host-tools smoke test-block and gate structure",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools smoke test-block contract");
    test_step.dependOn(&run_contract_tests.step);
}
