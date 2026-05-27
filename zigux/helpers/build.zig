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

fn addBitmapHelperModule(
    b: *std.Build,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Module {
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_view = b.createModule(.{
        .root_source_file = b.path("bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_view", bitmap_view);
    return root_module;
}

fn addErrPtrModule(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Module {
    return b.createModule(.{
        .root_source_file = b.path("err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
}

fn addXaValueModule(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    err_ptr: *std.Build.Module,
) *std.Build.Module {
    const root_module = b.createModule(.{
        .root_source_file = b.path("xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    return root_module;
}

fn addXarraySlotViewModule(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    err_ptr: *std.Build.Module,
    xa_value: *std.Build.Module,
) *std.Build.Module {
    const root_module = b.createModule(.{
        .root_source_file = b.path("xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);
    return root_module;
}

fn addMmioHelperModule(
    b: *std.Build,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    abi_bindings: *std.Build.Module,
    unsafe_policy: *std.Build.Module,
) *std.Build.Module {
    const root_module = addAbiHelperModule(
        b,
        root_source_file,
        target,
        optimize,
        abi_bindings,
    );
    root_module.addImport("unsafe_policy", unsafe_policy);
    return root_module;
}

fn addMmioWidthHelperModule(
    b: *std.Build,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    mmio_module: *std.Build.Module,
) *std.Build.Module {
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("mmio", mmio_module);
    return root_module;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = abiBindingsModule(b, target, optimize);
    const narrow_module = addAbiHelperModule(
        b,
        "../unsafe/narrow.zig",
        target,
        optimize,
        abi_bindings,
    );

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
    const narrow = addModuleTest(
        b,
        "helper-narrow",
        narrow_module,
    );
    const unsafe_policy_module = addAbiHelperModule(
        b,
        "unsafe_policy.zig",
        target,
        optimize,
        abi_bindings,
    );
    unsafe_policy_module.addImport("narrow", narrow_module);
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
    const bitmap_view = addHelperTest(
        b,
        "helper-bitmap-view",
        "bitmap_view.zig",
        target,
        optimize,
    );
    const list_view = addHelperTest(
        b,
        "helper-list-view",
        "list_view.zig",
        target,
        optimize,
    );
    const hlist_view = addHelperTest(
        b,
        "helper-hlist-view",
        "hlist_view.zig",
        target,
        optimize,
    );
    const cpumask_view = addModuleTest(
        b,
        "helper-cpumask-view",
        addBitmapHelperModule(
            b,
            "cpumask_view.zig",
            target,
            optimize,
        ),
    );
    const err_ptr_module = addErrPtrModule(b, target, optimize);
    const xa_value_module = addXaValueModule(
        b,
        target,
        optimize,
        err_ptr_module,
    );
    const err_ptr = addModuleTest(
        b,
        "helper-err-ptr",
        err_ptr_module,
    );
    const xa_value = addModuleTest(
        b,
        "helper-xa-value",
        xa_value_module,
    );
    const xarray_slot_view = addModuleTest(
        b,
        "helper-xarray-slot-view",
        addXarraySlotViewModule(
            b,
            target,
            optimize,
            err_ptr_module,
            xa_value_module,
        ),
    );
    const mmio_module = addMmioHelperModule(
        b,
        "mmio.zig",
        target,
        optimize,
        abi_bindings,
        unsafe_policy_module,
    );
    const mmio = addModuleTest(
        b,
        "helper-mmio",
        mmio_module,
    );
    const mmio_width = addModuleTest(
        b,
        "helper-mmio-width",
        addMmioWidthHelperModule(
            b,
            "mmio_width.zig",
            target,
            optimize,
            mmio_module,
        ),
    );
    const policy_helpers = b.step(
        "test-policy-helpers",
        "Run the helper-local Phase 3 ABI policy helper tests.",
    );
    policy_helpers.dependOn(&panic_policy.step);
    policy_helpers.dependOn(&allocator_policy.step);
    policy_helpers.dependOn(&narrow.step);
    policy_helpers.dependOn(&unsafe_policy.step);

    const low_level_helpers = b.step(
        "test-low-level-helpers",
        "Run the helper-local Phase 3 low-level wrapper and width-alias tests.",
    );
    low_level_helpers.dependOn(&atomic.step);
    low_level_helpers.dependOn(&barrier.step);
    low_level_helpers.dependOn(&mmio.step);
    low_level_helpers.dependOn(&mmio_width.step);

    const mmio_width_step = b.step(
        "test-mmio-width",
        "Run the helper-local MMIO width alias tests.",
    );
    mmio_width_step.dependOn(&mmio_width.step);

    const unsafe_boundary_helpers = b.step(
        "test-unsafe-boundary",
        "Run the helper-local Phase 3 unsafe-boundary tests.",
    );
    unsafe_boundary_helpers.dependOn(&narrow.step);
    unsafe_boundary_helpers.dependOn(&unsafe_policy.step);

    const shared_view_helpers = b.step(
        "test-shared-view-helpers",
        "Run the helper-local shared bitmap, list, hlist, and cpumask view tests.",
    );
    shared_view_helpers.dependOn(&bitmap_view.step);
    shared_view_helpers.dependOn(&list_view.step);
    shared_view_helpers.dependOn(&hlist_view.step);
    shared_view_helpers.dependOn(&cpumask_view.step);

    const xarray_helpers = b.step(
        "test-xarray-helpers",
        "Run the helper-local err_ptr, xa_value, and xarray-slot helper tests.",
    );
    xarray_helpers.dependOn(&err_ptr.step);
    xarray_helpers.dependOn(&xa_value.step);
    xarray_helpers.dependOn(&xarray_slot_view.step);

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
    all.dependOn(&narrow.step);
    all.dependOn(&unsafe_policy.step);
    all.dependOn(&atomic.step);
    all.dependOn(&barrier.step);
    all.dependOn(&bitmap_view.step);
    all.dependOn(&list_view.step);
    all.dependOn(&hlist_view.step);
    all.dependOn(&cpumask_view.step);
    all.dependOn(&err_ptr.step);
    all.dependOn(&xa_value.step);
    all.dependOn(&xarray_slot_view.step);
    all.dependOn(&mmio.step);
    all.dependOn(&mmio_width.step);
    b.default_step = all;
}
