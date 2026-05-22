const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_chain_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("notifier_abi_bindings", notifier_abi_module);

    const tests = b.addTest(.{
        .name = "phase3-notifier-chain-view-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-notifier-chain-view-test",
        "Run the focused Phase 3 notifier-chain-view replay",
    );
    test_step.dependOn(&run_tests.step);
}
