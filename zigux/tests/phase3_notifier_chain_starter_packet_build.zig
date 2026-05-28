const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_chain_view = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_chain_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_chain_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("notifier_chain_view", notifier_chain_view);

    const tests = b.addTest(.{
        .name = "phase3-notifier-chain-starter-packet",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-notifier-chain-starter-packet",
        "Run the shared Phase 3 notifier-chain starter packet",
    );
    step.dependOn(&run.step);
}
