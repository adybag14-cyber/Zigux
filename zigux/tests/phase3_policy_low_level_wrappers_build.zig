const std = @import("std");

fn addPolicyStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    abi_bindings: *std.Build.Module,
    allocator_policy: *std.Build.Module,
    layout_assert: *std.Build.Module,
    narrow_surface: *std.Build.Module,
    panic_policy: *std.Build.Module,
    unsafe_policy: *std.Build.Module,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("panic_policy", panic_policy);
    root_module.addImport("allocator_policy", allocator_policy);
    root_module.addImport("unsafe_policy", unsafe_policy);
    root_module.addImport("layout_assert", layout_assert);
    root_module.addImport("narrow_surface", narrow_surface);

    const tests = b.addTest(.{
        .name = "phase3-policy-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addLowLevelWrappers(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    atomic: *std.Build.Module,
    barrier: *std.Build.Module,
    layout_assert: *std.Build.Module,
    mmio: *std.Build.Module,
    narrow: *std.Build.Module,
    unsafe_policy: *std.Build.Module,
) *std.Build.Step.Run {
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
    unsafe_policy.addImport("narrow", narrow);
    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("unsafe_policy", unsafe_policy);

    const run_policy = addPolicyStarterPacket(
        b,
        target,
        optimize,
        abi_bindings,
        allocator_policy,
        layout_assert,
        narrow,
        panic_policy,
        unsafe_policy,
    );
    const run_low_level = addLowLevelWrappers(
        b,
        target,
        optimize,
        atomic,
        barrier,
        layout_assert,
        mmio,
        narrow,
        unsafe_policy,
    );

    const test_step = b.step(
        "phase3-policy-low-level-wrappers-test",
        "Run the Phase 3 policy and low-level wrapper packet self-checks",
    );
    test_step.dependOn(&run_policy.step);
    test_step.dependOn(&run_low_level.step);

    const default_step = b.step("test", "Run the Phase 3 policy and low-level wrapper packet self-checks");
    default_step.dependOn(&run_policy.step);
    default_step.dependOn(&run_low_level.step);
}
