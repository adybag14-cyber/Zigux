const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane01_phase15_full_parity_governance_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane01-phase15-full-parity-governance-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane01-phase15-full-parity-governance-contract",
        "Run Lane 01 Phase 15 full-parity governance roadmap contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 01 Phase 15 full-parity governance roadmap contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
