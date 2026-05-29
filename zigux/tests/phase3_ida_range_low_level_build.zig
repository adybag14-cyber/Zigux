const std = @import("std");

fn addPhase3IdaRangeStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ida_range_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_range_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_view.addImport("ida_bitmap_view", ida_bitmap_view);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_range_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ida_bitmap_view", ida_bitmap_view);
    root_module.addImport("ida_range_view", ida_range_view);

    const tests = b.addTest(.{
        .name = "phase3-ida-range-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3LowLevelWrappers(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);
    const narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow);
    const atomic = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });
    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("unsafe_policy", unsafe_policy);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("atomic", atomic);
    root_module.addImport("barrier", barrier);
    root_module.addImport("layout_assert", layout_assert);
    root_module.addImport("mmio", mmio);
    root_module.addImport("unsafe_policy", unsafe_policy);
    root_module.addImport("narrow", narrow);

    const tests = b.addTest(.{
        .name = "phase3-low-level-wrappers",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_range_starter_packet = addPhase3IdaRangeStarterPacket(b, target, optimize);
    const low_level_wrappers = addPhase3LowLevelWrappers(b, target, optimize);

    const paired_step = b.step(
        "phase3-ida-range-low-level-test",
        "Run the Phase 3 IDA range starter packet beside the low-level wrapper packet",
    );
    paired_step.dependOn(&ida_range_starter_packet.step);
    paired_step.dependOn(&low_level_wrappers.step);

    const test_step = b.step("test", "Run the Phase 3 IDA range plus low-level wrapper Lane 04 shard");
    test_step.dependOn(paired_step);
}
