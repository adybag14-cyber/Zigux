const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_scripts_readme_kconfig_bridge_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-scripts-readme-kconfig-bridge-packet-contract-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase2-scripts-readme-kconfig-bridge-packet-contract",
        "Run the Phase 2 scripts README kconfig bridge packet contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the Phase 2 scripts README kconfig bridge packet contract.");
    default_test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(default_test_step);
}
