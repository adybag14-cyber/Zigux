const std = @import("std");

fn addSurveyTest(
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
    const tests = b.addTest(.{
        .name = name,
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase1HostToolsSmoke(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const slab_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    bitmap_module.addImport("find_bit", find_bit_module);
    root_module.addImport("argv_split", argv_split_module);
    root_module.addImport("cmdline", cmdline_module);
    root_module.addImport("find_bit", find_bit_module);
    root_module.addImport("bitmap", bitmap_module);
    root_module.addImport("ctype", ctype_module);
    root_module.addImport("hweight", hweight_module);
    root_module.addImport("list_sort", list_sort_module);
    root_module.addImport("rbtree", rbtree_module);
    root_module.addImport("string", string_module);
    root_module.addImport("slab", slab_module);
    root_module.addImport("str_error_r", str_error_r_module);
    root_module.addImport("vsprintf", vsprintf_module);
    root_module.addImport("zalloc", zalloc_module);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3DevTStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("uapi_version", uapi_version);

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("uapi_dev_t", uapi_dev_t);
    root_module.addImport("dev_t_binding", dev_t_binding);
    root_module.addImport("version_binding", version_binding);
    root_module.addImport("export_shim", export_shim);

    const tests = b.addTest(.{
        .name = "phase3-dev-t-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3ErrPtrXarrayStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);

    const tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3XarraySlotStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);
    const xarray_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view.addImport("err_ptr", err_ptr);
    xarray_slot_view.addImport("xa_value", xa_value);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);
    root_module.addImport("xarray_slot_view", xarray_slot_view);

    const tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3BitmapCpumaskStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_view = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view.addImport("bitmap_view", bitmap_view);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_view", bitmap_view);
    root_module.addImport("cpumask_view", cpumask_view);

    const tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3ListHListStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const list_view = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", list_view);
    root_module.addImport("hlist_view", hlist_view);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3ErrPtrXarrayDump(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);

    const exe = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = root_module,
    });
    return b.addRunArtifact(exe);
}

fn addPhase3PolicyStarterPacket(
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

fn addPhase3AbiCorePacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("uapi_version", uapi_version);

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const header_family_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family_binding.addImport("abi_bindings", abi_bindings);
    header_family_binding.addImport("dev_t_binding", dev_t_binding);
    header_family_binding.addImport("version_binding", version_binding);
    header_family_binding.addImport("uapi_version", uapi_version);
    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);
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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("allocator_policy", allocator_policy);
    root_module.addImport("export_shim", export_shim);
    root_module.addImport("header_family_binding", header_family_binding);
    root_module.addImport("layout_assert", layout_assert);
    root_module.addImport("panic_policy", panic_policy);
    root_module.addImport("unsafe_policy", unsafe_policy);

    const tests = b.addTest(.{
        .name = "phase3-abi-core-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3ExportShim(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version.addImport("abi_bindings", abi_bindings);
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("uapi_version", uapi_version);

    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const tests = b.addTest(.{
        .name = "phase3-export-shim",
        .root_module = export_shim,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3ExportUapiLayout(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version.addImport("abi_bindings", abi_bindings);
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("uapi_version", uapi_version);
    const header_family_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family_binding.addImport("abi_bindings", abi_bindings);
    header_family_binding.addImport("dev_t_binding", dev_t_binding);
    header_family_binding.addImport("version_binding", version_binding);
    header_family_binding.addImport("uapi_version", uapi_version);
    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_export_uapi_layout.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("uapi_dev_t", uapi_dev_t);
    root_module.addImport("uapi_version", uapi_version);
    root_module.addImport("dev_t_binding", dev_t_binding);
    root_module.addImport("version_binding", version_binding);
    root_module.addImport("header_family_binding", header_family_binding);
    root_module.addImport("export_shim", export_shim);

    const tests = b.addTest(.{
        .name = "phase3-export-uapi-layout",
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

fn addPhase3AbiDump(
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
        .root_source_file = b.path("phase3_abi_dump_current.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);

    const exe = b.addExecutable(.{
        .name = "phase3-abi-dump",
        .root_module = root_module,
    });
    return b.addRunArtifact(exe);
}

fn addPhase7ArgvSplitSurvey(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    return addSurveyTest(
        b,
        "phase7-argv-split-survey",
        "phase7_argv_split_survey.zig",
        target,
        optimize,
    );
}

fn addPhase11GpioWatchdogVerify(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/watchdog/gpio_wdt_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase11-gpio-wdt-verify",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase12VirtioNetThroughputParity(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    const throughput_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("virtio_net_throughput_parity", throughput_module);

    const tests = b.addTest(.{
        .name = "phase12-virtio-net-throughput-parity",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);
    const phase3_dev_t_starter_packet = addPhase3DevTStarterPacket(b, target, optimize);
    const phase3_errptr_xarray_starter_packet = addPhase3ErrPtrXarrayStarterPacket(
        b,
        target,
        optimize,
    );
    const phase3_xarray_slot_starter_packet = addPhase3XarraySlotStarterPacket(
        b,
        target,
        optimize,
    );
    const phase3_bitmap_cpumask_starter_packet = addPhase3BitmapCpumaskStarterPacket(
        b,
        target,
        optimize,
    );
    const phase3_list_hlist_starter_packet = addPhase3ListHListStarterPacket(
        b,
        target,
        optimize,
    );
    const phase3_errptr_xarray_dump = addPhase3ErrPtrXarrayDump(b, target, optimize);
    const phase3_policy_starter_packet = addPhase3PolicyStarterPacket(b, target, optimize);
    const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);
    const phase3_export_shim = addPhase3ExportShim(b, target, optimize);
    const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);
    const phase3_low_level_wrappers = addPhase3LowLevelWrappers(b, target, optimize);
    const phase3_abi_dump = addPhase3AbiDump(b, target, optimize);
    const phase7_argv_split_survey = addPhase7ArgvSplitSurvey(b, target, optimize);
    const phase10_virtio_core_survey = addSurveyTest(
        b,
        "phase10-virtio-core-survey",
        "phase10_virtio_core_survey.zig",
        target,
        optimize,
    );
    const phase10_virtio_ring_survey = addSurveyTest(
        b,
        "phase10-virtio-ring-survey",
        "phase10_virtio_ring_survey.zig",
        target,
        optimize,
    );
    const phase11_gpio_wdt_verify = addPhase11GpioWatchdogVerify(b, target, optimize);
    const phase12_virtio_net_throughput_parity = addPhase12VirtioNetThroughputParity(
        b,
        target,
        optimize,
    );

    const phase12_virtio_net_survey = addSurveyTest(
        b,
        "phase12-virtio-net-survey",
        "phase12_virtio_net_survey.zig",
        target,
        optimize,
    );

    const phase1_step = b.step(
        "phase1-host-tools-smoke",
        "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",
    );
    phase1_step.dependOn(&phase1_host_tools_smoke.step);

    const phase3_step = b.step(
        "phase3-dev-t-starter-packet",
        "Run the shared Phase 3 dev_t starter packet from zigux/tests",
    );
    phase3_step.dependOn(&phase3_dev_t_starter_packet.step);

    const phase3_errptr_xarray_step = b.step(
        "phase3-errptr-xarray-starter-packet",
        "Run the shared Phase 3 err_ptr/xarray starter packet from zigux/tests",
    );
    phase3_errptr_xarray_step.dependOn(&phase3_errptr_xarray_starter_packet.step);

    const phase3_xarray_slot_step = b.step(
        "phase3-xarray-slot-starter-packet",
        "Run the shared Phase 3 xarray-slot starter packet from zigux/tests",
    );
    phase3_xarray_slot_step.dependOn(&phase3_xarray_slot_starter_packet.step);

    const phase3_bitmap_cpumask_step = b.step(
        "phase3-bitmap-cpumask-starter-packet",
        "Run the shared Phase 3 bitmap/cpumask starter packet from zigux/tests",
    );
    phase3_bitmap_cpumask_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);

    const phase3_list_hlist_step = b.step(
        "phase3-list-hlist-starter-packet",
        "Run the shared Phase 3 list/hlist starter packet from zigux/tests",
    );
    phase3_list_hlist_step.dependOn(&phase3_list_hlist_starter_packet.step);

    const phase3_errptr_xarray_dump_step = b.step(
        "phase3-errptr-xarray-dump",
        "Run the shared Phase 3 err_ptr/xarray dump from zigux/tests",
    );
    phase3_errptr_xarray_dump_step.dependOn(&phase3_errptr_xarray_dump.step);

    const phase3_errptr_xarray_slice_step = b.step(
        "phase3-errptr-xarray",
        "Run the shared Phase 3 err_ptr/xarray starter packet, xarray-slot starter packet, and dump from zigux/tests",
    );
    phase3_errptr_xarray_slice_step.dependOn(&phase3_errptr_xarray_starter_packet.step);
    phase3_errptr_xarray_slice_step.dependOn(&phase3_xarray_slot_starter_packet.step);
    phase3_errptr_xarray_slice_step.dependOn(&phase3_errptr_xarray_dump.step);

    const phase3_policy_step = b.step(
        "phase3-policy-starter-packet",
        "Run the shared Phase 3 policy starter packet from zigux/tests",
    );
    phase3_policy_step.dependOn(&phase3_policy_starter_packet.step);

    const phase3_abi_core_step = b.step(
        "phase3-abi-core-packet",
        "Run the shared Phase 3 ABI core packet from zigux/tests",
    );
    phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);

    const phase3_export_uapi_layout_step = b.step(
        "phase3-export-uapi-layout",
        "Run the shared Phase 3 export/UAPI layout replay from zigux/tests",
    );
    phase3_export_uapi_layout_step.dependOn(&phase3_export_uapi_layout.step);

    const phase3_abi_export_step = b.step(
        "phase3-abi-export",
        "Run the shared Phase 3 ABI core packet plus focused export shim and export/UAPI layout replays from zigux/tests",
    );
    phase3_abi_export_step.dependOn(&phase3_abi_core_packet.step);
    phase3_abi_export_step.dependOn(&phase3_export_shim.step);
    phase3_abi_export_step.dependOn(&phase3_export_uapi_layout.step);

    const phase3_low_level_wrapper_step = b.step(
        "phase3-low-level-wrappers",
        "Run the shared Phase 3 low-level wrapper packet from zigux/tests",
    );
    phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);

    const phase3_test_step = b.step(
        "phase3-test",
        "Run the current shared Phase 3 starter packet bundle from zigux/tests",
    );
    phase3_test_step.dependOn(&phase3_dev_t_starter_packet.step);
    phase3_test_step.dependOn(&phase3_errptr_xarray_starter_packet.step);
    phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);
    phase3_test_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);
    phase3_test_step.dependOn(&phase3_list_hlist_starter_packet.step);
    phase3_test_step.dependOn(&phase3_policy_starter_packet.step);
    phase3_test_step.dependOn(&phase3_abi_core_packet.step);
    phase3_test_step.dependOn(&phase3_export_shim.step);
    phase3_test_step.dependOn(&phase3_export_uapi_layout.step);
    phase3_test_step.dependOn(&phase3_low_level_wrappers.step);

    const phase3_dump_step = b.step(
        "phase3-dump",
        "Dump the current shared Phase 3 ABI snapshot from zigux/tests",
    );
    phase3_dump_step.dependOn(&phase3_abi_dump.step);

    const phase7_step = b.step(
        "phase7-argv-split-survey",
        "Run the Phase 7 argv_split survey anchor from the shared tests root",
    );
    phase7_step.dependOn(&phase7_argv_split_survey.step);

    const phase10_step = b.step(
        "phase10-virtio-core-survey",
        "Run the Phase 10 virtio core survey anchor from the shared tests root",
    );
    phase10_step.dependOn(&phase10_virtio_core_survey.step);

    const phase10_ring_step = b.step(
        "phase10-virtio-ring-survey",
        "Run the Phase 10 virtio ring survey anchor from the shared tests root",
    );
    phase10_ring_step.dependOn(&phase10_virtio_ring_survey.step);

    const phase11_step = b.step(
        "phase11-gpio-wdt-verify",
        "Run the Phase 11 gpio watchdog verification replay from the shared tests root",
    );
    phase11_step.dependOn(&phase11_gpio_wdt_verify.step);

    const phase12_step = b.step(
        "phase12-virtio-net-survey",
        "Run the Phase 12 virtio net survey and throughput-parity anchors from the shared tests root",
    );
    phase12_step.dependOn(&phase12_virtio_net_survey.step);
    phase12_step.dependOn(&phase12_virtio_net_throughput_parity.step);

    const phase12_throughput_step = b.step(
        "phase12-virtio-net-throughput-parity",
        "Run the Phase 12 virtio net throughput-parity anchor from the shared tests root",
    );
    phase12_throughput_step.dependOn(&phase12_virtio_net_throughput_parity.step);

    const smoke_step = b.step(
        "smoke",
        "Run the currently live shared survey anchors from zigux/tests",
    );
    smoke_step.dependOn(&phase1_host_tools_smoke.step);
    smoke_step.dependOn(phase3_test_step);
    smoke_step.dependOn(&phase7_argv_split_survey.step);
    smoke_step.dependOn(&phase10_virtio_core_survey.step);
    smoke_step.dependOn(&phase10_virtio_ring_survey.step);
    smoke_step.dependOn(&phase11_gpio_wdt_verify.step);
    smoke_step.dependOn(&phase12_virtio_net_survey.step);
    smoke_step.dependOn(&phase12_virtio_net_throughput_parity.step);

    const test_step = b.step(
        "test",
        "Run the shared Zigux tests-root survey smoke",
    );
    test_step.dependOn(&phase1_host_tools_smoke.step);
    test_step.dependOn(phase3_test_step);
    test_step.dependOn(&phase7_argv_split_survey.step);
    test_step.dependOn(&phase10_virtio_core_survey.step);
    test_step.dependOn(&phase10_virtio_ring_survey.step);
    test_step.dependOn(&phase11_gpio_wdt_verify.step);
    test_step.dependOn(&phase12_virtio_net_survey.step);
    test_step.dependOn(&phase12_virtio_net_throughput_parity.step);
}
