const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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

    const kobject_attr_group_contract_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kobject_example_attr_group_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase5_kobject_attr_group_contract_module = b.createModule(.{
        .root_source_file = b.path("phase5_kobject_attr_group_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase5_kobject_attr_group_contract_module.addImport(
        "kobject_attr_group_contract",
        kobject_attr_group_contract_module,
    );

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

    const phase5_bytestream_fifo_tests = b.addTest(.{
        .name = "phase5-bytestream-fifo-tests",
        .root_module = phase5_bytestream_fifo_module,
    });
    const run_phase5_bytestream_fifo_tests = b.addRunArtifact(phase5_bytestream_fifo_tests);

    const phase5_bytestream_fifo_survey_tests = b.addTest(.{
        .name = "phase5-bytestream-fifo-survey-tests",
        .root_module = phase5_bytestream_fifo_survey_module,
    });
    const run_phase5_bytestream_fifo_survey_tests = b.addRunArtifact(phase5_bytestream_fifo_survey_tests);

    const phase5_kobject_example_tests = b.addTest(.{
        .name = "phase5-kobject-example-tests",
        .root_module = phase5_kobject_example_module,
    });
    const run_phase5_kobject_example_tests = b.addRunArtifact(phase5_kobject_example_tests);

    const phase5_kobject_example_survey_tests = b.addTest(.{
        .name = "phase5-kobject-example-survey-tests",
        .root_module = phase5_kobject_example_survey_module,
    });
    const run_phase5_kobject_example_survey_tests = b.addRunArtifact(phase5_kobject_example_survey_tests);

    const phase5_kobject_attr_group_contract_tests = b.addTest(.{
        .name = "phase5-kobject-attr-group-contract-tests",
        .root_module = phase5_kobject_attr_group_contract_module,
    });
    const run_phase5_kobject_attr_group_contract_tests =
        b.addRunArtifact(phase5_kobject_attr_group_contract_tests);

    const phase5_kretprobe_example_tests = b.addTest(.{
        .name = "phase5-kretprobe-example-tests",
        .root_module = phase5_kretprobe_example_module,
    });
    const run_phase5_kretprobe_example_tests = b.addRunArtifact(phase5_kretprobe_example_tests);

    const phase5_kretprobe_example_survey_tests = b.addTest(.{
        .name = "phase5-kretprobe-example-survey-tests",
        .root_module = phase5_kretprobe_example_survey_module,
    });
    const run_phase5_kretprobe_example_survey_tests = b.addRunArtifact(phase5_kretprobe_example_survey_tests);

    const phase5_trace_events_sample_tests = b.addTest(.{
        .name = "phase5-trace-events-sample-tests",
        .root_module = phase5_trace_events_sample_module,
    });
    const run_phase5_trace_events_sample_tests = b.addRunArtifact(phase5_trace_events_sample_tests);

    const phase5_trace_events_sample_survey_tests = b.addTest(.{
        .name = "phase5-trace-events-sample-survey-tests",
        .root_module = phase5_trace_events_sample_survey_module,
    });
    const run_phase5_trace_events_sample_survey_tests = b.addRunArtifact(phase5_trace_events_sample_survey_tests);

    const test_step = b.step("test", "Run Phase 5 reference sample checks");
    test_step.dependOn(&run_phase5_bytestream_fifo_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_survey_tests.step);
    test_step.dependOn(&run_phase5_kobject_example_tests.step);
    test_step.dependOn(&run_phase5_kobject_example_survey_tests.step);
    test_step.dependOn(&run_phase5_kobject_attr_group_contract_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_tests.step);
    test_step.dependOn(&run_phase5_kretprobe_example_survey_tests.step);
    test_step.dependOn(&run_phase5_trace_events_sample_tests.step);
    test_step.dependOn(&run_phase5_trace_events_sample_survey_tests.step);
}
