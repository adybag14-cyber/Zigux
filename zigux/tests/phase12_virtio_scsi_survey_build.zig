const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase12-virtio-scsi-survey-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "test",
        "Run the Phase 12 virtio_scsi rollback-only survey tests",
    );
    test_step.dependOn(&run_tests.step);
}
