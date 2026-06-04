const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase15_deep_core_blocker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase15-deep-core-blocker-contract-tests",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase15-deep-core-blocker-contract",
        "Run the Phase 15 deep-core blocker survey contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 15 deep-core blocker survey contract");
    test_step.dependOn(&run_contract_tests.step);
}
