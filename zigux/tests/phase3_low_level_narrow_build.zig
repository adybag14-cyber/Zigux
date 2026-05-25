const std = @import("std");

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
    unsafe_policy.addImport("narrow_unsafe", narrow);
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
    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("narrow_unsafe", narrow);
    mmio.addImport("unsafe_policy", unsafe_policy);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("atomic", atomic);
    root_module.addImport("atomic_helpers", atomic);
    root_module.addImport("barrier", barrier);
    root_module.addImport("barrier_helpers", barrier);
    root_module.addImport("mmio", mmio);
    root_module.addImport("mmio_helpers", mmio);
    root_module.addImport("narrow", narrow);
    root_module.addImport("narrow_unsafe", narrow);
    root_module.addImport("allocator_policy", allocator_policy);
    root_module.addImport("allocator_policy_helpers", allocator_policy);
    root_module.addImport("panic_policy", panic_policy);
    root_module.addImport("panic_policy_helpers", panic_policy);
    root_module.addImport("unsafe_policy", unsafe_policy);

    const unit_tests = b.addTest(.{
        .name = "phase3-low-level-wrappers",
        .root_module = root_module,
    });
    return b.addRunArtifact(unit_tests);
}

fn addPhase3Narrow(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);

    const tests = b.addTest(.{
        .name = "phase3-narrow-test",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase3_low_level_wrappers = addPhase3LowLevelWrappers(b, target, optimize);
    const phase3_narrow = addPhase3Narrow(b, target, optimize);

    const step = b.step(
        "phase3-low-level-narrow-test",
        "Run the shared Phase 3 low-level wrapper and raw-pointer boundary packets through a standalone combined build shard",
    );
    step.dependOn(&phase3_low_level_wrappers.step);
    step.dependOn(&phase3_narrow.step);
}
