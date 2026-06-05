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
        .imports = &.{
            .{ .name = "err_ptr", .module = err_ptr_mod },
        },
    });

    const xarray_slot_view_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "err_ptr", .module = err_ptr_mod },
            .{ .name = "xa_value", .module = xa_value_mod },
        },
    });

    const tagged_window_mod = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_tagged_window_replay.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "err_ptr", .module = err_ptr_mod },
            .{ .name = "xa_value", .module = xa_value_mod },
            .{ .name = "xarray_slot_view", .module = xarray_slot_view_mod },
        },
    });

    const tests = b.addTest(.{
        .root_module = tagged_window_mod,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase3-xarray-slot-tagged-window-replay",
        "Run the Phase 3 xarray slot tagged-window replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 xarray slot tagged-window tests");
    test_step.dependOn(&run_tests.step);
}
