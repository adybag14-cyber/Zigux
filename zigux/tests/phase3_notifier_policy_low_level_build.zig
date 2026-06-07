const std = @import("std");

fn addNotifierStarterPacket(
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

fn addPolicyStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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
    const narrow_surface = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_surface.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow_surface);

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
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
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
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);
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
        .name = "phase3-low-level-wrappers-test",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier = addNotifierStarterPacket(b, target, optimize);
    const policy = addPolicyStarterPacket(b, target, optimize);
    const low_level = addLowLevelWrappers(b, target, optimize);

    const step = b.step(
        "phase3-notifier-policy-low-level-test",
        "Run the Phase 3 notifier, policy, and low-level wrapper packets together",
    );
    step.dependOn(&notifier.step);
    step.dependOn(&policy.step);
    step.dependOn(&low_level.step);

    const test_step = b.step("test", "Run the Phase 3 notifier/policy/low-level packet bundle");
    test_step.dependOn(&notifier.step);
    test_step.dependOn(&policy.step);
    test_step.dependOn(&low_level.step);
}
