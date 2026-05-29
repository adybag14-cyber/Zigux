const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase15-lane01-commit-train-handoff-contract-test",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase15_lane01_commit_train_handoff_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase15-lane01-commit-train-handoff-contract",
        "Run the Lane 01 commit-train handoff contract guard",
    );
    test_step.dependOn(&run_tests.step);
}
