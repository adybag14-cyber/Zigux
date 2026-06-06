const std = @import("std");

fn addHelperTest(
    b: *std.Build,
    name: []const u8,
    path: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
    err_ptr: *std.Build.Module,
    xa_value: ?*std.Build.Module,
) *std.Build.Step.Run {
    const module = b.createModule(.{
        .root_source_file = b.path(path),
        .target = target,
        .optimize = optimize,
    });
    if (!std.mem.eql(u8, name, "err_ptr")) {
        module.addImport("err_ptr", err_ptr);
    }
    if (xa_value) |xa| {
        module.addImport("xa_value", xa);
    }

    const tests = b.addTest(.{ .root_module = module });
    return b.addRunArtifact(tests);
}

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

    const err_ptr_tests = addHelperTest(
        b,
        "err_ptr",
        "../helpers/err_ptr.zig",
        target,
        optimize,
        err_ptr,
        null,
    );
    const xa_value_tests = addHelperTest(
        b,
        "xa_value",
        "../helpers/xa_value.zig",
        target,
        optimize,
        err_ptr,
        null,
    );
    const slot_view_tests = addHelperTest(
        b,
        "xarray_slot_view",
        "../helpers/xarray_slot_view.zig",
        target,
        optimize,
        err_ptr,
        xa_value,
    );

    const trio_step = b.step(
        "phase3-errptr-xarray-helper-trio-test",
        "Run the Phase 3 err_ptr, xa_value, and xarray slot helper tests together",
    );
    trio_step.dependOn(&err_ptr_tests.step);
    trio_step.dependOn(&xa_value_tests.step);
    trio_step.dependOn(&slot_view_tests.step);

    const test_step = b.step("test", "Run the Phase 3 err_ptr/xarray helper trio tests");
    test_step.dependOn(&err_ptr_tests.step);
    test_step.dependOn(&xa_value_tests.step);
    test_step.dependOn(&slot_view_tests.step);

    b.default_step.dependOn(trio_step);
}
