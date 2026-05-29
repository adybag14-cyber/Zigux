const std = @import("std");

fn addIdrSlotModules(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) struct {
    err_ptr: *std.Build.Module,
    xa_value: *std.Build.Module,
    xarray_slot_view: *std.Build.Module,
    idr_slot_view: *std.Build.Module,
} {
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
    const idr_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/idr_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_view.addImport("xarray_slot_view", xarray_slot_view);
    idr_slot_view.addImport("xa_value", xa_value);

    return .{
        .err_ptr = err_ptr,
        .xa_value = xa_value,
        .xarray_slot_view = xarray_slot_view,
        .idr_slot_view = idr_slot_view,
    };
}

fn addPhase3IdrSlotStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const modules = addIdrSlotModules(b, target, optimize);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", modules.err_ptr);
    root_module.addImport("xa_value", modules.xa_value);
    root_module.addImport("xarray_slot_view", modules.xarray_slot_view);
    root_module.addImport("idr_slot_view", modules.idr_slot_view);

    const tests = b.addTest(.{
        .name = "phase3-idr-slot-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3IdrSlotDump(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const modules = addIdrSlotModules(b, target, optimize);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", modules.err_ptr);
    root_module.addImport("xa_value", modules.xa_value);
    root_module.addImport("idr_slot_view", modules.idr_slot_view);

    const exe = b.addExecutable(.{
        .name = "phase3-idr-slot-dump",
        .root_module = root_module,
    });
    return b.addRunArtifact(exe);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const starter_packet = addPhase3IdrSlotStarterPacket(b, target, optimize);
    const dump = addPhase3IdrSlotDump(b, target, optimize);

    const idr_slot_step = b.step(
        "phase3-idr-slot-standalone",
        "Run the Phase 3 IDR slot starter packet and dump through a standalone Lane 04 shard",
    );
    idr_slot_step.dependOn(&starter_packet.step);
    idr_slot_step.dependOn(&dump.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 IDR slot standalone shard",
    );
    test_step.dependOn(idr_slot_step);
}
