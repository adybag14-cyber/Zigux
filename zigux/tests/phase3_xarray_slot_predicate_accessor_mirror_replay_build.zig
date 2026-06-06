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

    const test_mod = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_predicate_accessor_mirror_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_mod.addImport("err_ptr", err_ptr_mod);
    test_mod.addImport("xa_value", xa_value_mod);
    test_mod.addImport("xarray_slot_view", xarray_slot_view_mod);

    const tests = b.addTest(.{
        .root_module = test_mod,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase3-xarray-slot-predicate-accessor-mirror-replay",
        "Run the Phase 3 xarray slot predicate/accessor mirror replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 3 xarray slot predicate/accessor mirror replay tests");
    test_step.dependOn(&run_tests.step);
}
