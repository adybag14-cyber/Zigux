const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy.addImport("abi_bindings", abi_bindings);
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);
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

    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const policy_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    policy_module.addImport("abi_bindings", abi_bindings);
    policy_module.addImport("panic_policy", panic_policy);
    policy_module.addImport("allocator_policy", allocator_policy);
    policy_module.addImport("unsafe_policy", unsafe_policy);
    policy_module.addImport("layout_assert", layout_assert);
    policy_module.addImport("narrow_surface", narrow);

    const low_level_module = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    low_level_module.addImport("atomic", atomic);
    low_level_module.addImport("barrier", barrier);
    low_level_module.addImport("layout_assert", layout_assert);
    low_level_module.addImport("mmio", mmio);
    low_level_module.addImport("unsafe_policy", unsafe_policy);
    low_level_module.addImport("narrow", narrow);

    const ida_bitmap_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_module.addImport("ida_bitmap_view", ida_bitmap_view);

    const policy_tests = b.addTest(.{
        .name = "phase3-policy-starter-packet-test",
        .root_module = policy_module,
    });
    const low_level_tests = b.addTest(.{
        .name = "phase3-low-level-wrappers-test",
        .root_module = low_level_module,
    });
    const ida_bitmap_tests = b.addTest(.{
        .name = "phase3-ida-bitmap-starter-packet-test",
        .root_module = ida_bitmap_module,
    });

    const run_policy_tests = b.addRunArtifact(policy_tests);
    const run_low_level_tests = b.addRunArtifact(low_level_tests);
    const run_ida_bitmap_tests = b.addRunArtifact(ida_bitmap_tests);

    const test_step = b.step(
        "phase3-policy-low-level-ida-bitmap-test",
        "Run Phase 3 policy, low-level wrapper, and ida bitmap starter packets",
    );
    test_step.dependOn(&run_policy_tests.step);
    test_step.dependOn(&run_low_level_tests.step);
    test_step.dependOn(&run_ida_bitmap_tests.step);

    const default_step = b.step(
        "test",
        "Run Phase 3 policy, low-level wrapper, and ida bitmap starter packets",
    );
    default_step.dependOn(test_step);
    b.default_step.dependOn(test_step);
}
