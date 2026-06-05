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

    const replay_mod = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_lane_payload_crosscheck_replay.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "err_ptr", .module = err_ptr_mod },
            .{ .name = "xa_value", .module = xa_value_mod },
            .{ .name = "xarray_slot_view", .module = xarray_slot_view_mod },
        },
    });
    const replay_tests = b.addTest(.{
        .root_module = replay_mod,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase3-xarray-slot-lane-payload-crosscheck-replay",
        "Run the Phase 3 xarray slot lane payload crosscheck replay",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the Phase 3 xarray slot lane payload crosscheck replay");
    test_step.dependOn(&run_replay_tests.step);
}
