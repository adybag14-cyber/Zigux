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

    const slot_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    slot_mod.addImport("err_ptr", err_ptr_mod);
    slot_mod.addImport("xa_value", xa_value_mod);

    const test_mod = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_error_ordering_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_mod.addImport("err_ptr", err_ptr_mod);
    test_mod.addImport("xarray_slot_view", slot_mod);

    const tests = b.addTest(.{ .root_module = test_mod });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "phase3-xarray-slot-error-ordering-replay",
        "Run the Lane 29 xarray slot error-ordering replay",
    );
    test_step.dependOn(&run_tests.step);

    const alias_step = b.step("test", "Run the Lane 29 xarray slot error-ordering replay");
    alias_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
