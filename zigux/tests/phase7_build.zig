const std = @import("std");

fn createImportedTestRoot(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    root_path: []const u8,
    import_name: []const u8,
    import_path: []const u8,
) *std.Build.Module {
    const imported_module = b.createModule(.{
        .root_source_file = b.path(import_path),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_path),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport(import_name, imported_module);
    return root_module;
}

fn createStandaloneTestRoot(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    root_path: []const u8,
) *std.Build.Module {
    return b.createModule(.{
        .root_source_file = b.path(root_path),
        .target = target,
        .optimize = optimize,
    });
}

fn addTestRun(
    b: *std.Build,
    name: []const u8,
    root_module: *std.Build.Module,
    cwd: ?std.Build.LazyPath,
) *std.Build.Step.Run {
    const tests = b.addTest(.{
        .name = name,
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);
    if (cwd) |path| {
        run.setCwd(path);
    }
    return run;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const repo_root = b.path("../..");

    const string_helpers_root_module = createImportedTestRoot(
        b,
        target,
        optimize,
        "phase7_string_helpers.zig",
        "string_helpers",
        "../../lib/string_helpers.zig",
    );
    const string_helpers_survey_root_module = createStandaloneTestRoot(
        b,
        target,
        optimize,
        "phase7_string_helpers_survey.zig",
    );
    const string_helpers_sample_boundary_root_module = createStandaloneTestRoot(
        b,
        target,
        optimize,
        "phase7_string_helpers_sample_boundary.zig",
    );
    const cmdline_root_module = createImportedTestRoot(
        b,
        target,
        optimize,
        "phase7_cmdline.zig",
        "cmdline",
        "../../lib/cmdline.zig",
    );
    const cmdline_survey_root_module = createStandaloneTestRoot(
        b,
        target,
        optimize,
        "phase7_cmdline_survey.zig",
    );
    const argv_split_root_module = createImportedTestRoot(
        b,
        target,
        optimize,
        "phase7_argv_split.zig",
        "argv_split",
        "../../lib/argv_split.zig",
    );
    const argv_split_survey_root_module = createStandaloneTestRoot(
        b,
        target,
        optimize,
        "phase7_argv_split_survey.zig",
    );
    const rbtree_root_module = createImportedTestRoot(
        b,
        target,
        optimize,
        "phase7_rbtree.zig",
        "rbtree",
        "../../lib/rbtree.zig",
    );
    const rbtree_survey_root_module = createStandaloneTestRoot(
        b,
        target,
        optimize,
        "phase7_rbtree_survey.zig",
    );

    const run_string_helpers_tests = addTestRun(
        b,
        "phase7-string-helpers-tests",
        string_helpers_root_module,
        null,
    );
    const run_string_helpers_survey_tests = addTestRun(
        b,
        "phase7-string-helpers-survey-tests",
        string_helpers_survey_root_module,
        repo_root,
    );
    const run_string_helpers_sample_boundary_tests = addTestRun(
        b,
        "phase7-string-helpers-sample-boundary-tests",
        string_helpers_sample_boundary_root_module,
        repo_root,
    );
    const run_cmdline_tests = addTestRun(
        b,
        "phase7-cmdline-tests",
        cmdline_root_module,
        null,
    );
    const run_cmdline_survey_tests = addTestRun(
        b,
        "phase7-cmdline-survey-tests",
        cmdline_survey_root_module,
        repo_root,
    );
    const run_argv_split_tests = addTestRun(
        b,
        "phase7-argv-split-tests",
        argv_split_root_module,
        null,
    );
    const run_argv_split_survey_tests = addTestRun(
        b,
        "phase7-argv-split-survey-tests",
        argv_split_survey_root_module,
        repo_root,
    );
    const run_rbtree_tests = addTestRun(
        b,
        "phase7-rbtree-tests",
        rbtree_root_module,
        null,
    );
    const run_rbtree_survey_tests = addTestRun(
        b,
        "phase7-rbtree-survey-tests",
        rbtree_survey_root_module,
        repo_root,
    );

    const string_helpers_step = b.step(
        "phase7-string-helpers-test",
        "Run the Phase 7 string_helpers helper replay",
    );
    string_helpers_step.dependOn(&run_string_helpers_tests.step);

    const string_helpers_survey_step = b.step(
        "phase7-string-helpers-survey",
        "Run the Phase 7 string_helpers survey replay",
    );
    string_helpers_survey_step.dependOn(&run_string_helpers_survey_tests.step);

    const string_helpers_sample_boundary_step = b.step(
        "phase7-string-helpers-sample-boundary",
        "Run the Phase 7 string_helpers sample-boundary replay",
    );
    string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step);

    const cmdline_step = b.step(
        "phase7-cmdline-test",
        "Run the Phase 7 cmdline helper replay",
    );
    cmdline_step.dependOn(&run_cmdline_tests.step);

    const cmdline_survey_step = b.step(
        "phase7-cmdline-survey",
        "Run the Phase 7 cmdline survey replay",
    );
    cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);

    const argv_split_step = b.step(
        "phase7-argv-split-test",
        "Run the Phase 7 argv_split helper replay",
    );
    argv_split_step.dependOn(&run_argv_split_tests.step);

    const argv_split_survey_step = b.step(
        "phase7-argv-split-survey",
        "Run the Phase 7 argv_split survey replay",
    );
    argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step);

    const rbtree_step = b.step(
        "phase7-rbtree-test",
        "Run the Phase 7 rbtree helper replay",
    );
    rbtree_step.dependOn(&run_rbtree_tests.step);

    const rbtree_survey_step = b.step(
        "phase7-rbtree-survey",
        "Run the Phase 7 rbtree survey replay",
    );
    rbtree_survey_step.dependOn(&run_rbtree_survey_tests.step);

    const test_step = b.step("test", "Run the Phase 7 runtime helper tests");
    test_step.dependOn(&run_string_helpers_tests.step);
    test_step.dependOn(&run_string_helpers_survey_tests.step);
    test_step.dependOn(&run_string_helpers_sample_boundary_tests.step);
    test_step.dependOn(&run_cmdline_tests.step);
    test_step.dependOn(&run_cmdline_survey_tests.step);
    test_step.dependOn(&run_argv_split_tests.step);
    test_step.dependOn(&run_argv_split_survey_tests.step);
    test_step.dependOn(&run_rbtree_tests.step);
    test_step.dependOn(&run_rbtree_survey_tests.step);
}
