const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_ring_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),
        .target = target,
        .optimize = optimize,
    });
    const used_buffer_poll_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_used_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });
    used_buffer_poll_module.addImport("virtio_ring", virtio_ring_module);

    const tests = b.addTest(.{
        .name = "phase10-virtio-ring-used-buffer-poll-tests",
        .root_module = used_buffer_poll_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const used_buffer_poll_step = b.step(
        "phase10-virtio-ring-used-buffer-poll-tests",
        "Run the focused Phase 10 virtio ring used-buffer-poll wrapper tests",
    );
    used_buffer_poll_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the focused Phase 10 virtio ring used-buffer-poll wrapper tests",
    );
    test_step.dependOn(&run_tests.step);
}
