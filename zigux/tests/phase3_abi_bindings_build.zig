const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase3-abi-bindings-test",
        .root_module = abi_bindings_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-abi-bindings-test",
        "Run the focused Phase 3 ABI bindings replay",
    );
    test_step.dependOn(&run_tests.step);
}
