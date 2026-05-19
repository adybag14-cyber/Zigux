const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_net_queue_resume_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_queue_resume_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_queue_resume_root_module.addImport(
        "virtio_net_queue_resume",
        virtio_net_queue_resume_module,
    );

    const virtio_net_transmit_recycle_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_transmit_recycle_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_transmit_recycle_root_module.addImport(
        "virtio_net_transmit_recycle",
        virtio_net_transmit_recycle_module,
    );

    const phase12_virtio_net_queue_resume_tests = b.addTest(.{
        .name = "phase12-virtio-net-queue-resume-tests",
        .root_module = virtio_net_queue_resume_root_module,
    });
    const run_virtio_net_queue_resume_tests = b.addRunArtifact(
        phase12_virtio_net_queue_resume_tests,
    );

    const phase12_virtio_net_transmit_recycle_tests = b.addTest(.{
        .name = "phase12-virtio-net-transmit-recycle-tests",
        .root_module = virtio_net_transmit_recycle_root_module,
    });
    const run_virtio_net_transmit_recycle_tests = b.addRunArtifact(
        phase12_virtio_net_transmit_recycle_tests,
    );

    const smoke_step = b.step(
        "smoke",
        "Run the Phase 12 virtio_net queue-resume and transmit-recycle smoke tests",
    );
    smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 12 virtio_net queue-resume and transmit-recycle tests",
    );
    test_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
}
