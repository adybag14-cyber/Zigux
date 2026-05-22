const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);
    const panic_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
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

    const policy_root = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    policy_root.addImport("abi_bindings", abi_bindings);
    policy_root.addImport("allocator_policy", allocator_policy);
    policy_root.addImport("panic_policy", panic_policy);
    policy_root.addImport("unsafe_policy", unsafe_policy);
    policy_root.addImport("layout_assert", layout_assert);
    policy_root.addImport("narrow_surface", narrow);

    const low_level_root = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    low_level_root.addImport("atomic", atomic);
    low_level_root.addImport("barrier", barrier);
    low_level_root.addImport("mmio", mmio);
    low_level_root.addImport("unsafe_policy", unsafe_policy);
    low_level_root.addImport("narrow", narrow);

    const policy_tests = b.addTest(.{
        .root_module = policy_root,
    });
    const run_policy_tests = b.addRunArtifact(policy_tests);

    const low_level_tests = b.addTest(.{
        .root_module = low_level_root,
    });
    const run_low_level_tests = b.addRunArtifact(low_level_tests);

    const test_step = b.step(
        "phase3-policy-low-level-test",
        "Run the Phase 3 policy starter packet and low-level wrapper packet together",
    );
    test_step.dependOn(&run_policy_tests.step);
    test_step.dependOn(&run_low_level_tests.step);
}
