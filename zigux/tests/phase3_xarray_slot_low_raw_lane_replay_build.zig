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
            .root_source_file = b.path("phase3_xarray_slot_low_raw_lane_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "err_ptr", .module = err_ptr },
                .{ .name = "xa_value", .module = xa_value },
                .{ .name = "xarray_slot_view", .module = xarray_slot_view },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const lane_step = b.step("phase3-xarray-slot-low-raw-lane-replay", "Run the Phase 3 xarray low raw lane replay");
    lane_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 xarray low raw lane replay");
    test_step.dependOn(&run_tests.step);
}
