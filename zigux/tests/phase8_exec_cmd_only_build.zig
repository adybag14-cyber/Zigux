const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exec_cmd_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_exec_cmd.zig"),
        .target = target,
        .optimize = optimize,
    });

    const review_witness_tests = b.addTest(.{
        .name = "phase8-exec-cmd-tests",
        .root_module = exec_cmd_root_module,
    });

    const run_review_witness_tests = b.addRunArtifact(review_witness_tests);
    // Run the phase 8 exec-cmd review witness without importing the retired helper path.
    const test_step = b.step("test", "Run focused Phase 8 exec-cmd tests");
    test_step.dependOn(&run_review_witness_tests.step);
}
