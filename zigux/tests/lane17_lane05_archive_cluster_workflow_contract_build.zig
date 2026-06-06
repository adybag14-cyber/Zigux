const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_lane05_archive_cluster_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane17-lane05-archive-cluster-workflow-contract",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane17-lane05-archive-cluster-workflow-contract",
        "Guard the Lane 05 archive-helper workflow cluster in zigux-bootstrap.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Lane 05 archive-cluster workflow contract.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
