const std = @import("std");

fn addPhase3IdaAllocStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ida_alloc_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view.addImport("ida_bitmap_view", ida_bitmap_view);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ida_alloc_view", ida_alloc_view);
    root_module.addImport("ida_bitmap_view", ida_bitmap_view);

    const tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

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

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_alloc_starter_packet = addPhase3IdaAllocStarterPacket(b, target, optimize);
    const bitmap_cpumask_starter_packet = addPhase3BitmapCpumaskStarterPacket(b, target, optimize);

    const paired_step = b.step(
        "phase3-ida-alloc-bitmap-cpumask-test",
        "Run the Phase 3 IDA allocation starter packet beside the bitmap/cpumask starter packet",
    );
    paired_step.dependOn(&ida_alloc_starter_packet.step);
    paired_step.dependOn(&bitmap_cpumask_starter_packet.step);

    const test_step = b.step("test", "Run the Phase 3 IDA allocation plus bitmap/cpumask Lane 04 shard");
    test_step.dependOn(paired_step);
}
