const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    const xarray_slot_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_module.addImport("err_ptr", err_ptr_module);
    xarray_slot_module.addImport("xa_value", xa_value_module);

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_err_band_fourhundredfortyone_equations.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("err_ptr", err_ptr_module);
    test_module.addImport("xa_value", xa_value_module);
    test_module.addImport("xarray_slot_view", xarray_slot_module);

    const tests = b.addTest(.{ .root_module = test_module });
    const run = b.addRunArtifact(tests);

    const named = b.step(
        "phase3-xarray-slot-err-band-fourhundredfortyone-equations",
        "Run the Lane 30 xarray slot errno 441 equation replay",
    );
    named.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 30 xarray slot errno 441 equation replay");
    test_step.dependOn(&run.step);
    b.default_step.dependOn(&run.step);
}
