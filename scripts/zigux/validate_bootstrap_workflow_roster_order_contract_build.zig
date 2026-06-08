const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("validate_bootstrap_workflow_roster_order_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "validate-bootstrap-workflow-roster-order-contract-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "validate-bootstrap-workflow-roster-order-contract-test",
        "Run the focused validate-bootstrap workflow roster order contract",
    );
    test_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the focused validate-bootstrap workflow roster order contract");
    default_test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
