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

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_err_delta_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("err_ptr", err_ptr_module);
    replay_module.addImport("xa_value", xa_value_module);
    replay_module.addImport("xarray_slot_view", xarray_slot_view_module);

    const tests = b.addTest(.{
        .name = "phase3-xarray-slot-err-delta-replay-test",
        .root_module = replay_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase3-xarray-slot-err-delta-replay",
        "Run the focused Phase 3 xarray slot err delta replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 3 xarray slot err delta replay.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
