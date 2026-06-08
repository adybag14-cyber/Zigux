const std = @import("std");

fn addErrPtrXarrayStarter(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);

    const tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addXarraySlotStarter(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);
    root_module.addImport("xarray_slot_view", xarray_slot_view);

    const tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addErrPtrXarrayDump(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);

    const exe = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = root_module,
    });
    return b.addRunArtifact(exe);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const errptr_xarray_starter = addErrPtrXarrayStarter(b, target, optimize);
    const xarray_slot_starter = addXarraySlotStarter(b, target, optimize);
    const errptr_xarray_dump = addErrPtrXarrayDump(b, target, optimize);

    const bundle_step = b.step(
        "phase3-errptr-xarray-bundle",
        "Run the Lane 04 Phase 3 err_ptr/xarray starter, xarray-slot starter, and dump bundle.",
    );
    bundle_step.dependOn(&errptr_xarray_starter.step);
    bundle_step.dependOn(&xarray_slot_starter.step);
    bundle_step.dependOn(&errptr_xarray_dump.step);

    const test_step = b.step(
        "test",
        "Run the Lane 04 Phase 3 err_ptr/xarray bundle tests.",
    );
    test_step.dependOn(bundle_step);

    b.default_step.dependOn(bundle_step);
}
