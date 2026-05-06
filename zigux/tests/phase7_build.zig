const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const repo_root = b.path("../..");

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

    const argv_split_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_argv_split_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    rbtree_root_module.addImport("rbtree", rbtree_module);

    const rbtree_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_rbtree_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_survey_tests = b.addTest(.{
        .name = "phase7-rbtree-survey-tests",
        .root_module = rbtree_survey_root_module,
    });
    const run_rbtree_survey_tests = b.addRunArtifact(rbtree_survey_tests);

    const string_helpers_tests = b.addTest(.{
        .name = "phase7-string-helpers-tests",
        .root_module = string_helpers_root_module,
    });
    const run_string_helpers_tests = b.addRunArtifact(string_helpers_tests);
    const string_helpers_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/string_helpers_sample.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_helpers_sample_module.addImport("string_helpers", string_helpers_module);
    const string_helpers_sample_tests = b.addTest(.{
        .name = "phase7-string-helpers-sample-tests",
        .root_module = string_helpers_sample_module,
    });
    const run_string_helpers_sample_tests = b.addRunArtifact(string_helpers_sample_tests);
    const string_helpers_sample_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_string_helpers_sample_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_helpers_sample_survey_root_module.addImport("string_helpers", string_helpers_module);
    const string_helpers_sample_survey_tests = b.addTest(.{
        .name = "phase7-string-helpers-sample-survey-tests",
        .root_module = string_helpers_sample_survey_root_module,
    });
    const run_string_helpers_sample_survey_tests = b.addRunArtifact(string_helpers_sample_survey_tests);
    run_string_helpers_sample_survey_tests.setCwd(repo_root);

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

    const argv_split_survey_tests = b.addTest(.{
        .name = "phase7-argv-split-survey-tests",
        .root_module = argv_split_survey_root_module,
    });
    const run_argv_split_survey_tests = b.addRunArtifact(argv_split_survey_tests);

    const rbtree_tests = b.addTest(.{
        .name = "phase7-rbtree-tests",
        .root_module = rbtree_root_module,
    });
    const run_rbtree_tests = b.addRunArtifact(rbtree_tests);

    const test_step = b.step("test", "Run Phase 7 runtime helper tests");
    test_step.dependOn(&run_string_helpers_tests.step);
    test_step.dependOn(&run_string_helpers_sample_tests.step);
    test_step.dependOn(&run_string_helpers_sample_survey_tests.step);
    test_step.dependOn(&run_cmdline_tests.step);
    test_step.dependOn(&run_argv_split_tests.step);
    test_step.dependOn(&run_argv_split_survey_tests.step);
    test_step.dependOn(&run_rbtree_tests.step);
    test_step.dependOn(&run_rbtree_survey_tests.step);
}
