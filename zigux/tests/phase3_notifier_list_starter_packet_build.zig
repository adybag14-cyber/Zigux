const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_view = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_list_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("notifier_abi", notifier_abi);
    root_module.addImport("list_view", list_view);

    const tests = b.addTest(.{
        .name = "phase3-notifier-list-starter-packet",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-notifier-list-starter-packet",
        "Run the shared Phase 3 notifier/list starter packet",
    );
    step.dependOn(&run.step);
}
