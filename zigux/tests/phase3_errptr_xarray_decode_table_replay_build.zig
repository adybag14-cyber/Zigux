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

    const xarray_slot_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view_module.addImport("err_ptr", err_ptr_module);
    xarray_slot_view_module.addImport("xa_value", xa_value_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_decode_table_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr_module);
    root_module.addImport("xa_value", xa_value_module);
    root_module.addImport("xarray_slot_view", xarray_slot_view_module);

    const tests = b.addTest(.{
        .name = "phase3-errptr-xarray-decode-table-replay-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-errptr-xarray-decode-table-replay",
        "Run the Phase 3 err_ptr/xarray decode-table replay",
    );
    test_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 err_ptr/xarray decode-table replay");
    default_test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
