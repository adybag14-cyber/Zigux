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

    const test_step = b.step("test", "Run Phase 5 bytestream fifo sample checks");
    test_step.dependOn(&run_phase5_bytestream_fifo_tests.step);
    test_step.dependOn(&run_phase5_bytestream_fifo_survey_tests.step);
}
