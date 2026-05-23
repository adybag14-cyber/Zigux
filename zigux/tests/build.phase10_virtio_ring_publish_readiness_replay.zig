const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_ring_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),
        .target = target,
        .optimize = optimize,
    });
    const publish_readiness_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_ring_publish_readiness.zig"),
        .target = target,
        .optimize = optimize,
    });
    publish_readiness_module.addImport("virtio_ring", virtio_ring_module);

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_ring_publish_readiness_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("virtio_ring", virtio_ring_module);
    replay_module.addImport("virtio_ring_publish_readiness", publish_readiness_module);

    const tests = b.addTest(.{
        .name = "phase10-virtio-ring-publish-readiness-replay",
        .root_module = replay_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase10-virtio-ring-publish-readiness-replay",
        "Run the bounded Phase 10 virtio ring publish-readiness replay",
    );
    replay_step.dependOn(&run_tests.step);
}
