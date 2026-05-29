const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench_source_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "phase1-bench-source-contract",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-bench-source-contract",
        "Run the Phase 1 bench source topology contract from zigux/tests",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 bench source topology contract",
    );
    test_step.dependOn(&run_contract.step);
}
