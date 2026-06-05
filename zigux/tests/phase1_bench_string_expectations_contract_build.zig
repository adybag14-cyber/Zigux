const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench_string_expectations_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-bench-string-expectations-contract-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase1-bench-string-expectations-contract",
        "Run the Phase 1 bench string expectations contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run this build file's default test alias");
    test_step.dependOn(&run_tests.step);
}
