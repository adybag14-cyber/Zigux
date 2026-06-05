const std = @import("std");

fn addIdaBitmapXarraySlotTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

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

    const ida_bitmap_root = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_root.addImport("ida_bitmap_view", ida_bitmap_view);

    const xarray_slot_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_root.addImport("err_ptr", err_ptr);
    xarray_slot_root.addImport("xa_value", xa_value);
    xarray_slot_root.addImport("xarray_slot_view", xarray_slot_view);

    const ida_bitmap_tests = b.addTest(.{
        .name = "phase3-ida-bitmap-starter-packet",
        .root_module = ida_bitmap_root,
    });
    const xarray_slot_tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = xarray_slot_root,
    });

    const step = b.step(
        "phase3-ida-bitmap-xarray-slot-test",
        "Run the Phase 3 IDA-bitmap and xarray-slot starter packets together",
    );
    const ida_bitmap_run = b.addRunArtifact(ida_bitmap_tests);
    const xarray_slot_run = b.addRunArtifact(xarray_slot_tests);
    step.dependOn(&ida_bitmap_run.step);
    step.dependOn(&xarray_slot_run.step);
    return step;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests = addIdaBitmapXarraySlotTest(b, target, optimize);

    const test_step = b.step("test", "Run the Phase 3 IDA-bitmap plus xarray-slot harness");
    test_step.dependOn(tests);
}
