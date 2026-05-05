const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_input_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input.zig"),
        .target = target,
        .optimize = optimize,
    });
    const status_drain_tests_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_status_drain.zig"),
        .target = target,
        .optimize = optimize,
    });
    status_drain_tests_module.addImport("virtio_input", virtio_input_module);

    const status_drain_tests = b.addTest(.{
        .name = "phase10-virtio-input-status-drain-tests",
        .root_module = status_drain_tests_module,
    });
    const run_status_drain_tests = b.addRunArtifact(status_drain_tests);

    const test_step = b.step("test", "Run focused Phase 10 virtio input status-drain tests");
    test_step.dependOn(&run_status_drain_tests.step);
}
