const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const blocker_module = b.createModule(.{
        .root_source_file = b.path("phase10_virtio_input_registration_blocker.zig"),
        .target = target,
        .optimize = optimize,
    });
    const blocker_helper_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_input_registration_blocker.zig"),
        .target = target,
        .optimize = optimize,
    });
    blocker_module.addImport("virtio_input_registration_blocker", blocker_helper_module);

    const blocker_tests = b.addTest(.{
        .name = "phase10-virtio-input-registration-blocker-tests",
        .root_module = blocker_module,
    });
    const run_blocker_tests = b.addRunArtifact(blocker_tests);

    const test_step = b.step("test", "Run the focused Phase 10 virtio input registration blocker replay");
    test_step.dependOn(&run_blocker_tests.step);
}
