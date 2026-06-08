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
        .imports = &.{
            .{ .name = "err_ptr", .module = err_ptr },
        },
    });

    const xarray_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "err_ptr", .module = err_ptr },
            .{ .name = "xa_value", .module = xa_value },
        },
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_errno_span_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);
    root_module.addImport("xarray_slot_view", xarray_slot_view);

    const replay_tests = b.addTest(.{
        .root_module = root_module,
    });

    const run_replay = b.addRunArtifact(replay_tests);

    const named_step = b.step(
        "phase3-errptr-xarray-errno-span-replay",
        "Run Lane 29 Phase 3 err_ptr/xarray errno span replay",
    );
    named_step.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run Lane 29 Phase 3 err_ptr/xarray errno span replay");
    test_step.dependOn(&run_replay.step);

    b.default_step.dependOn(&run_replay.step);
}
