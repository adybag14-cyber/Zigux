const std = @import("std");

fn abiBindingsModule(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Module {
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings.addImport("notifier_abi", notifier_abi);
    return abi_bindings;
}

fn addModuleTest(
    b: *std.Build,
    name: []const u8,
    root_module: *std.Build.Module,
) *std.Build.Step.Run {
    const tests = b.addTest(.{
        .name = name,
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addHelperTest(
    b: *std.Build,
    name: []const u8,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
    return addModuleTest(b, name, root_module);
}

fn addAbiHelperModule(
    b: *std.Build,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    abi_bindings: *std.Build.Module,
) *std.Build.Module {
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    return root_module;
}

fn addAbiHelperTest(
    b: *std.Build,
    name: []const u8,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    abi_bindings: *std.Build.Module,
) *std.Build.Step.Run {
    return addModuleTest(
        b,
        name,
        addAbiHelperModule(b, root_source_file, target, optimize, abi_bindings),
    );
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = abiBindingsModule(b, target, optimize);

    const layout_assert = addAbiHelperTest(
        b,
        "helper-layout-assert",
        "layout_assert.zig",
        target,
        optimize,
        abi_bindings,
    );
    const panic_policy = addAbiHelperTest(
        b,
        "helper-panic-policy",
        "panic_policy.zig",
        target,
        optimize,
        abi_bindings,
    );
    const allocator_policy = addAbiHelperTest(
        b,
        "helper-allocator-policy",
        "allocator_policy.zig",
        target,
        optimize,
        abi_bindings,
    );
    const unsafe_policy_module = addAbiHelperModule(
        b,
        "unsafe_policy.zig",
        target,
        optimize,
        abi_bindings,
    );
    const unsafe_policy = addModuleTest(
        b,
        "helper-unsafe-policy",
        unsafe_policy_module,
    );
    const atomic = addHelperTest(
        b,
        "helper-atomic",
        "atomic.zig",
        target,
        optimize,
    );
    const barrier = addHelperTest(
        b,
        "helper-barrier",
        "barrier.zig",
        target,
        optimize,
    );
    const mmio_module = b.createModule(.{
        .root_source_file = b.path("mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio_module.addImport("abi_bindings", abi_bindings);
    mmio_module.addImport("unsafe_policy", unsafe_policy_module);
    const mmio = addModuleTest(
        b,
        "helper-mmio",
        mmio_module,
    );

    const policy_helpers = b.step(
        "test-policy-helpers",
        "Run the helper-local Phase 3 ABI policy helper tests.",
    );
    policy_helpers.dependOn(&panic_policy.step);
    policy_helpers.dependOn(&allocator_policy.step);
    policy_helpers.dependOn(&unsafe_policy.step);

    const low_level_helpers = b.step(
        "test-low-level-helpers",
        "Run the helper-local Phase 3 low-level wrapper tests.",
    );
    low_level_helpers.dependOn(&atomic.step);
    low_level_helpers.dependOn(&barrier.step);
    low_level_helpers.dependOn(&mmio.step);

    const layout_step = b.step(
        "test-layout-assert",
        "Run the helper-local Phase 3 layout assertion tests.",
    );
    layout_step.dependOn(&layout_assert.step);

    const all = b.step(
        "test",
        "Run the helper-local Phase 3 ABI helper test surface.",
    );
    all.dependOn(&layout_assert.step);
    all.dependOn(&panic_policy.step);
    all.dependOn(&allocator_policy.step);
    all.dependOn(&unsafe_policy.step);
    all.dependOn(&atomic.step);
    all.dependOn(&barrier.step);
    all.dependOn(&mmio.step);
    b.default_step = all;
}
