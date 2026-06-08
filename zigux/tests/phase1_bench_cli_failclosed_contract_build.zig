const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_bench_cli_failclosed_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step("phase1-bench-cli-failclosed-contract", "Run Phase 1 bench CLI and fail-closed output contract");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Phase 1 bench CLI and fail-closed output contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
