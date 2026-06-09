const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const command_failure_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_bench_command_failure_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(command_failure_tests);

    const contract_step = b.step("phase1-bench-command-failure-contract", "Run Phase 1 bench command failure diagnostic contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 1 bench command failure diagnostic contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}