const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const narrow_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_module.addImport("abi_bindings", abi_bindings_module);

    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_module);

    const atomic_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier_module = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const mmio_module = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio_module.addImport("abi_bindings", abi_bindings_module);
    mmio_module.addImport("unsafe_policy", unsafe_policy_module);

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view_module.addImport("abi_bindings", abi_bindings_module);
    bitmap_view_module.addImport("narrow_unsafe", narrow_module);

    const ida_bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_view_module.addImport("abi_bindings", abi_bindings_module);
    ida_bitmap_view_module.addImport("bitmap_view", bitmap_view_module);
    ida_bitmap_view_module.addImport("narrow_unsafe", narrow_module);

    const ida_alloc_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view_module.addImport("ida_bitmap_view", ida_bitmap_view_module);

    const ida_range_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_range_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_view_module.addImport("abi_bindings", abi_bindings_module);
    ida_range_view_module.addImport("bitmap_view", bitmap_view_module);
    ida_range_view_module.addImport("ida_bitmap_view", ida_bitmap_view_module);
    ida_range_view_module.addImport("ida_alloc_view", ida_alloc_view_module);
    ida_range_view_module.addImport("narrow_unsafe", narrow_module);

    const ida_range_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_range_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_packet_module.addImport("ida_bitmap_view", ida_bitmap_view_module);
    ida_range_packet_module.addImport("ida_range_view", ida_range_view_module);

    const low_level_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    low_level_packet_module.addImport("atomic", atomic_module);
    low_level_packet_module.addImport("barrier", barrier_module);
    low_level_packet_module.addImport("layout_assert", layout_assert_module);
    low_level_packet_module.addImport("mmio", mmio_module);
    low_level_packet_module.addImport("unsafe_policy", unsafe_policy_module);
    low_level_packet_module.addImport("narrow", narrow_module);

    const ida_range_tests = b.addTest(.{
        .name = "phase3-ida-range-starter-packet",
        .root_module = ida_range_packet_module,
    });
    const low_level_tests = b.addTest(.{
        .name = "phase3-low-level-wrappers",
        .root_module = low_level_packet_module,
    });

    const run_ida_range_tests = b.addRunArtifact(ida_range_tests);
    const run_low_level_tests = b.addRunArtifact(low_level_tests);

    const test_step = b.step(
        "phase3-ida-range-low-level-test",
        "Run the Phase 3 IDA range and low-level wrapper packets together",
    );
    test_step.dependOn(&run_ida_range_tests.step);
    test_step.dependOn(&run_low_level_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 IDA range and low-level wrapper packets");
    default_test_step.dependOn(test_step);
}
