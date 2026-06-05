const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests_build_path = b.option(
        []const u8,
        "tests-build-path",
        "Path to the zigux/tests/build.zig source checked by the contract",
    ) orelse "zigux/tests/build.zig";

    const options = b.addOptions();
    options.addOption([]const u8, "tests_build_path", tests_build_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane07_phase1_helper_module_wiring_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const tests = b.addTest(.{
        .name = "lane07-phase1-helper-module-wiring-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane07-phase1-helper-module-wiring-contract",
        "Validate Phase 1 helper module wiring in zigux/tests/build.zig",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 07 Phase 1 helper module wiring contract");
    test_step.dependOn(&run_tests.step);
}
