const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exec_cmd_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/exec-cmd.zig"),
        .target = target,
        .optimize = optimize,
    });

    const exec_cmd_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_exec_cmd.zig"),
        .target = target,
        .optimize = optimize,
    });
    exec_cmd_root_module.addImport("exec_cmd", exec_cmd_module);

    const review_witness_tests = b.addTest(.{
        .name = "phase8-exec-cmd-tests",
        .root_module = exec_cmd_root_module,
    });
    const helper_unit_tests = b.addTest(.{
        .name = "phase8-exec-cmd-helper-tests",
        .root_module = exec_cmd_module,
    });

    const run_review_witness_tests = b.addRunArtifact(review_witness_tests);
    const run_helper_unit_tests = b.addRunArtifact(helper_unit_tests);
    // Run the reminder witness and the helper-local exec-cmd packet together.
    const test_step = b.step("test", "Run focused Phase 8 exec-cmd tests");
    test_step.dependOn(&run_review_witness_tests.step);
    test_step.dependOn(&run_helper_unit_tests.step);
}
