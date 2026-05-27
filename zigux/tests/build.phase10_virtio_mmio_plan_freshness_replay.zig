const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_mmio_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const plan_freshness_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio_plan_freshness.zig"),
        .target = target,
        .optimize = optimize,
    });
    plan_freshness_module.addImport("virtio_mmio", virtio_mmio_module);

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_mmio_plan_freshness_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("virtio_mmio", virtio_mmio_module);
    replay_module.addImport("virtio_mmio_plan_freshness", plan_freshness_module);

    const wrapper_tests = b.addTest(.{
        .name = "phase10-virtio-mmio-plan-freshness-wrapper",
        .root_module = plan_freshness_module,
    });
    const run_wrapper_tests = b.addRunArtifact(wrapper_tests);

    const replay_tests = b.addTest(.{
        .name = "phase10-virtio-mmio-plan-freshness-replay",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase10-virtio-mmio-plan-freshness-replay",
        "Run the bounded Phase 10 virtio MMIO plan-freshness wrapper and replay tests",
    );
    replay_step.dependOn(&run_wrapper_tests.step);
    replay_step.dependOn(&run_replay_tests.step);
}
