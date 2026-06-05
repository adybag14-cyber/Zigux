const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_archive_setup_ladder_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const named_step = b.step(
        "lane05-archive-setup-ladder-workflow-contract",
        "Validate the Lane 05 pinned Zig archive setup workflow ladder contract",
    );
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 05 archive setup ladder workflow contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
