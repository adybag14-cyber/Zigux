const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_helpers_module = b.createModule(.{
        .root_source_file = b.path("../../lib/string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_helpers_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_helpers_root_module.addImport("string_helpers", string_helpers_module);

    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    cmdline_root_module.addImport("cmdline", cmdline_module);

    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    argv_split_root_module.addImport("argv_split", argv_split_module);

    const string_helpers_tests = b.addTest(.{
        .name = "phase7-string-helpers-tests",
        .root_module = string_helpers_root_module,
    });
    const run_string_helpers_tests = b.addRunArtifact(string_helpers_tests);

    const cmdline_tests = b.addTest(.{
        .name = "phase7-cmdline-tests",
        .root_module = cmdline_root_module,
    });
    const run_cmdline_tests = b.addRunArtifact(cmdline_tests);

    const argv_split_tests = b.addTest(.{
        .name = "phase7-argv-split-tests",
        .root_module = argv_split_root_module,
    });
    const run_argv_split_tests = b.addRunArtifact(argv_split_tests);

    const test_step = b.step("test", "Run Phase 7 runtime helper tests");
    test_step.dependOn(&run_string_helpers_tests.step);
    test_step.dependOn(&run_cmdline_tests.step);
    test_step.dependOn(&run_argv_split_tests.step);
}
