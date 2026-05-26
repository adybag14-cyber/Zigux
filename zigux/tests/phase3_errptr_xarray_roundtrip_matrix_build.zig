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

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_roundtrip_matrix.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("err_ptr", err_ptr);
    replay_module.addImport("xa_value", xa_value);
    replay_module.addImport("xarray_slot_view", xarray_slot_view);

    const replay_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-roundtrip-matrix",
        .root_module = replay_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const test_step = b.step(
        "phase3-errptr-xarray-roundtrip-matrix",
        "Run the Phase 3 err_ptr/xarray constructor-to-raw roundtrip matrix replay",
    );
    test_step.dependOn(&run_replay_tests.step);
}
