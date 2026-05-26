const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_teardown_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_input_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input.zig"),
        .target = target,
        .optimize = optimize,
    });
    const teardown_observation_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_teardown_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    teardown_observation_module.addImport("virtio_input", virtio_input_module);
    root_module.addImport("virtio_input", virtio_input_module);
    root_module.addImport("virtio_input_teardown_observation", teardown_observation_module);

    const tests = b.addTest(.{
        .name = "phase10-virtio-input-teardown-observation",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "test",
        "Run the Phase 10 virtio input teardown observation replay",
    );
    test_step.dependOn(&run_tests.step);
}
