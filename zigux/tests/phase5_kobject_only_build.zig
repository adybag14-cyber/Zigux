const std = @import("std");

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

    const kobject_example_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kobject_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_kobject_example_module = b.createModule(.{
        .root_source_file = b.path("phase5_kobject_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_kobject_example_module.addImport("kobject_example_sample", kobject_example_sample_module);

    const phase5_kobject_example_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_kobject_example_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const run_phase5_kobject_example_tests = addTestRun(
        b,
        "phase5-kobject-example-tests",
        phase5_kobject_example_module,
        null,
    );
    const run_phase5_kobject_example_survey_tests = addTestRun(
        b,
        "phase5-kobject-example-survey-tests",
        phase5_kobject_example_survey_module,
        repo_root,
    );

    const test_step = b.step("test", "Run focused Phase 5 kobject tests");
    test_step.dependOn(&run_phase5_kobject_example_tests.step);
    test_step.dependOn(&run_phase5_kobject_example_survey_tests.step);
}
