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
    const ida_bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_view_module.addImport("abi_bindings", abi_bindings_module);
    ida_bitmap_view_module.addImport("bitmap_view", bitmap_view_module);
    ida_bitmap_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const ida_alloc_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view_module.addImport("abi_bindings", abi_bindings_module);
    ida_alloc_view_module.addImport("bitmap_view", bitmap_view_module);
    ida_alloc_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const ida_range_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_range_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_view_module.addImport("abi_bindings", abi_bindings_module);
    ida_range_view_module.addImport("bitmap_view", bitmap_view_module);
    ida_range_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const ida_range_set_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_range_set_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_set_view_module.addImport("abi_bindings", abi_bindings_module);
    ida_range_set_view_module.addImport("bitmap_view", bitmap_view_module);
    ida_range_set_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const ida_policy_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_policy_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_policy_view_module.addImport("abi_bindings", abi_bindings_module);
    ida_policy_view_module.addImport("bitmap_view", bitmap_view_module);
    ida_policy_view_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const minor_alloc_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/minor_alloc_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    minor_alloc_plan_module.addImport("abi_bindings", abi_bindings_module);
    minor_alloc_plan_module.addImport("ida_policy_view", ida_policy_view_module);
    const dev_region_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/dev_region_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_region_plan_module.addImport("abi_bindings", abi_bindings_module);
    dev_region_plan_module.addImport("minor_alloc_plan", minor_alloc_plan_module);
    const cdev_add_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/cdev_add_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    cdev_add_plan_module.addImport("abi_bindings", abi_bindings_module);
    cdev_add_plan_module.addImport("dev_region_plan", dev_region_plan_module);
    const cdev_lookup_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/cdev_lookup_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    cdev_lookup_plan_module.addImport("abi_bindings", abi_bindings_module);
    cdev_lookup_plan_module.addImport("cdev_add_plan", cdev_add_plan_module);
    const chrdev_open_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_open_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_open_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_open_plan_module.addImport("cdev_lookup_plan", cdev_lookup_plan_module);
    const chrdev_fops_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_fops_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_fops_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_fops_plan_module.addImport("chrdev_open_plan", chrdev_open_plan_module);
    const chrdev_route_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_route_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_route_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_route_plan_module.addImport("chrdev_fops_plan", chrdev_fops_plan_module);
    const chrdev_io_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_io_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_io_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_io_plan_module.addImport("chrdev_route_plan", chrdev_route_plan_module);
    const chrdev_xfer_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_xfer_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_xfer_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_xfer_plan_module.addImport("chrdev_io_plan", chrdev_io_plan_module);
    const chrdev_resume_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_resume_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_resume_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_resume_plan_module.addImport("chrdev_xfer_plan", chrdev_xfer_plan_module);
    const chrdev_retry_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_retry_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_retry_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_retry_plan_module.addImport("chrdev_resume_plan", chrdev_resume_plan_module);
    const chrdev_requeue_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_requeue_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_requeue_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_requeue_plan_module.addImport("chrdev_retry_plan", chrdev_retry_plan_module);
    const chrdev_complete_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_complete_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_complete_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_complete_plan_module.addImport("chrdev_requeue_plan", chrdev_requeue_plan_module);
    const chrdev_notify_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_plan_module.addImport("chrdev_complete_plan", chrdev_complete_plan_module);
    const chrdev_notify_policy_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_policy_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_policy_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_policy_plan_module.addImport("chrdev_notify_plan", chrdev_notify_plan_module);
    const chrdev_notify_budget_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_budget_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_budget_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_budget_plan_module.addImport("chrdev_notify_policy_plan", chrdev_notify_policy_plan_module);
    const chrdev_notify_ack_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_plan_module.addImport("chrdev_notify_budget_plan", chrdev_notify_budget_plan_module);
    const chrdev_notify_ack_policy_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_policy_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_policy_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_policy_plan_module.addImport("chrdev_notify_ack_plan", chrdev_notify_ack_plan_module);
    const chrdev_notify_ack_budget_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_budget_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_budget_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_budget_plan_module.addImport("chrdev_notify_ack_policy_plan", chrdev_notify_ack_policy_plan_module);
    const chrdev_notify_ack_window_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_plan_module.addImport("chrdev_notify_ack_budget_plan", chrdev_notify_ack_budget_plan_module);
    const chrdev_notify_ack_window_policy_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_plan_module.addImport("chrdev_notify_ack_window_plan", chrdev_notify_ack_window_plan_module);
    const chrdev_notify_ack_window_policy_budget_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_plan_module.addImport("chrdev_notify_ack_window_policy_plan", chrdev_notify_ack_window_policy_plan_module);
    const chrdev_notify_ack_window_policy_budget_window_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_window_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_window_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_window_plan_module.addImport("chrdev_notify_ack_window_policy_budget_plan", chrdev_notify_ack_window_policy_budget_plan_module);
    const chrdev_notify_ack_window_policy_budget_window_delivery_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_window_delivery_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_window_delivery_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_window_delivery_plan_module.addImport("chrdev_notify_ack_window_policy_budget_window_plan", chrdev_notify_ack_window_policy_budget_window_plan_module);
    const chrdev_notify_ack_window_policy_budget_window_delivery_window_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_window_delivery_window_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_window_delivery_window_plan_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_plan", chrdev_notify_ack_window_policy_budget_window_delivery_plan_module);
    const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_plan_module);
    const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan_module);
    const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan_module);
    const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan_module);
    const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan_module);
    const chrdev_notify_ack_delivery_budget_guard_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_delivery_budget_guard_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_delivery_budget_guard_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_delivery_budget_guard_plan_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    const chrdev_notify_ack_delivery_budget_guard_window_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_delivery_budget_guard_window_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_delivery_budget_guard_window_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_delivery_budget_guard_window_plan_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    const chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_delivery_budget_guard_window_policy_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_plan", chrdev_notify_ack_delivery_budget_guard_window_plan_module);
    const chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module);
    const chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module);
    const chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan_module);
    const chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan_module = b.createModule(.{
        .root_source_file = b.path("../helpers/chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan_module.addImport("abi_bindings", abi_bindings_module);
    chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan_module);

    const export_shim_module = b.createModule(.{        .root_source_file = b.path("../kernel/export_shim.zig"),
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
    phase3_root_module.addImport("ida_bitmap_view", ida_bitmap_view_module);
    phase3_root_module.addImport("ida_alloc_view", ida_alloc_view_module);
    phase3_root_module.addImport("ida_range_view", ida_range_view_module);
    phase3_root_module.addImport("ida_range_set_view", ida_range_set_view_module);
    phase3_root_module.addImport("ida_policy_view", ida_policy_view_module);
    phase3_root_module.addImport("minor_alloc_plan", minor_alloc_plan_module);
    phase3_root_module.addImport("dev_region_plan", dev_region_plan_module);
    phase3_root_module.addImport("cdev_add_plan", cdev_add_plan_module);
    phase3_root_module.addImport("cdev_lookup_plan", cdev_lookup_plan_module);
    phase3_root_module.addImport("chrdev_open_plan", chrdev_open_plan_module);
    phase3_root_module.addImport("chrdev_fops_plan", chrdev_fops_plan_module);
    phase3_root_module.addImport("chrdev_route_plan", chrdev_route_plan_module);
    phase3_root_module.addImport("chrdev_io_plan", chrdev_io_plan_module);
    phase3_root_module.addImport("chrdev_xfer_plan", chrdev_xfer_plan_module);
    phase3_root_module.addImport("chrdev_resume_plan", chrdev_resume_plan_module);
    phase3_root_module.addImport("chrdev_retry_plan", chrdev_retry_plan_module);
    phase3_root_module.addImport("chrdev_requeue_plan", chrdev_requeue_plan_module);
    phase3_root_module.addImport("chrdev_complete_plan", chrdev_complete_plan_module);
    phase3_root_module.addImport("chrdev_notify_plan", chrdev_notify_plan_module);
    phase3_root_module.addImport("chrdev_notify_policy_plan", chrdev_notify_policy_plan_module);
    phase3_root_module.addImport("chrdev_notify_budget_plan", chrdev_notify_budget_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_plan", chrdev_notify_ack_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_policy_plan", chrdev_notify_ack_policy_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_budget_plan", chrdev_notify_ack_budget_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_plan", chrdev_notify_ack_window_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_plan", chrdev_notify_ack_window_policy_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_plan", chrdev_notify_ack_window_policy_budget_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_window_plan", chrdev_notify_ack_window_policy_budget_window_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_plan", chrdev_notify_ack_window_policy_budget_window_delivery_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_plan", chrdev_notify_ack_delivery_budget_guard_window_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan_module);
    phase3_root_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan_module);
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

    const phase3_ida_bitmap_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_ida_bitmap_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_ida_bitmap_dump_module.addImport("ida_bitmap_view", ida_bitmap_view_module);
    const phase3_ida_bitmap_dump = b.addExecutable(.{
        .name = "phase3-ida-bitmap-dump",
        .root_module = phase3_ida_bitmap_dump_module,
    });
    const run_phase3_ida_bitmap_dump = b.addRunArtifact(phase3_ida_bitmap_dump);
    const phase3_ida_bitmap_dump_step = b.step("phase3-ida-bitmap-dump", "Run Phase 3 ida bitmap interop dump");
    phase3_ida_bitmap_dump_step.dependOn(&run_phase3_ida_bitmap_dump.step);

    const phase3_ida_alloc_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_ida_alloc_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_ida_alloc_dump_module.addImport("ida_alloc_view", ida_alloc_view_module);
    const phase3_ida_alloc_dump = b.addExecutable(.{
        .name = "phase3-ida-alloc-dump",
        .root_module = phase3_ida_alloc_dump_module,
    });
    const run_phase3_ida_alloc_dump = b.addRunArtifact(phase3_ida_alloc_dump);
    const phase3_ida_alloc_dump_step = b.step("phase3-ida-alloc-dump", "Run Phase 3 ida allocation interop dump");
    phase3_ida_alloc_dump_step.dependOn(&run_phase3_ida_alloc_dump.step);

    const phase3_ida_range_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_range_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_ida_range_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_ida_range_dump_module.addImport("ida_range_view", ida_range_view_module);
    const phase3_ida_range_dump = b.addExecutable(.{
        .name = "phase3-ida-range-dump",
        .root_module = phase3_ida_range_dump_module,
    });
    const run_phase3_ida_range_dump = b.addRunArtifact(phase3_ida_range_dump);
    const phase3_ida_range_dump_step = b.step("phase3-ida-range-dump", "Run Phase 3 ida range interop dump");
    phase3_ida_range_dump_step.dependOn(&run_phase3_ida_range_dump.step);

    const phase3_ida_range_set_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_range_set_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_ida_range_set_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_ida_range_set_dump_module.addImport("ida_range_set_view", ida_range_set_view_module);
    const phase3_ida_range_set_dump = b.addExecutable(.{
        .name = "phase3-ida-range-set-dump",
        .root_module = phase3_ida_range_set_dump_module,
    });
    const run_phase3_ida_range_set_dump = b.addRunArtifact(phase3_ida_range_set_dump);
    const phase3_ida_range_set_dump_step = b.step("phase3-ida-range-set-dump", "Run Phase 3 ida range-set interop dump");
    phase3_ida_range_set_dump_step.dependOn(&run_phase3_ida_range_set_dump.step);

    const phase3_ida_policy_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_ida_policy_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_ida_policy_dump_module.addImport("ida_policy_view", ida_policy_view_module);
    const phase3_ida_policy_dump = b.addExecutable(.{
        .name = "phase3-ida-policy-dump",
        .root_module = phase3_ida_policy_dump_module,
    });
    const run_phase3_ida_policy_dump = b.addRunArtifact(phase3_ida_policy_dump);
    const phase3_ida_policy_dump_step = b.step("phase3-ida-policy-dump", "Run Phase 3 ida policy interop dump");
    phase3_ida_policy_dump_step.dependOn(&run_phase3_ida_policy_dump.step);

    const phase3_minor_alloc_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_minor_alloc_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_minor_alloc_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_minor_alloc_dump_module.addImport("minor_alloc_plan", minor_alloc_plan_module);
    const phase3_minor_alloc_dump = b.addExecutable(.{
        .name = "phase3-minor-alloc-dump",
        .root_module = phase3_minor_alloc_dump_module,
    });
    const run_phase3_minor_alloc_dump = b.addRunArtifact(phase3_minor_alloc_dump);
    const phase3_minor_alloc_dump_step = b.step("phase3-minor-alloc-dump", "Run Phase 3 minor alloc interop dump");
    phase3_minor_alloc_dump_step.dependOn(&run_phase3_minor_alloc_dump.step);

    const phase3_dev_region_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_dev_region_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_dev_region_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_dev_region_dump_module.addImport("dev_region_plan", dev_region_plan_module);
    const phase3_dev_region_dump = b.addExecutable(.{
        .name = "phase3-dev-region-dump",
        .root_module = phase3_dev_region_dump_module,
    });
    const run_phase3_dev_region_dump = b.addRunArtifact(phase3_dev_region_dump);
    const phase3_dev_region_dump_step = b.step("phase3-dev-region-dump", "Run Phase 3 dev region interop dump");
    phase3_dev_region_dump_step.dependOn(&run_phase3_dev_region_dump.step);

    const phase3_cdev_add_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_cdev_add_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_cdev_add_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_cdev_add_dump_module.addImport("cdev_add_plan", cdev_add_plan_module);
    phase3_cdev_add_dump_module.addImport("dev_region_plan", dev_region_plan_module);
    const phase3_cdev_add_dump = b.addExecutable(.{
        .name = "phase3-cdev-add-dump",
        .root_module = phase3_cdev_add_dump_module,
    });
    const run_phase3_cdev_add_dump = b.addRunArtifact(phase3_cdev_add_dump);
    const phase3_cdev_add_dump_step = b.step("phase3-cdev-add-dump", "Run Phase 3 cdev add interop dump");
    phase3_cdev_add_dump_step.dependOn(&run_phase3_cdev_add_dump.step);

    const phase3_cdev_lookup_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_cdev_lookup_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_cdev_lookup_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_cdev_lookup_dump_module.addImport("cdev_lookup_plan", cdev_lookup_plan_module);
    phase3_cdev_lookup_dump_module.addImport("cdev_add_plan", cdev_add_plan_module);
    const phase3_cdev_lookup_dump = b.addExecutable(.{
        .name = "phase3-cdev-lookup-dump",
        .root_module = phase3_cdev_lookup_dump_module,
    });
    const run_phase3_cdev_lookup_dump = b.addRunArtifact(phase3_cdev_lookup_dump);
    const phase3_cdev_lookup_dump_step = b.step("phase3-cdev-lookup-dump", "Run Phase 3 cdev lookup interop dump");
    phase3_cdev_lookup_dump_step.dependOn(&run_phase3_cdev_lookup_dump.step);

    const phase3_chrdev_open_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_open_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_open_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_open_dump_module.addImport("chrdev_open_plan", chrdev_open_plan_module);
    const phase3_chrdev_open_dump = b.addExecutable(.{
        .name = "phase3-chrdev-open-dump",
        .root_module = phase3_chrdev_open_dump_module,
    });
    const run_phase3_chrdev_open_dump = b.addRunArtifact(phase3_chrdev_open_dump);
    const phase3_chrdev_open_dump_step = b.step("phase3-chrdev-open-dump", "Run Phase 3 chrdev open interop dump");
    phase3_chrdev_open_dump_step.dependOn(&run_phase3_chrdev_open_dump.step);

    const phase3_chrdev_fops_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_fops_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_fops_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_fops_dump_module.addImport("chrdev_fops_plan", chrdev_fops_plan_module);
    const phase3_chrdev_fops_dump = b.addExecutable(.{
        .name = "phase3-chrdev-fops-dump",
        .root_module = phase3_chrdev_fops_dump_module,
    });
    const run_phase3_chrdev_fops_dump = b.addRunArtifact(phase3_chrdev_fops_dump);
    const phase3_chrdev_fops_dump_step = b.step("phase3-chrdev-fops-dump", "Run Phase 3 chrdev fops interop dump");
    phase3_chrdev_fops_dump_step.dependOn(&run_phase3_chrdev_fops_dump.step);

    const phase3_chrdev_route_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_route_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_route_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_route_dump_module.addImport("chrdev_route_plan", chrdev_route_plan_module);
    const phase3_chrdev_route_dump = b.addExecutable(.{
        .name = "phase3-chrdev-route-dump",
        .root_module = phase3_chrdev_route_dump_module,
    });
    const run_phase3_chrdev_route_dump = b.addRunArtifact(phase3_chrdev_route_dump);
    const phase3_chrdev_route_dump_step = b.step("phase3-chrdev-route-dump", "Run Phase 3 chrdev route interop dump");
    phase3_chrdev_route_dump_step.dependOn(&run_phase3_chrdev_route_dump.step);

    const phase3_chrdev_io_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_io_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_io_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_io_dump_module.addImport("chrdev_io_plan", chrdev_io_plan_module);
    const phase3_chrdev_io_dump = b.addExecutable(.{
        .name = "phase3-chrdev-io-dump",
        .root_module = phase3_chrdev_io_dump_module,
    });
    const run_phase3_chrdev_io_dump = b.addRunArtifact(phase3_chrdev_io_dump);
    const phase3_chrdev_io_dump_step = b.step("phase3-chrdev-io-dump", "Run Phase 3 chrdev io interop dump");
    phase3_chrdev_io_dump_step.dependOn(&run_phase3_chrdev_io_dump.step);

    const phase3_chrdev_xfer_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_xfer_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_xfer_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_xfer_dump_module.addImport("chrdev_xfer_plan", chrdev_xfer_plan_module);
    const phase3_chrdev_xfer_dump = b.addExecutable(.{
        .name = "phase3-chrdev-xfer-dump",
        .root_module = phase3_chrdev_xfer_dump_module,
    });
    const run_phase3_chrdev_xfer_dump = b.addRunArtifact(phase3_chrdev_xfer_dump);
    const phase3_chrdev_xfer_dump_step = b.step("phase3-chrdev-xfer-dump", "Run Phase 3 chrdev xfer interop dump");
    phase3_chrdev_xfer_dump_step.dependOn(&run_phase3_chrdev_xfer_dump.step);

    const phase3_chrdev_resume_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_resume_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_resume_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_resume_dump_module.addImport("chrdev_resume_plan", chrdev_resume_plan_module);
    const phase3_chrdev_resume_dump = b.addExecutable(.{
        .name = "phase3-chrdev-resume-dump",
        .root_module = phase3_chrdev_resume_dump_module,
    });
    const run_phase3_chrdev_resume_dump = b.addRunArtifact(phase3_chrdev_resume_dump);
    const phase3_chrdev_resume_dump_step = b.step("phase3-chrdev-resume-dump", "Run Phase 3 chrdev resume interop dump");
    phase3_chrdev_resume_dump_step.dependOn(&run_phase3_chrdev_resume_dump.step);

    const phase3_chrdev_retry_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_retry_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_retry_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_retry_dump_module.addImport("chrdev_retry_plan", chrdev_retry_plan_module);
    const phase3_chrdev_retry_dump = b.addExecutable(.{
        .name = "phase3-chrdev-retry-dump",
        .root_module = phase3_chrdev_retry_dump_module,
    });
    const run_phase3_chrdev_retry_dump = b.addRunArtifact(phase3_chrdev_retry_dump);
    const phase3_chrdev_retry_dump_step = b.step("phase3-chrdev-retry-dump", "Run Phase 3 chrdev retry interop dump");
    phase3_chrdev_retry_dump_step.dependOn(&run_phase3_chrdev_retry_dump.step);

    const phase3_chrdev_requeue_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_requeue_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_requeue_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_requeue_dump_module.addImport("chrdev_requeue_plan", chrdev_requeue_plan_module);
    const phase3_chrdev_requeue_dump = b.addExecutable(.{
        .name = "phase3-chrdev-requeue-dump",
        .root_module = phase3_chrdev_requeue_dump_module,
    });
    const run_phase3_chrdev_requeue_dump = b.addRunArtifact(phase3_chrdev_requeue_dump);
    const phase3_chrdev_requeue_dump_step = b.step("phase3-chrdev-requeue-dump", "Run Phase 3 chrdev requeue interop dump");
    phase3_chrdev_requeue_dump_step.dependOn(&run_phase3_chrdev_requeue_dump.step);

    const phase3_chrdev_complete_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_complete_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_complete_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_complete_dump_module.addImport("chrdev_complete_plan", chrdev_complete_plan_module);
    const phase3_chrdev_complete_dump = b.addExecutable(.{
        .name = "phase3-chrdev-complete-dump",
        .root_module = phase3_chrdev_complete_dump_module,
    });
    const run_phase3_chrdev_complete_dump = b.addRunArtifact(phase3_chrdev_complete_dump);
    const phase3_chrdev_complete_dump_step = b.step("phase3-chrdev-complete-dump", "Run Phase 3 chrdev complete interop dump");
    phase3_chrdev_complete_dump_step.dependOn(&run_phase3_chrdev_complete_dump.step);

    const phase3_chrdev_notify_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_dump_module.addImport("chrdev_notify_plan", chrdev_notify_plan_module);
    const phase3_chrdev_notify_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-dump",
        .root_module = phase3_chrdev_notify_dump_module,
    });
    const run_phase3_chrdev_notify_dump = b.addRunArtifact(phase3_chrdev_notify_dump);
    const phase3_chrdev_notify_dump_step = b.step("phase3-chrdev-notify-dump", "Run Phase 3 chrdev notify interop dump");
    phase3_chrdev_notify_dump_step.dependOn(&run_phase3_chrdev_notify_dump.step);

    const phase3_chrdev_notify_policy_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_policy_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_policy_dump_module.addImport("chrdev_notify_policy_plan", chrdev_notify_policy_plan_module);
    const phase3_chrdev_notify_policy_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-policy-dump",
        .root_module = phase3_chrdev_notify_policy_dump_module,
    });
    const run_phase3_chrdev_notify_policy_dump = b.addRunArtifact(phase3_chrdev_notify_policy_dump);
    const phase3_chrdev_notify_policy_dump_step = b.step("phase3-chrdev-notify-policy-dump", "Run Phase 3 chrdev notify policy interop dump");
    phase3_chrdev_notify_policy_dump_step.dependOn(&run_phase3_chrdev_notify_policy_dump.step);
    const phase3_chrdev_notify_budget_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_budget_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_budget_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_budget_dump_module.addImport("chrdev_notify_budget_plan", chrdev_notify_budget_plan_module);
    const phase3_chrdev_notify_budget_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-budget-dump",
        .root_module = phase3_chrdev_notify_budget_dump_module,
    });
    const run_phase3_chrdev_notify_budget_dump = b.addRunArtifact(phase3_chrdev_notify_budget_dump);
    const phase3_chrdev_notify_budget_dump_step = b.step("phase3-chrdev-notify-budget-dump", "Run Phase 3 chrdev notify budget interop dump");
    phase3_chrdev_notify_budget_dump_step.dependOn(&run_phase3_chrdev_notify_budget_dump.step);
    const phase3_chrdev_notify_ack_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_dump_module.addImport("chrdev_notify_ack_plan", chrdev_notify_ack_plan_module);
    const phase3_chrdev_notify_ack_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-dump",
        .root_module = phase3_chrdev_notify_ack_dump_module,
    });
    const run_phase3_chrdev_notify_ack_dump = b.addRunArtifact(phase3_chrdev_notify_ack_dump);
    const phase3_chrdev_notify_ack_dump_step = b.step("phase3-chrdev-notify-ack-dump", "Run Phase 3 chrdev notify ack interop dump");
    phase3_chrdev_notify_ack_dump_step.dependOn(&run_phase3_chrdev_notify_ack_dump.step);
    const phase3_chrdev_notify_ack_policy_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_policy_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_policy_dump_module.addImport("chrdev_notify_ack_policy_plan", chrdev_notify_ack_policy_plan_module);
    const phase3_chrdev_notify_ack_policy_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-policy-dump",
        .root_module = phase3_chrdev_notify_ack_policy_dump_module,
    });
    const run_phase3_chrdev_notify_ack_policy_dump = b.addRunArtifact(phase3_chrdev_notify_ack_policy_dump);
    const phase3_chrdev_notify_ack_policy_dump_step = b.step("phase3-chrdev-notify-ack-policy-dump", "Run Phase 3 chrdev notify ack policy interop dump");
    phase3_chrdev_notify_ack_policy_dump_step.dependOn(&run_phase3_chrdev_notify_ack_policy_dump.step);
    const phase3_chrdev_notify_ack_budget_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_budget_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_budget_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_budget_dump_module.addImport("chrdev_notify_ack_budget_plan", chrdev_notify_ack_budget_plan_module);
    const phase3_chrdev_notify_ack_budget_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-budget-dump",
        .root_module = phase3_chrdev_notify_ack_budget_dump_module,
    });
    const run_phase3_chrdev_notify_ack_budget_dump = b.addRunArtifact(phase3_chrdev_notify_ack_budget_dump);
    const phase3_chrdev_notify_ack_budget_dump_step = b.step("phase3-chrdev-notify-ack-budget-dump", "Run Phase 3 chrdev notify ack budget interop dump");
    phase3_chrdev_notify_ack_budget_dump_step.dependOn(&run_phase3_chrdev_notify_ack_budget_dump.step);
    const phase3_chrdev_notify_ack_window_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_dump_module.addImport("chrdev_notify_ack_window_plan", chrdev_notify_ack_window_plan_module);
    const phase3_chrdev_notify_ack_window_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-dump",
        .root_module = phase3_chrdev_notify_ack_window_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_dump);
    const phase3_chrdev_notify_ack_window_dump_step = b.step("phase3-chrdev-notify-ack-window-dump", "Run Phase 3 chrdev notify ack window interop dump");
    phase3_chrdev_notify_ack_window_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_dump.step);
    const phase3_chrdev_notify_ack_window_policy_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_dump_module.addImport("chrdev_notify_ack_window_policy_plan", chrdev_notify_ack_window_policy_plan_module);
    const phase3_chrdev_notify_ack_window_policy_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_dump);
    const phase3_chrdev_notify_ack_window_policy_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-dump", "Run Phase 3 chrdev notify ack window policy interop dump");
    phase3_chrdev_notify_ack_window_policy_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_dump.step);
    const phase3_chrdev_notify_ack_window_policy_budget_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_dump_module.addImport("chrdev_notify_ack_window_policy_budget_plan", chrdev_notify_ack_window_policy_budget_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-dump", "Run Phase 3 chrdev notify ack window policy budget interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_dump.step);
    const phase3_chrdev_notify_ack_window_policy_budget_window_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_window_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_window_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_window_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_plan", chrdev_notify_ack_window_policy_budget_window_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_window_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-window-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_window_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_window_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_window_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_window_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-window-dump", "Run Phase 3 chrdev notify ack window policy budget window interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_window_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_window_dump.step);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_plan", chrdev_notify_ack_window_policy_budget_window_delivery_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-window-delivery-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-window-delivery-dump", "Run Phase 3 chrdev notify ack window policy budget window delivery interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_dump.step);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-dump", "Run Phase 3 chrdev notify ack window policy budget window delivery window interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_dump.step);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-dump", "Run Phase 3 chrdev notify ack window policy budget window delivery window budget interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_dump.step);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-dump", "Run Phase 3 chrdev notify ack window policy budget window delivery window budget window interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_dump.step);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-dump", "Run Phase 3 chrdev notify ack window policy budget window delivery window budget window delivery interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_dump.step);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-dump", "Run Phase 3 chrdev notify ack window policy budget window delivery window budget window delivery window interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_dump.step);

    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-dump",
        .root_module = phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump_module,
    });
    const run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump = b.addRunArtifact(phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump);
    const phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump_step = b.step("phase3-chrdev-notify-ack-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-dump", "Run Phase 3 chrdev notify ack window policy budget window delivery window budget window delivery window budget interop dump");
    phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump_step.dependOn(&run_phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dump.step);
    const phase3_chrdev_notify_ack_delivery_budget_guard_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_delivery_budget_guard_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_delivery_budget_guard_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    const phase3_chrdev_notify_ack_delivery_budget_guard_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-delivery-budget-guard-dump",
        .root_module = phase3_chrdev_notify_ack_delivery_budget_guard_dump_module,
    });
    const run_phase3_chrdev_notify_ack_delivery_budget_guard_dump = b.addRunArtifact(phase3_chrdev_notify_ack_delivery_budget_guard_dump);
    const phase3_chrdev_notify_ack_delivery_budget_guard_dump_step = b.step("phase3-chrdev-notify-ack-delivery-budget-guard-dump", "Run Phase 3 chrdev notify ack delivery budget guard interop dump");
    phase3_chrdev_notify_ack_delivery_budget_guard_dump_step.dependOn(&run_phase3_chrdev_notify_ack_delivery_budget_guard_dump.step);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_delivery_budget_guard_window_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_delivery_budget_guard_window_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_plan", chrdev_notify_ack_delivery_budget_guard_window_plan_module);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-delivery-budget-guard-window-dump",
        .root_module = phase3_chrdev_notify_ack_delivery_budget_guard_window_dump_module,
    });
    const run_phase3_chrdev_notify_ack_delivery_budget_guard_window_dump = b.addRunArtifact(phase3_chrdev_notify_ack_delivery_budget_guard_window_dump);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_dump_step = b.step("phase3-chrdev-notify-ack-delivery-budget-guard-window-dump", "Run Phase 3 chrdev notify ack delivery budget guard window interop dump");
    phase3_chrdev_notify_ack_delivery_budget_guard_window_dump_step.dependOn(&run_phase3_chrdev_notify_ack_delivery_budget_guard_window_dump.step);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_plan", chrdev_notify_ack_delivery_budget_guard_window_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-dump",
        .root_module = phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_module,
    });
    const run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump = b.addRunArtifact(phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_step = b.step("phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-dump", "Run Phase 3 chrdev notify ack delivery budget guard window policy interop dump");
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump_step.dependOn(&run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_dump.step);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_plan", chrdev_notify_ack_delivery_budget_guard_window_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-dump",
        .root_module = phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_module,
    });
    const run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump = b.addRunArtifact(phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_step = b.step("phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-dump", "Run Phase 3 chrdev notify ack delivery budget guard window policy budget interop dump");
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump_step.dependOn(&run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_dump.step);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_plan", chrdev_notify_ack_delivery_budget_guard_window_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan_module);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-dump",
        .root_module = phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_module,
    });
    const run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump = b.addRunArtifact(phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_step = b.step("phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-dump", "Run Phase 3 chrdev notify ack delivery budget guard window policy budget window interop dump");
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump_step.dependOn(&run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_dump.step);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_plan", chrdev_notify_ack_delivery_budget_guard_window_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan_module);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-dump",
        .root_module = phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_module,
    });
    const run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump = b.addRunArtifact(phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_step = b.step("phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-dump", "Run Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery interop dump");
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump_step.dependOn(&run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_dump.step);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("abi_bindings", abi_bindings_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan", chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_plan", chrdev_notify_ack_delivery_budget_guard_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_plan", chrdev_notify_ack_delivery_budget_guard_window_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan_module);
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module.addImport("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan", chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan_module);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump = b.addExecutable(.{
        .name = "phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-dump",
        .root_module = phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_module,
    });
    const run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump = b.addRunArtifact(phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump);
    const phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_step = b.step("phase3-chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-dump", "Run Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window interop dump");
    phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump_step.dependOn(&run_phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_dump.step);
}
