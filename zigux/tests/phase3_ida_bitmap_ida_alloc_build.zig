const std = @import("std");

fn addPhase3IdaBitmapStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ida_bitmap_view", ida_bitmap_view);

    const tests = b.addTest(.{
        .name = "phase3-ida-bitmap-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

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

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_bitmap_starter = addPhase3IdaBitmapStarterPacket(b, target, optimize);
    const ida_alloc_starter = addPhase3IdaAllocStarterPacket(b, target, optimize);

    const test_step = b.step(
        "phase3-ida-bitmap-ida-alloc-test",
        "Run the Phase 3 IDA bitmap and IDA allocation starter packets together",
    );
    test_step.dependOn(&ida_bitmap_starter.step);
    test_step.dependOn(&ida_alloc_starter.step);
}
