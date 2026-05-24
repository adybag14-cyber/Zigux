const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_mmio_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const apply_observation_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio_apply_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    apply_observation_module.addImport("virtio_mmio", virtio_mmio_module);

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_mmio_apply_observation_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("virtio_mmio", virtio_mmio_module);
    replay_module.addImport("virtio_mmio_apply_observation", apply_observation_module);

    const tests = b.addTest(.{
        .name = "phase10-virtio-mmio-apply-observation-replay",
        .root_module = replay_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase10-virtio-mmio-apply-observation-replay",
        "Run the bounded Phase 10 virtio MMIO apply-observation replay",
    );
    replay_step.dependOn(&run_tests.step);
}
