const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-tests-build-smoke-roster-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_tests_build_smoke_roster_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-tests-build-smoke-roster-contract",
        "Check the shared tests-root smoke/test roster for the Phase 1 helper harness gates",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 tests-build smoke roster contract");
    test_step.dependOn(&run_tests.step);
}
