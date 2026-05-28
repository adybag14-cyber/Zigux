const std = @import("std");

fn addPhase3ListHlistStarterPacket(
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

    const unit_tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(unit_tests);
}

fn addPhase3NotifierAbi(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase3-notifier-abi",
        .root_module = root_module,
    });
    return b.addRunArtifact(unit_tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase3_list_hlist_starter_packet = addPhase3ListHlistStarterPacket(b, target, optimize);
    const phase3_notifier_abi = addPhase3NotifierAbi(b, target, optimize);

    const phase3_list_hlist_notifier_step = b.step(
        "phase3-list-hlist-notifier-test",
        "Run the Phase 3 list/hlist starter packet and notifier ABI packet together",
    );
    phase3_list_hlist_notifier_step.dependOn(&phase3_list_hlist_starter_packet.step);
    phase3_list_hlist_notifier_step.dependOn(&phase3_notifier_abi.step);
}
