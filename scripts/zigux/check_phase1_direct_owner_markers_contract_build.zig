const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "path to check-phase1-direct-owner-markers.py",
    ) orelse "check-phase1-direct-owner-markers.py";

    const options = b.addOptions();
    options.addOption([]const u8, "source_path", source_path);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("check_phase1_direct_owner_markers_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("contract_options", options);

    const contract_tests = b.addTest(.{
        .name = "check-phase1-direct-owner-markers-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-phase1-direct-owner-markers-contract",
        "Run the Phase 1 direct-owner marker checker source contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run contract tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
