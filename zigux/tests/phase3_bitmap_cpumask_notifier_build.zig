const std = @import("std");

fn addPhase3BitmapCpumaskStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_view = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view.addImport("bitmap_view", bitmap_view);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_view", bitmap_view);
    root_module.addImport("cpumask_view", cpumask_view);

    const tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3NotifierAbiPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase3-notifier-abi-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_cpumask = addPhase3BitmapCpumaskStarterPacket(b, target, optimize);
    const notifier_abi = addPhase3NotifierAbiPacket(b, target, optimize);

    const test_step = b.step(
        "phase3-bitmap-cpumask-notifier-test",
        "Run the standalone Phase 3 bitmap/cpumask starter packet plus notifier ABI packet from zigux/tests",
    );
    test_step.dependOn(&bitmap_cpumask.step);
    test_step.dependOn(&notifier_abi.step);
}
