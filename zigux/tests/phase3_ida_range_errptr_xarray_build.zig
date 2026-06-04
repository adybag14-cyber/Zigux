const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    narrow_unsafe_module.addImport("abi_bindings", abi_bindings_module);

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view_module.addImport("abi_bindings", abi_bindings_module);
    bitmap_view_module.addImport("narrow_unsafe", narrow_unsafe_module);

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
    ida_alloc_view_module.addImport("ida_bitmap_view", ida_bitmap_view_module);

    const ida_range_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_range_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_view_module.addImport("abi_bindings", abi_bindings_module);
    ida_range_view_module.addImport("bitmap_view", bitmap_view_module);
    ida_range_view_module.addImport("ida_bitmap_view", ida_bitmap_view_module);
    ida_range_view_module.addImport("ida_alloc_view", ida_alloc_view_module);
    ida_range_view_module.addImport("narrow_unsafe", narrow_unsafe_module);

    const err_ptr_module = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value_module.addImport("err_ptr", err_ptr_module);

    const ida_range_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_range_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_packet_module.addImport("ida_bitmap_view", ida_bitmap_view_module);
    ida_range_packet_module.addImport("ida_range_view", ida_range_view_module);

    const errptr_xarray_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_packet_module.addImport("err_ptr", err_ptr_module);
    errptr_xarray_packet_module.addImport("xa_value", xa_value_module);

    const ida_range_tests = b.addTest(.{
        .name = "phase3-ida-range-starter-packet",
        .root_module = ida_range_packet_module,
    });
    const errptr_xarray_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_packet_module,
    });

    const run_ida_range_tests = b.addRunArtifact(ida_range_tests);
    const run_errptr_xarray_tests = b.addRunArtifact(errptr_xarray_tests);

    const test_step = b.step(
        "phase3-ida-range-errptr-xarray-test",
        "Run the Phase 3 IDA range and err_ptr/xarray starter packets together",
    );
    test_step.dependOn(&run_ida_range_tests.step);
    test_step.dependOn(&run_errptr_xarray_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 IDA range and err_ptr/xarray starter packets");
    default_test_step.dependOn(test_step);
}
