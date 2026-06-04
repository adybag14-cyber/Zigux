const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase4_test_fsmount_shared_root_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase4-test-fsmount-shared-root-contract-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase4-test-fsmount-shared-root-contract",
        "Run the Phase 4 test_fsmount shared-root harness contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 4 test_fsmount shared-root harness contract");
    test_step.dependOn(&run_tests.step);
}
