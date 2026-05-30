const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_phase1_bench_runtime_diagnostics_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "check-phase1-bench-runtime-diagnostics-contract",
        "Run the Phase 1 bench checker runtime diagnostics contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 bench checker runtime diagnostics contract",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
