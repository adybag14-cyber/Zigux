const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_chrdev_window_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);

    const tests = b.addTest(.{
        .name = "phase3-abi-chrdev-window-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase3-abi-chrdev-window-replay",
        "Run the focused Phase 3 ABI chrdev window replay from zigux/tests",
    );
    replay_step.dependOn(&run_tests.step);
}
