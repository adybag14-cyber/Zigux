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

    const replay_mod = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_err_ok_complement_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_mod.addImport("err_ptr", err_ptr_mod);
    replay_mod.addImport("xa_value", xa_value_mod);
    replay_mod.addImport("xarray_slot_view", xarray_slot_view_mod);

    const tests = b.addTest(.{ .root_module = replay_mod });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase3-xarray-slot-err-ok-complement-replay",
        "Run the Phase 3 xarray slot err_ptr ok-complement replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 xarray slot err_ptr ok-complement replay");
    test_step.dependOn(&run_tests.step);
}
