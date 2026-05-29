const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_bench_live_guard_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "lane17-phase1-bench-live-guard-contract-tests",
        .root_module = module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-bench-live-guard-contract",
        "Run the Lane 17 Phase 1 bench live workflow guard contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 bench live workflow guard contract");
    test_step.dependOn(&run_tests.step);
}
