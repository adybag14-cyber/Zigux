const std = @import("std");

fn addPhase3ErrPtrXarrayStarterPacket(
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

fn addPhase3XarraySlotStarterPacket(
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

fn addPhase3ErrPtrXarrayDump(
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
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);
    root_module.addImport("xarray_slot_view", xarray_slot_view);

    const exe = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = root_module,
    });
    return b.addRunArtifact(exe);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase3_errptr_xarray_starter_packet = addPhase3ErrPtrXarrayStarterPacket(
        b,
        target,
        optimize,
    );
    const phase3_xarray_slot_starter_packet = addPhase3XarraySlotStarterPacket(
        b,
        target,
        optimize,
    );
    const phase3_errptr_xarray_dump = addPhase3ErrPtrXarrayDump(b, target, optimize);

    const phase3_errptr_xarray_slot_dump_test = b.step(
        "phase3-errptr-xarray-slot-dump-test",
        "Run the current Lane 29 starter packets and dump together from zigux/tests",
    );
    phase3_errptr_xarray_slot_dump_test.dependOn(&phase3_errptr_xarray_starter_packet.step);
    phase3_errptr_xarray_slot_dump_test.dependOn(&phase3_xarray_slot_starter_packet.step);
    phase3_errptr_xarray_slot_dump_test.dependOn(&phase3_errptr_xarray_dump.step);
}
