const std = @import("std");

fn addPhase3ListHListStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const list_view = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", list_view);
    root_module.addImport("hlist_view", hlist_view);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3NotifierStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_view = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_view.addImport("notifier_abi", notifier_abi);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("notifier_abi", notifier_abi);
    root_module.addImport("notifier_view", notifier_view);

    const tests = b.addTest(.{
        .name = "phase3-notifier-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3IdrSlotStarterPacket(
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

    const idr_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/idr_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_view.addImport("xarray_slot_view", xarray_slot_view);
    idr_slot_view.addImport("xa_value", xa_value);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);
    root_module.addImport("xarray_slot_view", xarray_slot_view);
    root_module.addImport("idr_slot_view", idr_slot_view);

    const tests = b.addTest(.{
        .name = "phase3-idr-slot-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_hlist_tests = addPhase3ListHListStarterPacket(b, target, optimize);
    const notifier_tests = addPhase3NotifierStarterPacket(b, target, optimize);
    const idr_slot_tests = addPhase3IdrSlotStarterPacket(b, target, optimize);

    const combined_step = b.step(
        "phase3-list-hlist-notifier-idr-slot-test",
        "Run the Phase 3 list/hlist, notifier, and IDR-slot starter packets together.",
    );
    combined_step.dependOn(&list_hlist_tests.step);
    combined_step.dependOn(&notifier_tests.step);
    combined_step.dependOn(&idr_slot_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 list/hlist, notifier, and IDR-slot starter-packet harness.",
    );
    test_step.dependOn(combined_step);
}
