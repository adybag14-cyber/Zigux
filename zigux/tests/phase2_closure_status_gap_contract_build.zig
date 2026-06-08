const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const repo_root = b.option([]const u8, "repo-root", "Repository root for runtime file reads") orelse ".";

    const test_step = b.step("phase2-closure-status-gap-contract", "Run the Phase 2 closure status/gap contract");
    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_closure_status_gap_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(.{ .cwd_relative = repo_root });
    test_step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run all tests");
    default_step.dependOn(test_step);
    b.default_step.dependOn(test_step);
}
