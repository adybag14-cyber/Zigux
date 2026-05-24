const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_ring_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_ring_reset_readiness_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_reset_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_ring_reset_readiness_module.addImport("virtio_ring", virtio_ring_module);

    const phase10_virtio_ring_reset_readiness_root_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_reset_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_ring_reset_readiness_root_module.addImport(
        "virtio_ring",
        virtio_ring_module,
    );
    phase10_virtio_ring_reset_readiness_root_module.addImport(
        "virtio_ring_reset_readiness",
        virtio_ring_reset_readiness_module,
    );

    const phase10_virtio_ring_reset_readiness_tests = b.addTest(.{
        .name = "phase10-virtio-ring-reset-readiness-test",
        .root_module = phase10_virtio_ring_reset_readiness_root_module,
    });
    const run_phase10_virtio_ring_reset_readiness_tests = b.addRunArtifact(
        phase10_virtio_ring_reset_readiness_tests,
    );

    const phase10_virtio_ring_reset_readiness_step = b.step(
        "phase10-virtio-ring-reset-readiness-test",
        "Run the Phase 10 virtio ring reset-readiness replay tests",
    );
    phase10_virtio_ring_reset_readiness_step.dependOn(
        &run_phase10_virtio_ring_reset_readiness_tests.step,
    );

    const test_step = b.step(
        "test",
        "Run the Phase 10 virtio ring reset-readiness replay tests",
    );
    test_step.dependOn(&run_phase10_virtio_ring_reset_readiness_tests.step);
}
