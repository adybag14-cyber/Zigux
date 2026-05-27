const std = @import("std");

fn addPacketTest(
    b: *std.Build,
    name: []const u8,
    root_source_file: []const u8,
    virtio_mmio_module: *std.Build.Module,
    virtio_mmio_verify_module: *std.Build.Module,
    virtio_mmio_apply_observation_module: *std.Build.Module,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("virtio_mmio", virtio_mmio_module);
    root_module.addImport("virtio_mmio_verify", virtio_mmio_verify_module);
    root_module.addImport("virtio_mmio_apply_observation", virtio_mmio_apply_observation_module);

    const tests = b.addTest(.{
        .name = name,
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_mmio_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_mmio_verify_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_mmio_verify_module.addImport("virtio_mmio", virtio_mmio_module);

    const virtio_mmio_apply_observation_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/virtio/virtio_mmio_apply_observation.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_mmio_apply_observation_module.addImport("virtio_mmio", virtio_mmio_module);

    const lab_tests = addPacketTest(
        b,
        "phase10-virtio-mmio-packet-lab-tests",
        "phase10_virtio_mmio.zig",
        virtio_mmio_module,
        virtio_mmio_verify_module,
        virtio_mmio_apply_observation_module,
        target,
        optimize,
    );
    const verify_tests = addPacketTest(
        b,
        "phase10-virtio-mmio-packet-verify-tests",
        "../../drivers/virtio/virtio_mmio_verify.zig",
        virtio_mmio_module,
        virtio_mmio_verify_module,
        virtio_mmio_apply_observation_module,
        target,
        optimize,
    );
    const apply_observation_replay_tests = addPacketTest(
        b,
        "phase10-virtio-mmio-packet-apply-observation-replay",
        "phase10_virtio_mmio_apply_observation_replay.zig",
        virtio_mmio_module,
        virtio_mmio_verify_module,
        virtio_mmio_apply_observation_module,
        target,
        optimize,
    );
    const survey_tests = addPacketTest(
        b,
        "phase10-virtio-mmio-packet-survey-tests",
        "phase10_virtio_mmio_survey.zig",
        virtio_mmio_module,
        virtio_mmio_verify_module,
        virtio_mmio_apply_observation_module,
        target,
        optimize,
    );

    const lab_step = b.step(
        "phase10-virtio-mmio-packet-lab-tests",
        "Run the bounded Phase 10 virtio MMIO packet lab tests",
    );
    lab_step.dependOn(&lab_tests.step);

    const verify_step = b.step(
        "phase10-virtio-mmio-packet-verify-tests",
        "Run the bounded Phase 10 virtio MMIO packet verify tests",
    );
    verify_step.dependOn(&verify_tests.step);

    const apply_observation_replay_step = b.step(
        "phase10-virtio-mmio-packet-apply-observation-replay",
        "Run the bounded Phase 10 virtio MMIO packet apply-observation replay",
    );
    apply_observation_replay_step.dependOn(&apply_observation_replay_tests.step);

    const survey_step = b.step(
        "phase10-virtio-mmio-packet-survey-tests",
        "Run the bounded Phase 10 virtio MMIO packet survey tests",
    );
    survey_step.dependOn(&survey_tests.step);

    const packet_step = b.step(
        "phase10-virtio-mmio-packet",
        "Run the bounded Phase 10 virtio MMIO packet bundle",
    );
    packet_step.dependOn(&lab_tests.step);
    packet_step.dependOn(&verify_tests.step);
    packet_step.dependOn(&apply_observation_replay_tests.step);
    packet_step.dependOn(&survey_tests.step);

    const test_step = b.step(
        "test",
        "Run the bounded Phase 10 virtio MMIO packet bundle",
    );
    test_step.dependOn(&lab_tests.step);
    test_step.dependOn(&verify_tests.step);
    test_step.dependOn(&apply_observation_replay_tests.step);
    test_step.dependOn(&survey_tests.step);
}
