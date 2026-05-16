const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_module.addImport("virtio", virtio_module);

    const syntax_lab_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_syntax_lab.zig"),
        .target = target,
        .optimize = optimize,
    });
    syntax_lab_module.addImport("virtio_net", virtio_net_module);

    const syntax_lab_tests = b.addTest(.{
        .name = "phase12-virtio-net-syntax-lab-tests",
        .root_module = syntax_lab_module,
    });

    const run_syntax_lab_tests = b.addRunArtifact(syntax_lab_tests);

    const smoke_step = b.step("smoke", "Run Phase 12 virtio_net syntax lab smoke");
    smoke_step.dependOn(&run_syntax_lab_tests.step);

    const test_step = b.step("test", "Run Phase 12 virtio_net syntax lab tests");
    test_step.dependOn(&run_syntax_lab_tests.step);
}
