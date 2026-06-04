const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase2-cross-direct-checker-issue-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_direct_checker_issue_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "phase2-cross-direct-checker-issue-contract",
        "Run the Phase 2 cross direct checker issue-code contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 2 cross direct checker issue-code contract",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(named_step);
}
