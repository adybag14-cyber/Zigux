const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const queue_resume_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });
    const receive_refill_replay_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_receive_refill_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const transmit_recycle_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    const post_reset_replay_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_post_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const throughput_parity_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });

    const syntax_lab_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_syntax_lab.zig"),
        .target = target,
        .optimize = optimize,
    });
    syntax_lab_module.addImport("virtio", virtio_module);
    syntax_lab_module.addImport("virtio_net_queue_resume", queue_resume_module);
    syntax_lab_module.addImport(
        "virtio_net_receive_refill_replay",
        receive_refill_replay_module,
    );
    syntax_lab_module.addImport("virtio_net_transmit_recycle", transmit_recycle_module);
    syntax_lab_module.addImport("virtio_net_post_reset_replay", post_reset_replay_module);
    syntax_lab_module.addImport("virtio_net_throughput_parity", throughput_parity_module);

    const syntax_lab_tests = b.addTest(.{
        .name = "phase12-virtio-net-syntax-lab-tests",
        .root_module = syntax_lab_module,
    });
    const run_syntax_lab_tests = b.addRunArtifact(syntax_lab_tests);

    const smoke_step = b.step("smoke", "Run the Phase 12 virtio_net syntax-lab smoke tests");
    smoke_step.dependOn(&run_syntax_lab_tests.step);

    const test_step = b.step("test", "Run the Phase 12 virtio_net syntax-lab tests");
    test_step.dependOn(&run_syntax_lab_tests.step);
}
