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
    const exec_cmd_test_options = b.addOptions();
    exec_cmd_test_options.addOption([]const u8, "repo_root", b.pathFromRoot("../.."));
    exec_cmd_root_module.addImport("exec_cmd", exec_cmd_module);
    exec_cmd_root_module.addOptions("build_options", exec_cmd_test_options);

    const exec_cmd_tests = b.addTest(.{
        .name = "phase8-exec-cmd-tests",
        .root_module = exec_cmd_root_module,
    });
    const run_exec_cmd_tests = b.addRunArtifact(exec_cmd_tests);

    const test_step = b.step("test", "Run focused Phase 8 exec-cmd tests");
    test_step.dependOn(&run_exec_cmd_tests.step);
    b.default_step.dependOn(test_step);
}