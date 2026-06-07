const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const validator_path = b.option(
        []const u8,
        "validator-path",
        "Path to scripts/zigux/validate-phase1-closure.py",
    ) orelse "scripts/zigux/validate-phase1-closure.py";

    const options = b.addOptions();
    options.addOption([]const u8, "validator_path", validator_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_root_surface_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("config", options);

    const tests = b.addTest(.{
        .name = "phase1-closure-root-surface-contract",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-closure-root-surface-contract",
        "Run the Phase 1 closure root-surface contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure root-surface contract");
    test_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(&run_contract_tests.step);
}
