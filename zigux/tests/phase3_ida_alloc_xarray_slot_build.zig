const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const ida_alloc_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view.addImport("ida_bitmap_view", ida_bitmap_view);

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

    const ida_alloc_root = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_root.addImport("ida_alloc_view", ida_alloc_view);
    ida_alloc_root.addImport("ida_bitmap_view", ida_bitmap_view);

    const xarray_slot_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_root.addImport("err_ptr", err_ptr);
    xarray_slot_root.addImport("xa_value", xa_value);
    xarray_slot_root.addImport("xarray_slot_view", xarray_slot_view);

    const ida_alloc_tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet-test",
        .root_module = ida_alloc_root,
    });

    const xarray_slot_tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet-test",
        .root_module = xarray_slot_root,
    });

    const run_ida_alloc_tests = b.addRunArtifact(ida_alloc_tests);
    const run_xarray_slot_tests = b.addRunArtifact(xarray_slot_tests);

    const paired = b.step(
        "phase3-ida-alloc-xarray-slot-test",
        "Run the Phase 3 IDA allocation starter packet beside the xarray-slot starter packet",
    );
    paired.dependOn(&run_ida_alloc_tests.step);
    paired.dependOn(&run_xarray_slot_tests.step);

    const test_step = b.step("test", "Run the Phase 3 IDA allocation/xarray-slot pair tests");
    test_step.dependOn(paired);
}
