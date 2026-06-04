const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "lane01-release-planning-continuation-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_release_planning_continuation_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane01-release-planning-continuation-contract",
        "Run the Lane 01 release-planning continuation contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 01 release-planning continuation contract");
    test_step.dependOn(&run_tests.step);
}
