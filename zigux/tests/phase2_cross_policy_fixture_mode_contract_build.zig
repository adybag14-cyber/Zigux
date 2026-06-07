const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_policy_fixture_mode_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const named_step = b.step(
        "phase2-cross-policy-fixture-mode-contract",
        "Run the Lane 21 Phase 2 cross policy/fixture mode contract",
    );
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 21 Phase 2 cross policy/fixture mode contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
