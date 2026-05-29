const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench_checker_selftest_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase1-bench-checker-selftest-contract",
        .root_module = root_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-bench-checker-selftest-contract",
        "Run the focused Phase 1 bench checker self-test contract from zigux/tests",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step(
        "test",
        "Run the focused Phase 1 bench checker self-test contract from zigux/tests",
    );
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(test_step);
}
