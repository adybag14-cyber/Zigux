const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_validator_handoff_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-validator-handoff-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-validator-handoff-contract",
        "Validate the Phase 1 closure-validator handoff and workflow smoke route",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 validator handoff contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
