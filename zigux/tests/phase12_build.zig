const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase12_virtio_net_survey_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase12_virtio_net_survey_tests = b.addTest(.{
        .name = "phase12-virtio-net-survey-tests",
        .root_module = phase12_virtio_net_survey_module,
    });
    const run_phase12_virtio_net_survey_tests = b.addRunArtifact(phase12_virtio_net_survey_tests);

    const test_step = b.step("test", "Run Phase 12 virtio_net survey tests");
    test_step.dependOn(&run_phase12_virtio_net_survey_tests.step);
}
