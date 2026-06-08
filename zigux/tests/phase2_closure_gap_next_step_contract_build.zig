const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_gap_next_step_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step(
        "phase2-closure-gap-next-step-contract",
        "Run the Phase 2 closure gap next-step contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 2 closure gap next-step contract tests.",
    );
    test_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(&run_contract_tests.step);
}
