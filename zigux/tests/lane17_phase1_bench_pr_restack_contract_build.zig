const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "lane17-phase1-bench-pr-restack-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_pr_restack_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-bench-pr-restack-contract",
        "Validate Lane 17 Phase 1 bench workflow PR restack hygiene",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 bench workflow PR restack contract");
    test_step.dependOn(&run_tests.step);
}
