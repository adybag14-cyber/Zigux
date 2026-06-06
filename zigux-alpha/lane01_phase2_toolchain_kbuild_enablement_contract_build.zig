const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane01_phase2_toolchain_kbuild_enablement_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane01-phase2-toolchain-kbuild-enablement-contract",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane01-phase2-toolchain-kbuild-enablement-contract",
        "Run the Lane 01 Phase 2 toolchain and kbuild roadmap contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Lane 01 Phase 2 toolchain and kbuild contract tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
