const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_fixdep_manifest_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase2-closure-fixdep-manifest-contract-tests",
        .root_module = contract_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-closure-fixdep-manifest-contract",
        "Run the Phase 2 closure fixdep manifest contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 closure fixdep manifest contract tests");
    test_step.dependOn(&run_tests.step);
}
