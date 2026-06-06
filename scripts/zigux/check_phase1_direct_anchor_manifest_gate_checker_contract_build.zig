const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "path to check-phase1-direct-anchor-manifest-gate.py",
    ) orelse "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py";

    const options = b.addOptions();
    options.addOption([]const u8, "source_path", source_path);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_phase1_direct_anchor_manifest_gate_checker_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addOptions("contract_options", options);

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "check-phase1-direct-anchor-manifest-gate-checker-contract",
        "Validate the Phase 1 direct-anchor manifest gate checker source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the direct-anchor manifest gate checker contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
