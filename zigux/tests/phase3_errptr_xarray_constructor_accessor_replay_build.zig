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

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_constructor_accessor_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("err_ptr", err_ptr);
    replay_module.addImport("xa_value", xa_value);
    replay_module.addImport("xarray_slot_view", xarray_slot_view);

    const tests = b.addTest(.{
        .name = "phase3-errptr-xarray-constructor-accessor-replay-tests",
        .root_module = replay_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase3-errptr-xarray-constructor-accessor-replay",
        "Run Lane 29 err_ptr/xarray constructor accessor replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 29 err_ptr/xarray constructor accessor replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
