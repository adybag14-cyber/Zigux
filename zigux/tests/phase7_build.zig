const std = @import("std");

fn createStandaloneRootModule(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    root_source_file: []const u8,
) *std.Build.Module {
    return b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
}

fn createImportedRootModule(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    helper_source_file: []const u8,
    root_source_file: []const u8,
    import_name: []const u8,
) *std.Build.Module {
    const helper_module = createStandaloneRootModule(b, target, optimize, helper_source_file);
    const root_module = createStandaloneRootModule(b, target, optimize, root_source_file);
    root_module.addImport(import_name, helper_module);
    return root_module;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_helpers_root_module = createImportedRootModule(
        b,
        target,
        optimize,
        "../../lib/string_helpers.zig",
        "phase7_string_helpers.zig",
        "string_helpers",
    );

    const string_helpers_survey_root_module = createStandaloneRootModule(
        b,
        target,
        optimize,
        "phase7_string_helpers_survey.zig",
    );
    const string_helpers_survey_tests = b.addTest(.{
        .name = "phase7-string-helpers-survey-tests",
        .root_module = string_helpers_survey_root_module,
    });
    const run_string_helpers_survey_tests = b.addRunArtifact(string_helpers_survey_tests);
    run_string_helpers_survey_tests.setCwd(b.path("../.."));
    const string_helpers_survey_step = b.step(
        "phase7-string-helpers-survey",
        "Run the Phase 7 string helpers survey replay",
    );
    string_helpers_survey_step.dependOn(&run_string_helpers_survey_tests.step);

    const cmdline_root_module = createImportedRootModule(
        b,
        target,
        optimize,
        "../../lib/cmdline.zig",
        "phase7_cmdline.zig",
        "cmdline",
    );

    const cmdline_survey_root_module = createStandaloneRootModule(
        b,
        target,
        optimize,
        "phase7_cmdline_survey.zig",
    );
    const cmdline_survey_tests = b.addTest(.{
        .name = "phase7-cmdline-survey-tests",
        .root_module = cmdline_survey_root_module,
    });
    const run_cmdline_survey_tests = b.addRunArtifact(cmdline_survey_tests);
    run_cmdline_survey_tests.setCwd(b.path("../.."));
    const cmdline_survey_step = b.step(
        "phase7-cmdline-survey",
        "Run the Phase 7 cmdline survey replay",
    );
    cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);

    const argv_split_root_module = createImportedRootModule(
        b,
        target,
        optimize,
        "../../lib/argv_split.zig",
        "phase7_argv_split.zig",
        "argv_split",
    );

    const argv_split_survey_root_module = createStandaloneRootModule(
        b,
        target,
        optimize,
        "phase7_argv_split_survey.zig",
    );
    const argv_split_survey_tests = b.addTest(.{
        .name = "phase7-argv-split-survey-tests",
        .root_module = argv_split_survey_root_module,
    });
    const run_argv_split_survey_tests = b.addRunArtifact(argv_split_survey_tests);
    run_argv_split_survey_tests.setCwd(b.path("../.."));
    const argv_split_survey_step = b.step(
        "phase7-argv-split-survey",
        "Run the Phase 7 argv split survey replay",
    );
    argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step);

    const rbtree_root_module = createImportedRootModule(
        b,
        target,
        optimize,
        "../../lib/rbtree.zig",
        "phase7_rbtree.zig",
        "rbtree",
    );

    const rbtree_survey_root_module = createStandaloneRootModule(
        b,
        target,
        optimize,
        "phase7_rbtree_survey.zig",
    );
    const rbtree_survey_tests = b.addTest(.{
        .name = "phase7-rbtree-survey-tests",
        .root_module = rbtree_survey_root_module,
    });
    const run_rbtree_survey_tests = b.addRunArtifact(rbtree_survey_tests);
    run_rbtree_survey_tests.setCwd(b.path("../.."));
    const rbtree_survey_step = b.step(
        "phase7-rbtree-survey",
        "Run the Phase 7 rbtree survey replay",
    );
    rbtree_survey_step.dependOn(&run_rbtree_survey_tests.step);

    const string_helpers_sample_boundary_root_module = createStandaloneRootModule(
        b,
        target,
        optimize,
        "phase7_string_helpers_sample_boundary.zig",
    );
    const string_helpers_sample_boundary_tests = b.addTest(.{
        .name = "phase7-string-helpers-sample-boundary-tests",
        .root_module = string_helpers_sample_boundary_root_module,
    });
    const run_string_helpers_sample_boundary_tests = b.addRunArtifact(string_helpers_sample_boundary_tests);
    run_string_helpers_sample_boundary_tests.setCwd(b.path("../.."));
    const string_helpers_sample_boundary_step = b.step(
        "phase7-string-helpers-sample-boundary",
        "Run the Phase 7 string helpers sample-boundary replay",
    );
    string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step);

    const string_helpers_tests = b.addTest(.{
        .name = "phase7-string-helpers-tests",
        .root_module = string_helpers_root_module,
    });
    const run_string_helpers_tests = b.addRunArtifact(string_helpers_tests);
    const string_helpers_step = b.step(
        "phase7-string-helpers-test",
        "Run the Phase 7 string helpers tests",
    );
    string_helpers_step.dependOn(&run_string_helpers_tests.step);

    const cmdline_tests = b.addTest(.{
        .name = "phase7-cmdline-tests",
        .root_module = cmdline_root_module,
    });
    const run_cmdline_tests = b.addRunArtifact(cmdline_tests);
    const cmdline_step = b.step(
        "phase7-cmdline-test",
        "Run the Phase 7 cmdline helper tests",
    );
    cmdline_step.dependOn(&run_cmdline_tests.step);

    const argv_split_tests = b.addTest(.{
        .name = "phase7-argv-split-tests",
        .root_module = argv_split_root_module,
    });
    const run_argv_split_tests = b.addRunArtifact(argv_split_tests);
    const argv_split_step = b.step(
        "phase7-argv-split-test",
        "Run the Phase 7 argv split helper tests",
    );
    argv_split_step.dependOn(&run_argv_split_tests.step);

    const rbtree_tests = b.addTest(.{
        .name = "phase7-rbtree-tests",
        .root_module = rbtree_root_module,
    });
    const run_rbtree_tests = b.addRunArtifact(rbtree_tests);
    const rbtree_step = b.step(
        "phase7-rbtree-test",
        "Run the Phase 7 rbtree helper tests",
    );
    rbtree_step.dependOn(&run_rbtree_tests.step);

    const test_step = b.step("test", "Run Phase 7 runtime helper tests");
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
