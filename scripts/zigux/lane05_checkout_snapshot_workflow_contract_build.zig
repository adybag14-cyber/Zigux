const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane05_checkout_snapshot_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "lane05-checkout-snapshot-workflow-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane05-checkout-snapshot-workflow-contract",
        "Run the Lane 05 checkout snapshot workflow contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 05 checkout snapshot workflow contract",
    );
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
