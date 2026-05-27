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

    const test_step = b.step("test", "Run the Phase 7 argv_split helper-local tests");
    test_step.dependOn(&run_argv_split_tests.step);
    test_step.dependOn(&run_argv_split_survey_tests.step);
}
