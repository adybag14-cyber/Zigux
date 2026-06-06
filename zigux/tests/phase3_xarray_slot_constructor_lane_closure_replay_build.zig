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

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_xarray_slot_constructor_lane_closure_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("err_ptr", err_ptr_module);
    tests.root_module.addImport("xa_value", xa_value_module);
    tests.root_module.addImport("xarray_slot_view", xarray_slot_module);

    const run_tests = b.addRunArtifact(tests);

    const named = b.step(
        "phase3-xarray-slot-constructor-lane-closure-replay",
        "Run the Phase 3 xarray slot constructor lane closure replay",
    );
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);
}
