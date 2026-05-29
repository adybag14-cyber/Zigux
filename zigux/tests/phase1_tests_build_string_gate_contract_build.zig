const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-tests-build-string-gate-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_tests_build_string_gate_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-tests-build-string-gate-contract",
        "Run the Phase 1 tests build host-tools plus string direct-anchor contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 tests build string-gate contract");
    test_step.dependOn(&run_tests.step);
}
