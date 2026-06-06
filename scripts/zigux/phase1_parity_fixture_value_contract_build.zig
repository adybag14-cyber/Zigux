const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_parity_fixture_value_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-parity-fixture-value-contract",
        "Run the Phase 1 parity fixture-value source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 parity fixture-value contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
