const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane01_bootstrap_phase2_toolchain_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane01-bootstrap-phase2-toolchain-contract",
        "Run the Lane 01 Phase 2 toolchain roadmap contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 2 toolchain roadmap contract");
    test_step.dependOn(&run_tests.step);
}
