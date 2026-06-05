const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr = b.addModule("err_ptr", .{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
    });
    const xa_value = b.addModule("xa_value", .{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .imports = &.{
            .{ .name = "err_ptr", .module = err_ptr },
        },
    });
    const xarray_slot_view = b.addModule("xarray_slot_view", .{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .imports = &.{
            .{ .name = "err_ptr", .module = err_ptr },
            .{ .name = "xa_value", .module = xa_value },
        },
    });

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_kind_predicate_table_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("err_ptr", err_ptr);
    test_module.addImport("xa_value", xa_value);
    test_module.addImport("xarray_slot_view", xarray_slot_view);

    const tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase3-xarray-slot-kind-predicate-table-replay",
        "Run the Phase 3 xarray slot kind/predicate table replay.",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 xarray slot kind/predicate table replay.");
    test_step.dependOn(&run_tests.step);
}
