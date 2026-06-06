const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_checker_issue_group_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = root_module,
    });

    const run = b.addRunArtifact(tests);
    const route = b.step("phase2-cross-checker-issue-group-contract", "Run the Phase 2 cross checker issue-group contract");
    route.dependOn(&run.step);

    const test_step = b.step("test", "Run the Phase 2 cross checker issue-group contract");
    test_step.dependOn(&run.step);
}
