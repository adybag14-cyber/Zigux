const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr = b.addModule("err_ptr", .{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
    });
    const xa_value = b.addModule("xa_value", .{
        .root_source_file = b.path("../helpers/xa_value.zig"),
    });
    xa_value.addImport("err_ptr", err_ptr);

    const xarray_slot_view = b.addModule("xarray_slot_view", .{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
    });
    xarray_slot_view.addImport("err_ptr", err_ptr);
    xarray_slot_view.addImport("xa_value", xa_value);

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_err_raw_offset_ladder_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("err_ptr", err_ptr);
    replay_module.addImport("xarray_slot_view", xarray_slot_view);

    const tests = b.addTest(.{
        .name = "phase3-xarray-slot-err-raw-offset-ladder-replay-tests",
        .root_module = replay_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step(
        "phase3-xarray-slot-err-raw-offset-ladder-replay",
        "Run the Phase 3 xarray slot err raw offset ladder replay",
    );
    step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run the Phase 3 xarray slot err raw offset ladder replay");
    default_step.dependOn(&run_tests.step);
}
