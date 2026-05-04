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

    const bytestream_fifo_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/bytestream_fifo.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_bytestream_fifo_module = b.createModule(.{
        .root_source_file = b.path("phase5_bytestream_fifo.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_bytestream_fifo_module.addImport("bytestream_fifo_sample", bytestream_fifo_sample_module);
    const phase5_bytestream_fifo_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_bytestream_fifo_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

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
    const kretprobe_example_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kretprobe_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_kretprobe_example_module = b.createModule(.{
        .root_source_file = b.path("phase5_kretprobe_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_kretprobe_example_module.addImport("kretprobe_example_sample", kretprobe_example_sample_module);
    const phase5_kretprobe_example_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_kretprobe_example_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const trace_events_sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/trace_events_sample.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_trace_events_sample_module = b.createModule(.{
        .root_source_file = b.path("phase5_trace_events_sample.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_trace_events_sample_module.addImport("trace_events_sample", trace_events_sample_module);
    const phase5_trace_events_sample_survey_module = b.createModule(.{
        .root_source_file = b.path("phase5_trace_events_sample_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const run_bytestream_fifo_sample_tests = addTestRun(
        b,
        "phase5-bytestream-fifo-sample-tests",
        bytestream_fifo_sample_module,
        null,
    );
    const run_phase5_bytestream_fifo_tests = addTestRun(
        b,
        "phase5-bytestream-fifo-tests",
        phase5_bytestream_fifo_module,
        null,
    );
    const run_phase5_bytestream_fifo_survey_tests = addTestRun(
        b,
        "phase5-bytestream-fifo-survey-tests",
        phase5_bytestream_fifo_survey_module,
        repo_root,
    );

    const run_kobject_example_sample_tests = addTestRun(
        b,
        "phase5-kobject-example-sample-tests",
        kobject_example_sample_module,
        null,
    );
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
    const run_kretprobe_example_sample_tests = addTestRun(
        b,
        "phase5-kretprobe-example-sample-tests",
        kretprobe_example_sample_module,
        null,
    );
    const run_phase5_kretprobe_example_tests = addTestRun(
        b,
        "phase5-kretprobe-example-tests",
        phase5_kretprobe_example_module,
        null,
    );
    const run_phase5_kretprobe_example_survey_tests = addTestRun(
        b,
        "phase5-kretprobe-example-survey-tests",
        phase5_kretprobe_example_survey_module,
        repo_root,
    );
    const run_phase5_trace_events_sample_tests = addTestRun(
        b,
        "phase5-trace-events-sample-tests",
        trace_events_sample_module,
        null,
    );
    const run_phase5_trace_events_tests = addTestRun(
        b,
        "phase5-trace-events-tests",
        phase5_trace_events_sample_module,
        null,
    );
    const run_phase5_trace_events_sample_survey_tests = addTestRun(
        b,
        "phase5-trace-events-sample-survey-tests",
        phase5_trace_events_sample_survey_module,
        repo_root,
    );

    const test_step = b.step("test", "Run Phase 5 reference sample checks");
    test_step.dependOn(&run_bytestream_fifo_sample_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_survey_tests.step);
    test_step.dependOn(&run_kobject_example_sample_tests.step);
    test_step.dependOn(&run_phase5_kobject_example_tests.step);
    test_step.dependOn(&run_phase5_kobject_example_survey_tests.step);
    test_step.dependOn(&run_kretprobe_example_sample_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_survey_tests.step);
    test_step.dependOn(&run_phase5_trace_events_sample_tests.step);
    test_step.dependOn(&run_phase5_trace_events_tests.step);
    test_step.dependOn(&run_phase5_trace_events_sample_survey_tests.step);
}
