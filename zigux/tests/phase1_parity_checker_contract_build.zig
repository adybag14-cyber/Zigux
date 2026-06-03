const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_parity_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = root_module,
        .name = "phase1-parity-checker-contract",
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-parity-checker-contract",
        "Run the Phase 1 parity checker contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the default Phase 1 parity checker contract tests");
    test_step.dependOn(&run_tests.step);
}
