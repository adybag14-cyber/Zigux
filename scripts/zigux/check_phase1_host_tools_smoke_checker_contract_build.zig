const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "Path to scripts/zigux/check-phase1-host-tools-smoke.py",
    ) orelse "scripts/zigux/check-phase1-host-tools-smoke.py";

    const options = b.addOptions();
    options.addOption([]const u8, "source_path", source_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_phase1_host_tools_smoke_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const contract_tests = b.addTest(.{
        .name = "check-phase1-host-tools-smoke-checker-contract-tests",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-phase1-host-tools-smoke-checker-contract",
        "Validate the Phase 1 host-tools smoke checker source contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 host-tools smoke checker contract tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
