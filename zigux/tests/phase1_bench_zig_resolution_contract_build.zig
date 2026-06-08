const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench_zig_resolution_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase1-bench-zig-resolution-contract-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step("phase1-bench-zig-resolution-contract", "Run the Phase 1 bench Zig resolution contract.");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 bench Zig resolution contract tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
