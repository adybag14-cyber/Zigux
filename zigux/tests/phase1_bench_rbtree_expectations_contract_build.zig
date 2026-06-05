const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench_rbtree_expectations_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase1-bench-rbtree-expectations-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-bench-rbtree-expectations-contract",
        "Run Phase 1 bench rbtree expectations contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 1 bench rbtree expectations contract");
    test_step.dependOn(&run_tests.step);
}
