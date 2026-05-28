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

    const test_step = b.step("test", "Run the Phase 7 cmdline helper-local tests");
    test_step.dependOn(&run_cmdline_tests.step);
    test_step.dependOn(&run_cmdline_survey_tests.step);
}
