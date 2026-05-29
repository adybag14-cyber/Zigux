const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_bench_live_guard_hook_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane17-phase1-bench-live-guard-hook-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const named_step = b.step("lane17-phase1-bench-live-guard-hook-contract", "Run Lane 17 Phase 1 bench live guard hook contract tests");
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 bench live guard hook contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
