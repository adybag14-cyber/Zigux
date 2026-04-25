const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_core_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase10_virtio_core_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_core.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_core_module.addImport("virtio_core", virtio_core_module);

    const phase10_virtio_core_tests = b.addTest(.{
        .name = "phase10-virtio-core-tests",
        .root_module = phase10_virtio_core_module,
    });
    const run_phase10_virtio_core_tests = b.addRunArtifact(phase10_virtio_core_tests);

    const test_step = b.step("test", "Run Phase 10 virtio core lab-driver tests");
    test_step.dependOn(&run_phase10_virtio_core_tests.step);
}