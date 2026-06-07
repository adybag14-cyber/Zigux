const std = @import("std");

fn addListHlistModules(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) struct {
    list_view: *std.Build.Module,
    hlist_view: *std.Build.Module,
} {
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

    return .{
        .list_view = list_view,
        .hlist_view = hlist_view,
    };
}

fn addStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const modules = addListHlistModules(b, target, optimize);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", modules.list_view);
    root_module.addImport("hlist_view", modules.hlist_view);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addDumpPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const modules = addListHlistModules(b, target, optimize);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", modules.list_view);
    root_module.addImport("hlist_view", modules.hlist_view);

    const exe = b.addExecutable(.{
        .name = "phase3-list-hlist-dump",
        .root_module = root_module,
    });
    return b.addRunArtifact(exe);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const run_starter = addStarterPacket(b, target, optimize);
    const run_dump = addDumpPacket(b, target, optimize);

    const bundle_step = b.step(
        "phase3-list-hlist-bundle",
        "Run the Phase 3 list/hlist starter and dump harness packets",
    );
    bundle_step.dependOn(&run_starter.step);
    bundle_step.dependOn(&run_dump.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 list/hlist bundled harness self-check",
    );
    test_step.dependOn(bundle_step);

    b.default_step.dependOn(bundle_step);
}
