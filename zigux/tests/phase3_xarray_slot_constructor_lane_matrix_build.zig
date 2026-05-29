const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value_mod.addImport("err_ptr", err_ptr_mod);

    const xarray_slot_view_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view_mod.addImport("err_ptr", err_ptr_mod);
    xarray_slot_view_mod.addImport("xa_value", xa_value_mod);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_xarray_slot_constructor_lane_matrix.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("err_ptr", err_ptr_mod);
    tests.root_module.addImport("xa_value", xa_value_mod);
    tests.root_module.addImport("xarray_slot_view", xarray_slot_view_mod);

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase3-xarray-slot-constructor-lane-matrix",
        "Run the Phase 3 xarray slot constructor lane matrix replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 xarray slot constructor lane matrix replay");
    test_step.dependOn(&run_tests.step);
}
