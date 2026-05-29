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
    root_module.addImport("ida_bitmap_view", ida_bitmap_view);
    root_module.addImport("ida_alloc_view", ida_alloc_view);

    const tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3NotifierStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_view = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_view.addImport("notifier_abi", notifier_abi);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("notifier_abi", notifier_abi);
    root_module.addImport("notifier_view", notifier_view);

    const tests = b.addTest(.{
        .name = "phase3-notifier-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_alloc = addPhase3IdaAllocStarterPacket(b, target, optimize);
    const notifier = addPhase3NotifierStarterPacket(b, target, optimize);

    const test_step = b.step(
        "phase3-ida-alloc-notifier-test",
        "Run the standalone Phase 3 IDA allocation starter packet plus notifier starter packet from zigux/tests",
    );
    test_step.dependOn(&ida_alloc.step);
    test_step.dependOn(&notifier.step);

    const default_test_step = b.step("test", "Run the Phase 3 IDA allocation plus notifier standalone shard");
    default_test_step.dependOn(test_step);
}
