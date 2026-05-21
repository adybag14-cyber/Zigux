const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_core_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_driver_id_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_driver_id.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_driver_id_module.addImport("virtio_core", virtio_core_module);

    const phase10_virtio_driver_id_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_driver_id.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase10_virtio_driver_id_module.addImport("virtio_core", virtio_core_module);
    phase10_virtio_driver_id_module.addImport("virtio_driver_id", virtio_driver_id_module);

    const tests = b.addTest(.{
        .name = "phase10-virtio-driver-id-tests",
        .root_module = phase10_virtio_driver_id_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step("test", "Run the focused Phase 10 virtio driver-id tests");
    test_step.dependOn(&run_tests.step);
}
