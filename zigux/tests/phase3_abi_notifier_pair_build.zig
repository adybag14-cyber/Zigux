const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_notifier_pair_abi_tests",
        .root_module = abi_bindings,
    });
    const notifier_tests = b.addTest(.{
        .name = "phase3_abi_notifier_pair_notifier_tests",
        .root_module = notifier_abi,
    });

    const abi_run = b.addRunArtifact(abi_tests);
    const notifier_run = b.addRunArtifact(notifier_tests);

    const pair_step = b.step(
        "phase3-abi-notifier-pair-test",
        "Run the focused Phase 3 ABI bindings and notifier ABI pair replay.",
    );
    pair_step.dependOn(&abi_run.step);
    pair_step.dependOn(&notifier_run.step);
}
