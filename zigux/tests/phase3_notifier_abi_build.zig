const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase3-notifier-abi-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-notifier-abi-test",
        "Run the focused Phase 3 notifier ABI replay",
    );
    test_step.dependOn(&run_tests.step);
}