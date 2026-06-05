const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr = b.addModule("err_ptr", .{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });

    const xa_value = b.addModule("xa_value", .{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);

    const xarray_slot_view = b.addModule("xarray_slot_view", .{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view.addImport("err_ptr", err_ptr);
    xarray_slot_view.addImport("xa_value", xa_value);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_xarray_slot_floor_constructor_rejection.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("err_ptr", err_ptr);
    tests.root_module.addImport("xa_value", xa_value);
    tests.root_module.addImport("xarray_slot_view", xarray_slot_view);

    const run_tests = b.addRunArtifact(tests);

    const step = b.step("phase3-xarray-slot-floor-constructor-rejection", "Run the Phase 3 xarray slot floor constructor rejection replay");
    step.dependOn(&run_tests.step);

    const all_tests = b.step("test", "Run the Phase 3 xarray slot floor constructor rejection replay");
    all_tests.dependOn(&run_tests.step);
}
