const std = @import("std");

fn addIdaAllocIdrSlotTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
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
    const xarray_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view.addImport("err_ptr", err_ptr);
    xarray_slot_view.addImport("xa_value", xa_value);
    const idr_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/idr_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_view.addImport("xarray_slot_view", xarray_slot_view);
    idr_slot_view.addImport("xa_value", xa_value);

    const ida_root = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_root.addImport("ida_alloc_view", ida_alloc_view);
    ida_root.addImport("ida_bitmap_view", ida_bitmap_view);

    const idr_root = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_root.addImport("err_ptr", err_ptr);
    idr_root.addImport("xa_value", xa_value);
    idr_root.addImport("xarray_slot_view", xarray_slot_view);
    idr_root.addImport("idr_slot_view", idr_slot_view);

    const ida_tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet",
        .root_module = ida_root,
    });
    const idr_tests = b.addTest(.{
        .name = "phase3-idr-slot-starter-packet",
        .root_module = idr_root,
    });

    const step = b.step(
        "phase3-ida-alloc-idr-slot-test",
        "Run the Phase 3 IDA allocation and IDR slot starter packets together",
    );
    const ida_run = b.addRunArtifact(ida_tests);
    const idr_run = b.addRunArtifact(idr_tests);
    step.dependOn(&ida_run.step);
    step.dependOn(&idr_run.step);
    return step;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests = addIdaAllocIdrSlotTest(b, target, optimize);

    const test_step = b.step("test", "Run the Phase 3 IDA allocation plus IDR slot harness");
    test_step.dependOn(tests);
}
