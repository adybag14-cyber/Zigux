const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    bitmap_module.addImport("find_bit", find_bit_module);

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap", bitmap_module);
    root_module.addImport("find_bit", find_bit_module);
    root_module.addImport("string", string_module);
    root_module.addImport("rbtree", rbtree_module);
    root_module.addImport("argv_split", argv_split_module);
    root_module.addImport("cmdline", cmdline_module);
    root_module.addImport("ctype", ctype_module);
    root_module.addImport("hweight", hweight_module);
    root_module.addImport("list_sort", list_sort_module);
    root_module.addImport("slab", slab_module);
    root_module.addImport("str_error_r", str_error_r_module);
    root_module.addImport("vsprintf", vsprintf_module);
    root_module.addImport("zalloc", zalloc_module);

    const tests = b.addTest(.{
        .name = "phase1-helper-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("test", "Run Phase 1 helper tests");
    test_step.dependOn(&run_tests.step);

    const bench_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench.zig"),
        .target = target,
        .optimize = optimize,
    });
    bench_root_module.addImport("bitmap", bitmap_module);
    bench_root_module.addImport("find_bit", find_bit_module);
    bench_root_module.addImport("string", string_module);
    bench_root_module.addImport("rbtree", rbtree_module);
    bench_root_module.addImport("argv_split", argv_split_module);
    bench_root_module.addImport("cmdline", cmdline_module);
    bench_root_module.addImport("ctype", ctype_module);
    bench_root_module.addImport("hweight", hweight_module);
    bench_root_module.addImport("list_sort", list_sort_module);
    bench_root_module.addImport("slab", slab_module);
    bench_root_module.addImport("str_error_r", str_error_r_module);
    bench_root_module.addImport("vsprintf", vsprintf_module);
    bench_root_module.addImport("zalloc", zalloc_module);

    const bench = b.addExecutable(.{
        .name = "phase1-bench",
        .root_module = bench_root_module,
    });
    const run_bench = b.addRunArtifact(bench);
    const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");
    bench_step.dependOn(&run_bench.step);

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);
    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);
    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);
    const atomic_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });
    const mmio_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio_helpers_module.addImport("abi_bindings", abi_bindings_module);
    mmio_helpers_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view_module.addImport("abi_bindings", abi_bindings_module);
    bitmap_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const cpumask_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view_module.addImport("abi_bindings", abi_bindings_module);
    cpumask_view_module.addImport("bitmap_view", bitmap_view_module);
    cpumask_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const list_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    list_view_module.addImport("abi_bindings", abi_bindings_module);
    list_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const hlist_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    hlist_view_module.addImport("abi_bindings", abi_bindings_module);
    hlist_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const err_ptr_module = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    err_ptr_module.addImport("abi_bindings", abi_bindings_module);
    const xa_value_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value_module.addImport("abi_bindings", abi_bindings_module);
    const xarray_slot_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view_module.addImport("abi_bindings", abi_bindings_module);
    xarray_slot_view_module.addImport("err_ptr", err_ptr_module);
    xarray_slot_view_module.addImport("xa_value", xa_value_module);
    xarray_slot_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const idr_slot_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/idr_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_view_module.addImport("abi_bindings", abi_bindings_module);
    idr_slot_view_module.addImport("err_ptr", err_ptr_module);
    idr_slot_view_module.addImport("xa_value", xa_value_module);
    idr_slot_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);

    const phase3_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_root_module.addImport("abi_bindings", abi_bindings_module);
    phase3_root_module.addImport("layout_assert", layout_assert_module);
    phase3_root_module.addImport("panic_policy", panic_policy_module);
    phase3_root_module.addImport("allocator_policy", allocator_policy_module);
    phase3_root_module.addImport("atomic_helpers", atomic_helpers_module);
    phase3_root_module.addImport("barrier_helpers", barrier_helpers_module);
    phase3_root_module.addImport("mmio_helpers", mmio_helpers_module);
    phase3_root_module.addImport("bitmap_view", bitmap_view_module);
    phase3_root_module.addImport("cpumask_view", cpumask_view_module);
    phase3_root_module.addImport("list_view", list_view_module);
    phase3_root_module.addImport("hlist_view", hlist_view_module);
    phase3_root_module.addImport("err_ptr", err_ptr_module);
    phase3_root_module.addImport("xa_value", xa_value_module);
    phase3_root_module.addImport("xarray_slot_view", xarray_slot_view_module);
    phase3_root_module.addImport("idr_slot_view", idr_slot_view_module);
    phase3_root_module.addImport("export_shim", export_shim_module);
    phase3_root_module.addImport("narrow_unsafe", narrow_unsafe_module);
    phase3_root_module.addImport("uapi_version", uapi_version_module);

    const phase3_tests = b.addTest(.{
        .name = "phase3-abi-tests",
        .root_module = phase3_root_module,
    });
    const run_phase3_tests = b.addRunArtifact(phase3_tests);
    const phase3_step = b.step("phase3-test", "Run Phase 3 ABI and interop substrate tests");
    phase3_step.dependOn(&run_phase3_tests.step);

    const phase3_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_dump_module.addImport("abi_bindings", abi_bindings_module);
    const phase3_dump = b.addExecutable(.{
        .name = "phase3-abi-dump",
        .root_module = phase3_dump_module,
    });
    const run_phase3_dump = b.addRunArtifact(phase3_dump);
    const phase3_dump_step = b.step("phase3-dump", "Run Phase 3 ABI dump");
    phase3_dump_step.dependOn(&run_phase3_dump.step);

    const phase3_bitmap_cpumask_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_bitmap_cpumask_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_bitmap_cpumask_dump_module.addImport("bitmap_view", bitmap_view_module);
    phase3_bitmap_cpumask_dump_module.addImport("cpumask_view", cpumask_view_module);
    const phase3_bitmap_cpumask_dump = b.addExecutable(.{
        .name = "phase3-bitmap-cpumask-dump",
        .root_module = phase3_bitmap_cpumask_dump_module,
    });
    const run_phase3_bitmap_cpumask_dump = b.addRunArtifact(phase3_bitmap_cpumask_dump);
    const phase3_bitmap_cpumask_dump_step = b.step("phase3-bitmap-cpumask-dump", "Run Phase 3 bitmap/cpumask interop dump");
    phase3_bitmap_cpumask_dump_step.dependOn(&run_phase3_bitmap_cpumask_dump.step);

    const phase3_list_hlist_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_list_hlist_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_list_hlist_dump_module.addImport("list_view", list_view_module);
    phase3_list_hlist_dump_module.addImport("hlist_view", hlist_view_module);
    phase3_list_hlist_dump_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const phase3_list_hlist_dump = b.addExecutable(.{
        .name = "phase3-list-hlist-dump",
        .root_module = phase3_list_hlist_dump_module,
    });
    const run_phase3_list_hlist_dump = b.addRunArtifact(phase3_list_hlist_dump);
    const phase3_list_hlist_dump_step = b.step("phase3-list-hlist-dump", "Run Phase 3 list/hlist interop dump");
    phase3_list_hlist_dump_step.dependOn(&run_phase3_list_hlist_dump.step);

    const phase3_errptr_xarray_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_errptr_xarray_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_errptr_xarray_dump_module.addImport("err_ptr", err_ptr_module);
    phase3_errptr_xarray_dump_module.addImport("xa_value", xa_value_module);
    const phase3_errptr_xarray_dump = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = phase3_errptr_xarray_dump_module,
    });
    const run_phase3_errptr_xarray_dump = b.addRunArtifact(phase3_errptr_xarray_dump);
    const phase3_errptr_xarray_dump_step = b.step("phase3-errptr-xarray-dump", "Run Phase 3 err_ptr/xarray interop dump");
    phase3_errptr_xarray_dump_step.dependOn(&run_phase3_errptr_xarray_dump.step);

    const phase3_xarray_slot_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_xarray_slot_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_xarray_slot_dump_module.addImport("err_ptr", err_ptr_module);
    phase3_xarray_slot_dump_module.addImport("xa_value", xa_value_module);
    phase3_xarray_slot_dump_module.addImport("xarray_slot_view", xarray_slot_view_module);
    const phase3_xarray_slot_dump = b.addExecutable(.{
        .name = "phase3-xarray-slot-dump",
        .root_module = phase3_xarray_slot_dump_module,
    });
    const run_phase3_xarray_slot_dump = b.addRunArtifact(phase3_xarray_slot_dump);
    const phase3_xarray_slot_dump_step = b.step("phase3-xarray-slot-dump", "Run Phase 3 xarray slot interop dump");
    phase3_xarray_slot_dump_step.dependOn(&run_phase3_xarray_slot_dump.step);

    const phase3_idr_slot_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_idr_slot_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_idr_slot_dump_module.addImport("err_ptr", err_ptr_module);
    phase3_idr_slot_dump_module.addImport("xa_value", xa_value_module);
    phase3_idr_slot_dump_module.addImport("idr_slot_view", idr_slot_view_module);
    const phase3_idr_slot_dump = b.addExecutable(.{
        .name = "phase3-idr-slot-dump",
        .root_module = phase3_idr_slot_dump_module,
    });
    const run_phase3_idr_slot_dump = b.addRunArtifact(phase3_idr_slot_dump);
    const phase3_idr_slot_dump_step = b.step("phase3-idr-slot-dump", "Run Phase 3 idr slot interop dump");
    phase3_idr_slot_dump_step.dependOn(&run_phase3_idr_slot_dump.step);
}
