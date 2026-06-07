const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_setup_failure_handoff_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "lane05-setup-failure-handoff-contract",
        "Run the Lane 05 setup failure and GITHUB_PATH handoff contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 05 setup failure and GITHUB_PATH handoff contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
