const std = @import("std");

fn addBitmapCpumaskStarterPacket(
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

fn addListHlistStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const list_view = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", list_view);
    root_module.addImport("hlist_view", hlist_view);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_cpumask = addBitmapCpumaskStarterPacket(b, target, optimize);
    const list_hlist = addListHlistStarterPacket(b, target, optimize);

    const step = b.step(
        "phase3-bitmap-cpumask-list-hlist-test",
        "Run the shared Phase 3 bitmap/cpumask and list/hlist starter packets together",
    );
    step.dependOn(&bitmap_cpumask.step);
    step.dependOn(&list_hlist.step);

    const test_step = b.step(
        "test",
        "Run the shared Phase 3 bitmap/cpumask and list/hlist starter packet bundle",
    );
    test_step.dependOn(step);

    b.default_step.dependOn(test_step);
}
