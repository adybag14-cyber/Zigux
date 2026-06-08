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

    const replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_zero_sentinel_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root_module.addImport("err_ptr", err_ptr_module);
    replay_root_module.addImport("xa_value", xa_value_module);
    replay_root_module.addImport("xarray_slot_view", xarray_slot_view_module);

    const replay_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-zero-sentinel-replay-tests",
        .root_module = replay_root_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    run_replay_tests.setCwd(b.path("../.."));

    const named_step = b.step(
        "phase3-errptr-xarray-zero-sentinel-replay",
        "Run the Phase 3 err_ptr/xarray zero sentinel replay",
    );
    named_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 3 err_ptr/xarray zero sentinel replay tests");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}
