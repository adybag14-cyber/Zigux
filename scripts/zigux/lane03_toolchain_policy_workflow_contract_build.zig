const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane03_toolchain_policy_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "lane03-toolchain-policy-workflow-contract",
        "Validate the Lane 03 toolchain policy, checker, bootstrap workflow, and Makefile route contract",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 03 toolchain policy workflow contract tests");
    test_step.dependOn(&run_tests.step);
}
