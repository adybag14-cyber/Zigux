const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_errptr_xarray_errno_pair_matrix_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("err_ptr", err_ptr);
    tests.root_module.addImport("xa_value", xa_value);
    tests.root_module.addImport("xarray_slot_view", xarray_slot_view);

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step("phase3-errptr-xarray-errno-pair-matrix-replay", "Run the Phase 3 err_ptr/xarray errno pair matrix replay");
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 err_ptr/xarray errno pair matrix replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
